from __future__ import annotations

import json
import tempfile
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi

from .models import Comment, TranscriptResult, TranscriptSegment, VideoResearchItem, VideoResult
from .utils import clean_text, extract_youtube_id, run_command, safe_json, vtt_to_text, write_text, youtube_url

DEFAULT_LANGUAGES = ["en", "en-US", "en-GB", "es", "es-ES"]


def search_youtube(query: str, max_results: int = 5) -> list[VideoResult]:
    """Search YouTube using yt-dlp's ytsearch without a YouTube API key."""
    max_results = max(1, min(max_results, 25))
    output = run_command(
        [
            "yt-dlp",
            "--dump-json",
            "--flat-playlist",
            "--no-warnings",
            f"ytsearch{max_results}:{query}",
        ],
        timeout=120,
    )

    results: list[VideoResult] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        video_id = data.get("id") or extract_youtube_id(data.get("url", ""))
        url = data.get("url") or youtube_url(video_id)
        if not url.startswith("http"):
            url = youtube_url(video_id)
        results.append(
            VideoResult(
                id=video_id,
                title=data.get("title") or "",
                url=url,
                channel=data.get("channel") or data.get("uploader") or "",
                duration=data.get("duration"),
                view_count=data.get("view_count"),
                upload_date=data.get("upload_date"),
                description=data.get("description") or "",
            )
        )
    return results


def transcript_from_api(url_or_id: str, languages: list[str] | None = None) -> TranscriptResult:
    video_id = extract_youtube_id(url_or_id)
    languages = languages or DEFAULT_LANGUAGES

    try:
        raw_segments = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
    except AttributeError:
        # Compatibility with newer object-based API variants.
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id, languages=languages)
        raw_segments = []
        for item in fetched:
            raw_segments.append(
                {
                    "text": getattr(item, "text", ""),
                    "start": getattr(item, "start", None),
                    "duration": getattr(item, "duration", None),
                }
            )

    segments = [
        TranscriptSegment(
            text=clean_text(seg.get("text", "")),
            start=seg.get("start"),
            duration=seg.get("duration"),
        )
        for seg in raw_segments
        if clean_text(seg.get("text", ""))
    ]
    text = " ".join(seg.text for seg in segments)
    return TranscriptResult(
        video_id=video_id,
        url=youtube_url(video_id),
        source="youtube-transcript-api",
        language=None,
        text=text,
        segments=segments,
    )


def transcript_from_ytdlp_subs(url_or_id: str, languages: list[str] | None = None) -> TranscriptResult:
    video_id = extract_youtube_id(url_or_id)
    url = youtube_url(video_id)
    languages = languages or DEFAULT_LANGUAGES
    sub_langs = ",".join(languages + ["es.*", "en.*"])

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        run_command(
            [
                "yt-dlp",
                "--skip-download",
                "--write-auto-subs",
                "--write-subs",
                "--sub-format",
                "vtt",
                "--sub-langs",
                sub_langs,
                "--output",
                "%(id)s.%(ext)s",
                url,
            ],
            cwd=tmp_path,
            timeout=180,
        )
        vtt_files = sorted(tmp_path.glob("*.vtt"))
        if not vtt_files:
            raise RuntimeError("No VTT subtitles were found with yt-dlp.")
        # Prefer English, then Spanish, then anything.
        preferred = sorted(
            vtt_files,
            key=lambda p: (
                0 if ".en" in p.name else 1 if ".es" in p.name else 2,
                len(p.name),
            ),
        )[0]
        text = vtt_to_text(preferred.read_text(encoding="utf-8", errors="replace"))
        if not text:
            raise RuntimeError("The subtitles were empty or could not be cleaned.")
        return TranscriptResult(
            video_id=video_id,
            url=url,
            source=f"yt-dlp-subtitles:{preferred.name}",
            language=None,
            text=text,
            segments=[],
        )


def download_audio(url_or_id: str, output_dir: str | Path) -> Path:
    video_id = extract_youtube_id(url_or_id)
    url = youtube_url(video_id)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_command(
        [
            "yt-dlp",
            "-f",
            "bestaudio/best",
            "-x",
            "--audio-format",
            "mp3",
            "--output",
            f"{video_id}.%(ext)s",
            url,
        ],
        cwd=out_dir,
        timeout=900,
    )
    matches = list(out_dir.glob(f"{video_id}.*"))
    if not matches:
        raise RuntimeError("Could not download the audio.")
    return matches[0]


def transcript_from_local_whisper(url_or_id: str, model_size: str = "small") -> TranscriptResult:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "faster-whisper is not installed. Install it with: pip install -e '.[local-transcribe]'"
        ) from exc

    video_id = extract_youtube_id(url_or_id)
    with tempfile.TemporaryDirectory() as tmp:
        audio_path = download_audio(video_id, tmp)
        model = WhisperModel(model_size, device="auto", compute_type="auto")
        segments_iter, info = model.transcribe(str(audio_path), vad_filter=True)
        segments: list[TranscriptSegment] = []
        for seg in segments_iter:
            text = clean_text(seg.text)
            if text:
                segments.append(
                    TranscriptSegment(
                        text=text,
                        start=float(seg.start),
                        duration=float(seg.end - seg.start),
                    )
                )
        text = " ".join(seg.text for seg in segments)
        return TranscriptResult(
            video_id=video_id,
            url=youtube_url(video_id),
            source=f"faster-whisper:{model_size}",
            language=getattr(info, "language", None),
            text=text,
            segments=segments,
        )


def get_best_transcript(
    url_or_id: str,
    languages: list[str] | None = None,
    audio_fallback: bool = False,
    whisper_model: str = "small",
) -> TranscriptResult:
    errors: list[str] = []
    for fn in (transcript_from_api, transcript_from_ytdlp_subs):
        try:
            return fn(url_or_id, languages=languages)
        except Exception as exc:  # noqa: BLE001 - useful for fallback chain
            errors.append(f"{fn.__name__}: {exc}")

    if audio_fallback:
        try:
            return transcript_from_local_whisper(url_or_id, model_size=whisper_model)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"transcript_from_local_whisper: {exc}")

    raise RuntimeError("Could not extract a transcript. " + " | ".join(errors))


def get_comments(url_or_id: str, max_comments: int = 100) -> list[Comment]:
    """Try to fetch comments through yt-dlp. This can be slow or unavailable for some videos."""
    video_id = extract_youtube_id(url_or_id)
    url = youtube_url(video_id)
    max_comments = max(0, min(max_comments, 1000))
    if max_comments == 0:
        return []

    output = run_command(
        [
            "yt-dlp",
            "--skip-download",
            "--write-comments",
            "--dump-single-json",
            "--no-warnings",
            url,
        ],
        timeout=240,
    )
    data = json.loads(output)
    raw_comments = data.get("comments") or []
    comments: list[Comment] = []
    for item in raw_comments[:max_comments]:
        text = clean_text(item.get("text") or item.get("html") or "")
        if not text:
            continue
        comments.append(
            Comment(
                text=text,
                author=item.get("author"),
                like_count=item.get("like_count"),
                timestamp=str(item.get("timestamp")) if item.get("timestamp") else None,
            )
        )
    return comments


def research_youtube_topic(
    query: str,
    max_videos: int = 5,
    comments: int = 0,
    audio_fallback: bool = False,
    whisper_model: str = "small",
) -> list[VideoResearchItem]:
    videos = search_youtube(query, max_results=max_videos)
    items: list[VideoResearchItem] = []

    for video in videos:
        transcript = None
        transcript_error = None
        video_comments: list[Comment] = []
        comments_error = None

        try:
            transcript = get_best_transcript(
                video.url,
                audio_fallback=audio_fallback,
                whisper_model=whisper_model,
            )
        except Exception as exc:  # noqa: BLE001
            transcript_error = str(exc)

        if comments > 0:
            try:
                video_comments = get_comments(video.url, max_comments=comments)
            except Exception as exc:  # noqa: BLE001
                comments_error = str(exc)

        items.append(
            VideoResearchItem(
                video=video,
                transcript=transcript,
                transcript_error=transcript_error,
                comments=video_comments,
                comments_error=comments_error,
            )
        )

    return items


def render_markdown_report(query: str, items: list[VideoResearchItem]) -> str:
    parts: list[str] = []
    parts.append(f"# AI Research Report: {query}\n")
    parts.append("This report contains automatically extracted sources. Verify important claims.\n")

    for idx, item in enumerate(items, start=1):
        video = item.video
        parts.append(f"\n## {idx}. {video.title or video.id}\n")
        parts.append(f"- URL: {video.url}\n")
        if video.channel:
            parts.append(f"- Channel: {video.channel}\n")
        if video.duration:
            parts.append(f"- Duration: {video.duration} seconds\n")
        if video.view_count:
            parts.append(f"- Views: {video.view_count}\n")

        parts.append("\n### Transcript\n")
        if item.transcript:
            text = item.transcript.text.strip()
            if len(text) > 18000:
                text = text[:18000] + "\n\n[TRUNCATED: transcript too long]\n"
            parts.append(text + "\n")
            parts.append(f"\n_Transcript source: {item.transcript.source}_\n")
        else:
            parts.append(f"Not available. Error: {item.transcript_error}\n")

        if item.comments or item.comments_error:
            parts.append("\n### Extracted comments\n")
            if item.comments:
                for c_idx, comment in enumerate(item.comments, start=1):
                    prefix = f"{c_idx}."
                    likes = f" ({comment.like_count} likes)" if comment.like_count is not None else ""
                    author = f"{comment.author}: " if comment.author else ""
                    parts.append(f"{prefix} {author}{comment.text}{likes}\n")
            else:
                parts.append(f"Not available. Error: {item.comments_error}\n")

    return "".join(parts).strip() + "\n"


def save_research_report(
    query: str,
    out: str | Path,
    max_videos: int = 5,
    comments: int = 0,
    audio_fallback: bool = False,
    whisper_model: str = "small",
) -> Path:
    items = research_youtube_topic(
        query=query,
        max_videos=max_videos,
        comments=comments,
        audio_fallback=audio_fallback,
        whisper_model=whisper_model,
    )
    return write_text(out, render_markdown_report(query, items))


def research_as_json(query: str, max_videos: int = 5, comments: int = 0) -> str:
    items = research_youtube_topic(query=query, max_videos=max_videos, comments=comments)
    return safe_json([item.model_dump() for item in items])
