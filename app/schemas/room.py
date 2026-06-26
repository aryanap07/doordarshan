from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoomCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=100,
        examples=["AI Study Group"],
    )


class RoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_code: str
    title: str
    is_active: bool
    host_id: int
    created_at: datetime
