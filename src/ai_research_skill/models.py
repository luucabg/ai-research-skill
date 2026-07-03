from __future__ import annotations

from pydantic import BaseModel, Field


class VideoResult(BaseModel):
    id: str
    title: str = ""
    url: str
    channel: str = ""
    duration: int | None = None
    view_count: int | None = None
    upload_date: str | None = None
    description: str = ""


class TranscriptSegment(BaseModel):
    text: str
    start: float | None = None
    duration: float | None = None


class TranscriptResult(BaseModel):
    video_id: str
    url: str
    source: str
    language: str | None = None
    text: str
    segments: list[TranscriptSegment] = Field(default_factory=list)


class Comment(BaseModel):
    text: str
    author: str | None = None
    like_count: int | None = None
    timestamp: str | None = None


class VideoResearchItem(BaseModel):
    video: VideoResult
    transcript: TranscriptResult | None = None
    transcript_error: str | None = None
    comments: list[Comment] = Field(default_factory=list)
    comments_error: str | None = None
