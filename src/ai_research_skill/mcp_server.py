from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .youtube import (
    get_best_transcript,
    get_comments,
    render_markdown_report,
    research_youtube_topic,
    search_youtube,
)
from .utils import safe_json

mcp = FastMCP("ai-research-skill")


@mcp.tool()
def youtube_search(query: str, max_results: int = 5) -> str:
    """Search YouTube videos without an API key using yt-dlp."""
    videos = search_youtube(query, max_results=max_results)
    return safe_json([video.model_dump() for video in videos])


@mcp.tool()
def youtube_transcript(url_or_id: str, audio_fallback: bool = True) -> str:
    """Extract the best available transcript from a YouTube video."""
    transcript = get_best_transcript(url_or_id, audio_fallback=audio_fallback)
    return safe_json(transcript.model_dump())


@mcp.tool()
def youtube_comments(url_or_id: str, max_comments: int = 100) -> str:
    """Try to extract comments from a YouTube video. This can be slow."""
    comments = get_comments(url_or_id, max_comments=max_comments)
    return safe_json([comment.model_dump() for comment in comments])


@mcp.tool()
def youtube_research(
    query: str,
    max_videos: int = 5,
    comments_per_video: int = 0,
    audio_fallback: bool = True,
) -> str:
    """
    Search YouTube, extract transcripts/comments, and return a Markdown research context.

    Intended AI behavior: call this tool, read the returned context, compare the
    sources, and answer the user directly. Do not ask the user to open transcript
    folders or manually paste files. This tool does not save a final report in
    MCP mode; temporary subtitle/audio files are deleted by the extractor. Audio fallback is enabled by default in MCP mode, so missing subtitles can be handled automatically when the full installer has been used.
    """
    items = research_youtube_topic(
        query=query,
        max_videos=max_videos,
        comments=comments_per_video,
        audio_fallback=audio_fallback,
    )
    return render_markdown_report(query, items)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
