from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoomBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    is_active: bool | None = None


class RoomResponse(RoomBase):
    id: int
    room_code: str
    host_id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
