# AI Research Skill

## Purpose

Use this skill when a user asks for research that may benefit from information hidden in YouTube videos, transcripts, subtitles, demos, reviews, podcasts, tutorials, or comment sections.

The goal is to give the user a direct, practical answer, not to make them manually open transcript folders or paste files back into the assistant.

## Core behavior

When the user asks a research question, the assistant should:

1. Decide whether YouTube/video research would add useful information.
2. If useful, call the available research tool, preferably `youtube_research`.
3. Read the returned research context.
4. Compare repeated claims, recommendations, complaints, contradictions, and examples across sources.
5. Answer the user directly with a clear conclusion.
6. Mention the main evidence from the returned sources when relevant.

The assistant should not tell the user to manually inspect temporary folders, raw subtitle files, or downloaded audio.

## Preferred tool

Use:

```text
youtube_research(query, max_videos, comments_per_video, audio_fallback)
```

Recommended defaults:

```text
max_videos = 5 to 8
comments_per_video = 0 for factual research
comments_per_video = 50 to 150 for product research, complaints, market research, or user sentiment
audio_fallback = true
```

## When to use comments

Use comments when the user is asking about:

- product quality,
- real user complaints,
- buying decisions,
- customer pain points,
- repeated objections,
- market research,
- software bugs,
- scams or suspicious tools,
- sentiment around a creator, product, or service.

Do not treat comments as reliable factual proof. Treat them as anecdotal signals and look for repeated patterns.

## When not to use this skill

Do not use this skill when:

- the answer is simple and does not need video research,
- the user only wants a rewrite, translation, or short explanation,
- the topic requires official/legal/medical/financial sources and YouTube would be weak evidence,
- the user explicitly says not to browse or research externally.

## Answer style

The final answer should be practical and decision-oriented.

For product or recommendation research, prefer this structure:

1. Best choice.
2. Why it is the best choice.
3. Main alternatives.
4. Repeated complaints or risks.
5. What to avoid.
6. Confidence level based on source agreement.

For general research, prefer:

1. Direct answer.
2. Key evidence or patterns.
3. Contradictions or uncertainty.
4. Practical conclusion.

## Source handling

The returned research context may include video titles, URLs, transcript excerpts, transcript source, and comments.

The assistant should:

- prefer repeated claims across multiple sources,
- separate creator claims from user comments,
- be clear when evidence is weak,
- avoid pretending that comments prove factual truth,
- avoid overfitting to a single video.

## Temporary files and storage

In automatic tool mode, research should be returned directly to the assistant.

Temporary files created for subtitles, audio extraction, or transcription should be treated as internal implementation details and should be deleted automatically by the tool when possible.

A final Markdown report should only be saved when the user or CLI explicitly requests it.

## Manual fallback

If the assistant cannot call the tool directly, tell the user to run the CLI command and paste/upload the generated Markdown report.

Example:

```bash
ai-research youtube "best Philips beard trimmer under 70 euros" --max-videos 6 --comments 75 --audio-fallback --out research.md
```

Then the assistant can analyze the report manually.
