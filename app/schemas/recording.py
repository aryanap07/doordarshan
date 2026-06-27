from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RecordingCreate(BaseModel):
    meeting_id: int
    file_url: str = Field(
        min_length=1,
        max_length=500,
        examples=["https://example.com/recordings/meeting-123.mp4"],
    )
    duration_seconds: int | None = Field(
        default=None,
        description="Optional recording duration in seconds.",
        ge=0,
    )


class RecordingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    creator_id: int
    file_url: str
    duration_seconds: int | None
    created_at: datetime
