from __future__ import annotations

from pathlib import Path
import importlib.util
import shutil
import sys

import typer
from rich.console import Console
from rich.table import Table

from .youtube import (
    get_best_transcript,
    get_comments,
    render_markdown_report,
    research_youtube_topic,
    save_research_report,
    search_youtube,
)

app = typer.Typer(help="AI Research Skill CLI. Manual mode saves/prints reports; MCP mode returns research directly to the AI.")
console = Console()


@app.command("doctor")
def doctor_cmd() -> None:
    """Check whether the local environment is ready for automatic research."""
    table = Table(title="AI Research Skill environment check")
    table.add_column("Dependency")
    table.add_column("Status")
    table.add_column("Why it matters")

    checks = [
        ("Python", sys.executable, "Runs the local tool server and CLI."),
        ("yt-dlp", shutil.which("yt-dlp"), "Searches YouTube, downloads subtitles/audio, and extracts comments."),
        ("FFmpeg", shutil.which("ffmpeg"), "Required for audio download/conversion and local transcription fallback."),
        (
            "faster-whisper",
            "installed" if importlib.util.find_spec("faster_whisper") else None,
            "Transcribes audio locally when transcripts/subtitles are missing.",
        ),
    ]

    all_ok = True
    for name, value, reason in checks:
        ok = bool(value)
        all_ok = all_ok and ok
        status = "[green]OK[/green]" if ok else "[red]Missing[/red]"
        if value and name in {"Python", "yt-dlp", "FFmpeg"}:
            status += f"\n{value}"
        table.add_row(name, status, reason)

    console.print(table)
    if all_ok:
        console.print("[green]Full automatic mode is ready.[/green]")
    else:
        console.print(
            "[yellow]Some pieces are missing. Run scripts/install_windows.ps1 on Windows, "
            "or scripts/install_macos_linux.sh on macOS/Linux.[/yellow]"
        )


@app.command("search-youtube")
def search_youtube_cmd(
    query: str = typer.Argument(..., help="Topic to search on YouTube"),
    max_results: int = typer.Option(5, "--max-results", "-n"),
) -> None:
    videos = search_youtube(query, max_results=max_results)
    table = Table(title=f"YouTube search: {query}")
    table.add_column("#")
    table.add_column("Title")
    table.add_column("Channel")
    table.add_column("URL")
    for i, video in enumerate(videos, start=1):
        table.add_row(str(i), video.title, video.channel, video.url)
    console.print(table)


@app.command("transcript")
def transcript_cmd(
    url_or_id: str = typer.Argument(..., help="YouTube URL or ID"),
    out: Path | None = typer.Option(None, "--out", "-o"),
    audio_fallback: bool = typer.Option(False, "--audio-fallback"),
    whisper_model: str = typer.Option("small", "--whisper-model"),
) -> None:
    result = get_best_transcript(
        url_or_id,
        audio_fallback=audio_fallback,
        whisper_model=whisper_model,
    )
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result.text, encoding="utf-8")
        console.print(f"Saved to [bold]{out}[/bold]")
    else:
        console.print(result.text)


@app.command("comments")
def comments_cmd(
    url_or_id: str = typer.Argument(..., help="YouTube URL or ID"),
    max_comments: int = typer.Option(100, "--max-comments", "-n"),
) -> None:
    comments = get_comments(url_or_id, max_comments=max_comments)
    for i, comment in enumerate(comments, start=1):
        likes = f" [{comment.like_count} likes]" if comment.like_count is not None else ""
        console.print(f"[bold]{i}.[/bold] {comment.text}{likes}")


@app.command("youtube")
def youtube_research_cmd(
    query: str = typer.Argument(..., help="Topic to research"),
    max_videos: int = typer.Option(5, "--max-videos", "-n"),
    comments: int = typer.Option(0, "--comments", help="Comments per video. 0 = disabled"),
    out: Path = typer.Option(Path("outputs/report.md"), "--out", "-o"),
    audio_fallback: bool = typer.Option(False, "--audio-fallback"),
    whisper_model: str = typer.Option("small", "--whisper-model"),
) -> None:
    console.print(f"Researching: [bold]{query}[/bold]")
    path = save_research_report(
        query=query,
        out=out,
        max_videos=max_videos,
        comments=comments,
        audio_fallback=audio_fallback,
        whisper_model=whisper_model,
    )
    console.print(f"Report saved to [bold]{path}[/bold]")


@app.command("youtube-print")
def youtube_research_print_cmd(
    query: str = typer.Argument(..., help="Topic to research"),
    max_videos: int = typer.Option(3, "--max-videos", "-n"),
    comments: int = typer.Option(0, "--comments"),
) -> None:
    items = research_youtube_topic(query=query, max_videos=max_videos, comments=comments)
    console.print(render_markdown_report(query, items))
