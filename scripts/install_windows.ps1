$ErrorActionPreference = "Stop"

function Test-CommandExists {
    param([string]$Command)
    return [bool](Get-Command $Command -ErrorAction SilentlyContinue)
}

function Refresh-Path {
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machinePath;$userPath"
}

Write-Host "Installing AI Research Skill with full local transcription support..."

if (-not (Test-CommandExists "python")) {
    throw "Python was not found. Install Python 3.11+ first, then run this script again."
}

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

# Install the project and the local transcription extra.
# This installs faster-whisper so the tool can transcribe audio locally when transcripts/subtitles are missing.
pip install -e ".[local-transcribe]"

Write-Host "Checking FFmpeg..."

if (-not (Test-CommandExists "ffmpeg")) {
    Write-Host "FFmpeg was not found. Trying to install it automatically..."

    if (Test-CommandExists "winget") {
        winget install --id Gyan.FFmpeg -e --source winget --accept-package-agreements --accept-source-agreements
    }
    elseif (Test-CommandExists "choco") {
        choco install ffmpeg -y
    }
    elseif (Test-CommandExists "scoop") {
        scoop install ffmpeg
    }
    else {
        Write-Warning "Could not find winget, Chocolatey, or Scoop. Install FFmpeg manually or install winget from Microsoft Store."
    }

    Refresh-Path
}

Write-Host ""
Write-Host "Running environment check..."
ai-research doctor

Write-Host ""
Write-Host "Installed. Test manual mode with:"
Write-Host "ai-research youtube 'best Philips beard trimmer' --max-videos 3 --comments 30 --audio-fallback --out examples/report.md"
Write-Host ""
Write-Host "For automatic AI mode, connect the MCP server using:"
Write-Host "ai-research-mcp"
