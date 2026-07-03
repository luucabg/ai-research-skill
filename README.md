# AI Research Skill

Most AI answers are limited by what the assistant can already see.

But a lot of useful, practical information is not sitting in clean blog posts or documentation. It is buried inside YouTube videos, subtitles, product reviews, tutorials, podcasts, demos, and comment sections.

**AI Research Skill lets an AI assistant pull that hidden information automatically before it answers.**

The intended experience is simple:

```text
User: What is the best Philips beard trimmer under €70?
↓
The AI calls this tool.
↓
The tool searches YouTube, extracts transcripts, optional comments, and useful source text.
↓
The AI reads that context, compares the sources, and gives a practical answer.
```

The user should not need to open transcript folders, copy files, or manually feed research back into the AI.

## What this is

This is a local research tool for AI assistants and coding agents.

It can be used in two ways:

1. **Automatic AI tool mode**: the AI calls the tool through MCP and uses the returned research context directly.
2. **Manual mode**: you run the command yourself and generate a Markdown research report that can be pasted or uploaded into any AI assistant.

The main goal is **automatic AI tool mode**. Manual mode exists as a fallback because it works everywhere.


## Is this a Skill or an MCP tool?

Both, but they are not the same thing.

- `SKILL.md` tells an AI agent **how to behave** when doing this kind of research.
- The MCP server gives the AI agent **tools it can actually call**, such as `youtube_research`, `youtube_transcript`, and `youtube_comments`.

The best setup is to use both: the skill instructions guide the assistant, and MCP lets the assistant automatically search YouTube, extract transcripts, use audio fallback, read comments, and return a final answer without making the user manage files manually.

## Why this exists

Normal AI research often misses information from:

- YouTube reviews,
- long tutorials,
- product comparisons,
- podcasts,
- demos,
- real user complaints,
- niche communities,
- and comment sections.

Those sources often contain the most useful practical details: what breaks, what people regret buying, what actually works, and what repeated complaints appear across different videos.

This tool turns that information into clean text an AI can use.

## What it does, in plain English

When the AI or user gives it a topic, for example:

```text
best Philips beard trimmer
```

The tool can:

- search YouTube for relevant videos,
- pick a limited number of results,
- extract transcripts when available,
- fall back to YouTube subtitles when needed,
- optionally extract comments,
- optionally download audio and transcribe it locally with Whisper,
- return a clean research report directly to the AI,
- optionally save the report as a `.md` file for debugging or manual use.

In automatic mode, the research is returned to the AI during the conversation. The AI can then compare the sources and answer directly.

## Automatic mode: the intended flow

With an MCP-compatible client, the assistant can use this project as a tool.

Example user question:

```text
What is the best Philips beard trimmer under €70?
```

The assistant can call:

```text
youtube_research(query="best Philips beard trimmer under 70 euros", max_videos=6, comments_per_video=50, audio_fallback=True)
```

In MCP mode, `audio_fallback` is enabled by default. The tool first tries transcripts and subtitles. It only downloads/transcribes audio if those easier methods fail.

The tool returns a clean research context containing video titles, URLs, transcript text, transcript source, and optionally selected comments.

Then the AI answers something like:

```text
Based on the repeated points across the videos, I would buy X because...
The main complaints are...
Avoid Y if...
```

No transcript folder needs to be opened by the user.

## Does it save files?

In MCP mode, the tool returns the research text directly to the AI.

By default:

- transcripts are kept in memory,
- comments are kept in memory,
- temporary subtitle/audio files are created only when needed,
- temporary files are deleted automatically,
- no final report is saved unless you explicitly run the CLI with `--out` or add your own storage layer.

Manual mode saves a `.md` file because that is the point of manual mode.

## Who this is for

This is useful if you want an AI to research:

- products before buying,
- software tools,
- business niches,
- customer pain points,
- competitors,
- tutorials,
- technical problems,
- local markets,
- AI tools,
- or any topic where YouTube has better information than normal search results.

You do not need to be an advanced developer to use the basic version. You need Python and the command line. MCP setup is more technical, but once connected, the user experience is simple.

## What it includes

- YouTube search using `yt-dlp`, no YouTube API key required.
- Transcript extraction using `youtube-transcript-api`.
- Subtitle fallback using `yt-dlp`.
- Automatic local audio transcription fallback using `faster-whisper` when full setup is installed.
- Optional comment extraction using `yt-dlp`.
- A command-line interface.
- An MCP server for AI clients that support MCP.
- Prompts for manual and MCP-based usage.

## What it does not do

Important limitations:

- It does not bypass private content.
- It does not log into user accounts.
- It does not guarantee every video has subtitles.
- It does not guarantee comments are available.
- It does not reliably scrape every social media platform.
- It does not replace human judgment.

TikTok, Instagram, X/Twitter, and Facebook are not included in this first version because free and reliable access is much more fragile. YouTube is the best starting point because transcripts, subtitles, comments, and audio extraction are more realistic to automate.

## Quick install

The recommended installer sets up the full automatic workflow: Python environment, YouTube extraction, local Whisper transcription, and FFmpeg for audio handling.

### Windows PowerShell

```powershell
cd ai-research-skill
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\install_windows.ps1
```

The script will:

- create a local virtual environment,
- install the project,
- install local transcription support with `faster-whisper`,
- check for FFmpeg,
- try to install FFmpeg automatically using `winget`, Chocolatey, or Scoop,
- run `ai-research doctor` to verify the setup.

### macOS/Linux

```bash
cd ai-research-skill
chmod +x scripts/install_macos_linux.sh
./scripts/install_macos_linux.sh
```

After setup, the AI can use audio fallback automatically through MCP. The user should not need to manually install FFmpeg, download audio, or manage transcript folders.

Check the environment any time with:

```bash
ai-research doctor
```

## MCP usage

Start the MCP server:

```bash
ai-research-mcp
```

Example MCP config:

```json
{
  "mcpServers": {
    "ai-research-skill": {
      "command": "ai-research-mcp"
    }
  }
}
```

If your client cannot find the command, use the full path to the virtual environment Python:

```json
{
  "mcpServers": {
    "ai-research-skill": {
      "command": "C:\\path\\to\\ai-research-skill\\.venv\\Scripts\\python.exe",
      "args": ["-m", "ai_research_skill.mcp_server"]
    }
  }
}
```

Different AI clients have different MCP setup screens. The important part is that the client must be able to launch or connect to this MCP server.

## Available MCP tools

- `youtube_search`: searches YouTube videos.
- `youtube_transcript`: extracts a video transcript when possible.
- `youtube_comments`: extracts video comments when possible.
- `youtube_research`: searches multiple videos, extracts transcripts/comments, falls back to local audio transcription when enabled, and returns a Markdown research context directly to the AI.

## Recommended AI behavior

When connected as a tool, the AI should:

1. Decide whether YouTube research would improve the answer.
2. Call `youtube_research` with a focused query.
3. Read the returned research context.
4. Compare repeated claims, recommendations, complaints, and contradictions.
5. Answer the user directly.
6. Cite video URLs from the research report when making source-based claims.
7. Avoid telling the user to manually open transcript files unless manual mode is being used.

See:

```text
prompts/mcp_agent_instructions.md
```

## Manual mode

Manual mode is still useful when your AI client cannot call MCP tools.

Run:

```bash
ai-research youtube "best Philips beard trimmer" --max-videos 5 --comments 50 --out examples/report.md
```

Then open:

```text
examples/report.md
```

Paste or upload that report into your preferred AI assistant together with:

```text
prompts/research_skill_prompt.md
```

This is less smooth, but it works almost everywhere because the output is just text.

## Example workflow

Automatic mode:

```text
User: What is the best cheap beard trimmer from Philips, Braun, or Remington?
AI: calls youtube_research(...)
Tool: returns transcripts/comments/source context
AI: compares the information and answers directly
```

Manual mode:

```bash
ai-research youtube "best cheap beard trimmer Philips Braun Remington" --max-videos 8 --comments 100 --out beard-trimmer-research.md
```

Then ask an AI:

```text
Use this research report. Tell me which product is actually the best value, what users complain about, and which one you would buy.
```

## Recommended roadmap

Start simple. Do not try to support every platform immediately.

Best order:

1. YouTube transcripts.
2. YouTube comments.
3. Normal web search with SearXNG.
4. Reddit.
5. Local Whisper transcription.
6. TikTok/Instagram/X only if there is a clear reason.
