from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MeetingBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )
    description: str | None = Field(
        default=None,
        max_length=500,
    )
    room_id: int | None = Field(
        default=None,
        description="Optional room ID associated with the meeting.",
    )
    scheduled_at: datetime | None = Field(
        default=None,
        description="Optional scheduled time for the meeting.",
    )


class MeetingCreate(MeetingBase):
    pass


class MeetingUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    description: str | None = Field(
        default=None,
        max_length=500,
    )
    room_id: int | None = Field(
        default=None,
        description="Optional room ID associated with the meeting.",
    )
    scheduled_at: datetime | None = Field(
        default=None,
        description="Optional scheduled time for the meeting.",
    )
    is_active: bool | None = None


class MeetingResponse(MeetingBase):
    id: int
    host_id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
