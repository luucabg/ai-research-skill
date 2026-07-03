from __future__ import annotations

import html
import json
import re
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

YOUTUBE_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{11}$")


def run_command(args: list[str], cwd: str | Path | None = None, timeout: int = 120) -> str:
    proc = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    if proc.returncode != 0:
        stderr = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(stderr[:2000])
    return proc.stdout


def extract_youtube_id(url_or_id: str) -> str:
    value = url_or_id.strip()
    if YOUTUBE_ID_RE.match(value):
        return value

    parsed = urlparse(value)
    host = parsed.netloc.lower().replace("www.", "")

    if host in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
        qs = parse_qs(parsed.query)
        if "v" in qs and qs["v"]:
            return qs["v"][0]
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) >= 2 and parts[0] in {"shorts", "embed", "live"}:
            return parts[1]

    if host == "youtu.be":
        parts = [p for p in parsed.path.split("/") if p]
        if parts:
            return parts[0]

    raise ValueError(f"This does not look like a valid YouTube URL/ID: {url_or_id}")


def youtube_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def clean_text(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def vtt_to_text(vtt: str) -> str:
    lines: list[str] = []
    seen_recent: set[str] = set()

    for raw in vtt.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line == "WEBVTT" or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if "-->" in line:
            continue
        if line.startswith("NOTE"):
            continue
        if re.fullmatch(r"\d+", line):
            continue
        line = clean_text(line)
        if not line:
            continue
        # YouTube auto-captions often duplicate nearby lines.
        normalized = line.lower()
        if normalized in seen_recent:
            continue
        lines.append(line)
        seen_recent.add(normalized)
        if len(seen_recent) > 50:
            seen_recent = set(list(seen_recent)[-25:])

    return " ".join(lines).strip()


def safe_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def write_text(path: str | Path, text: str) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p
