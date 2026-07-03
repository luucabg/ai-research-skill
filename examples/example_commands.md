# Example Commands

## Automatic AI tool mode

This is the intended workflow.

Start the MCP server:

```bash
ai-research-mcp
```

Then connect it from an MCP-compatible AI client.

Once connected, ask the AI normally:

```text
What is the best Philips beard trimmer under €70?
```

The AI should call `youtube_research`, read the returned transcripts/comments/source context, and answer directly.

The user does not need to open transcript folders or paste Markdown files.

## Manual mode: save a report

```bash
ai-research youtube "best Philips beard trimmer" --max-videos 5 --comments 50 --out outputs/philips-trimmer.md
```

## Manual mode: print a report to the terminal

```bash
ai-research youtube-print "best Philips beard trimmer" --max-videos 3 --comments 20
```

## Search YouTube only

```bash
ai-research search-youtube "best Philips beard trimmer" --max-results 10
```

## Extract one transcript

```bash
ai-research transcript "https://www.youtube.com/watch?v=VIDEO_ID" --out outputs/transcript.txt
```

## Extract comments

```bash
ai-research comments "https://www.youtube.com/watch?v=VIDEO_ID" --max-comments 100
```

## Check full automatic setup

```bash
ai-research doctor
```

If the installer completed successfully, MCP mode can use local audio transcription automatically when transcripts/subtitles are missing.

Manual test with audio fallback enabled:

```bash
ai-research youtube "best budget microphone" --max-videos 3 --audio-fallback --out outputs/microphone.md
```
