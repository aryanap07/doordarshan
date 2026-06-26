from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ParticipantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    user_id: int
    joined_at: datetime
    left_at: datetime | None
