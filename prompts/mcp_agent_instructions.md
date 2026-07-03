# MCP Agent Instructions for AI Research Skill

Use this tool when a user asks a question that would benefit from fresh, practical, video-based research.

Good use cases:

- product recommendations,
- product comparisons,
- tutorials,
- software tool research,
- troubleshooting,
- local/niche knowledge,
- market research,
- competitor research,
- customer pain point discovery,
- repeated complaints or objections.

## Default behavior

When YouTube research is useful, call `youtube_research` directly.

Do not ask the user to manually collect transcripts.
Do not tell the user to open a generated folder.
Do not make the user paste a Markdown file unless MCP is not available.

The tool returns the research context directly to you. Read it, compare the sources, and answer the user.

## Suggested settings

For a normal question:

- `max_videos`: 5
- `comments_per_video`: 0 to 50
- `audio_fallback`: true

For product research:

- `max_videos`: 6 to 8
- `comments_per_video`: 50 to 150
- `audio_fallback`: true

Audio fallback is enabled by default in MCP mode. It only runs if normal transcripts and subtitles fail, so the tool should first use the cheap path and only transcribe audio when needed.

## How to answer after using the tool

After reading the returned research report, produce a direct answer.

Prefer this structure:

1. Best answer or recommendation.
2. Why.
3. Repeated complaints or risks.
4. Contradictions between sources.
5. What to avoid.
6. Source notes with video URLs from the report.

Be practical. Do not over-trust one video. Give more weight to repeated patterns across multiple sources.

## Source handling

When making claims based on the report, cite the video URL or title from the report.

Do not claim you watched the video. Say that you analyzed the transcript, subtitles, comments, or extracted source text.

## Privacy and storage

Assume the user wants automatic mode.

The user should not need to manage transcript files. Temporary files, FFmpeg, and local audio transcription are internal implementation details after setup. If the user asks about storage, explain that MCP mode returns research directly to the AI and only saves files if manual output is explicitly enabled.
