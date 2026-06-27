from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RecordingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    creator_id: int
    file_url: str
    duration_seconds: int | None
    created_at: datetime
