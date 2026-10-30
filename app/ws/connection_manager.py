from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from fastapi import WebSocket

from app.ws.messages import (
    BaseMessage,
    ParticipantInfo,
    ParticipantJoinedMessage,
    ParticipantLeftMessage,
    ParticipantListMessage,
)
from app.ws.utils import send_json

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ConnectedParticipant:
    user_id: int
    username: str
    websocket: WebSocket
    room_code: str


class ConnectionManager:
    def __init__(self) -> None:
        self._rooms: dict[str, dict[int, ConnectedParticipant]] = {}
        self._reverse: dict[WebSocket, ConnectedParticipant] = {}

    async def connect(
        self,
        websocket: WebSocket,
        room_code: str,
        user_id: int,
        username: str,
    ) -> None:
        await websocket.accept()

        participant = ConnectedParticipant(
            user_id=user_id,
            username=username,
            websocket=websocket,
            room_code=room_code,
        )

        room = self._rooms.setdefault(room_code, {})

        old = room.get(user_id)
        if old is not None:
            self._reverse.pop(old.websocket, None)

        room[user_id] = participant
        self._reverse[websocket] = participant

        logger.info(
            "Participant joined: user_id=%s participant_count=%d",
            user_id,
            len(room),
        )

        await self._broadcast(
            room_code,
            ParticipantJoinedMessage(
                user_id=user_id,
                username=username,
            ),
            exclude_user_id=user_id,
        )

        participants = [
            ParticipantInfo(
                user_id=p.user_id,
                username=p.username,
            )
            for p in room.values()
            if p.user_id != user_id
        ]

        await send_json(
            websocket,
            ParticipantListMessage(participants=participants),
        )

    async def disconnect(self, websocket: WebSocket) -> None:
        participant = self._reverse.pop(websocket, None)
        if participant is None:
            return

        room = self._rooms.get(participant.room_code)
        if room is None:
            return

        room.pop(participant.user_id, None)

        if not room:
            self._rooms.pop(participant.room_code, None)

        logger.info(
            "Participant left: user_id=%s participant_count=%d",
            participant.user_id,
            len(room),
        )

        await self._broadcast(
            participant.room_code,
            ParticipantLeftMessage(
                user_id=participant.user_id,
                username=participant.username,
            ),
        )

    async def send_to(
        self,
        room_code: str,
        user_id: int,
        message: BaseMessage,
    ) -> bool:
        participant = self.get_participant(room_code, user_id)
        if participant is None:
            return False

        return await send_json(participant.websocket, message)

    async def broadcast(
        self,
        room_code: str,
        message: BaseMessage,
        exclude_user_id: int | None = None,
    ) -> None:
        await self._broadcast(room_code, message, exclude_user_id)

    async def _broadcast(
        self,
        room_code: str,
        message: BaseMessage,
        exclude_user_id: int | None = None,
    ) -> None:
        participants = [
            participant
            for participant in self.list_participants(room_code)
            if exclude_user_id is None or participant.user_id != exclude_user_id
        ]

        if not participants:
            return

        results = await asyncio.gather(
            *(send_json(p.websocket, message) for p in participants),
            return_exceptions=True,
        )

        for participant, result in zip(participants, results, strict=True):
            if isinstance(result, Exception):
                logger.error(
                    "Broadcast failed: user_id=%s error_type=%s",
                    participant.user_id,
                    type(result).__name__,
                    exc_info=(type(result), result, result.__traceback__),
                )

    def get_participant_by_ws(
        self,
        websocket: WebSocket,
    ) -> ConnectedParticipant | None:
        return self._reverse.get(websocket)

    def get_participant(
        self,
        room_code: str,
        user_id: int,
    ) -> ConnectedParticipant | None:
        return self._rooms.get(room_code, {}).get(user_id)

    def list_participants(
        self,
        room_code: str,
    ) -> list[ConnectedParticipant]:
        return list(self._rooms.get(room_code, {}).values())

    @property
    def total_rooms(self) -> int:
        return len(self._rooms)

    @property
    def total_connections(self) -> int:
        return len(self._reverse)


manager = ConnectionManager()
