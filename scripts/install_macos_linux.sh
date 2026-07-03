#!/usr/bin/env bash
set -euo pipefail

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

echo "Installing AI Research Skill with full local transcription support..."

if ! command_exists python3; then
  echo "Python 3 was not found. Install Python 3.11+ first, then run this script again." >&2
  exit 1
fi

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[local-transcribe]"

echo "Checking FFmpeg..."
if ! command_exists ffmpeg; then
  echo "FFmpeg was not found. Trying to install it automatically..."
  if command_exists brew; then
    brew install ffmpeg
  elif command_exists apt-get; then
    sudo apt-get update
    sudo apt-get install -y ffmpeg
  elif command_exists dnf; then
    sudo dnf install -y ffmpeg
  elif command_exists pacman; then
    sudo pacman -S --noconfirm ffmpeg
  else
    echo "Could not install FFmpeg automatically. Install it with your system package manager." >&2
  fi
fi

echo ""
echo "Running environment check..."
ai-research doctor

echo ""
echo "Installed. Test manual mode with:"
echo "ai-research youtube 'best Philips beard trimmer' --max-videos 3 --comments 30 --audio-fallback --out examples/report.md"
echo ""
echo "For automatic AI mode, connect the MCP server using:"
echo "ai-research-mcp"
