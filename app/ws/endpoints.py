from __future__ import annotations

import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.security import decode_access_token
from app.crud.crud_room import get_room_by_code
from app.crud.crud_user import get_user_by_id
from app.db.base import SessionLocal
from app.ws.connection_manager import manager
from app.ws.constants import (
    WS_CLOSE_INTERNAL_ERROR,
    WS_CLOSE_POLICY_VIOLATION,
)
from app.ws.exceptions import (
    AuthenticationError,
    GracefulDisconnect,
    MessageValidationError,
    RoomInactiveError,
    RoomNotFoundError,
    TargetNotFoundError,
    WebSocketError,
)
from app.ws.handlers import dispatch_message
from app.ws.heartbeat import heartbeat_manager
from app.ws.messages import ErrorMessage
from app.ws.utils import send_json
from app.ws.validators import parse_message

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket Signaling"])


@router.websocket("/ws/rooms/{room_code}")
async def websocket_signaling(
    websocket: WebSocket,
    room_code: str,
    token: str | None = Query(default=None),
) -> None:
    if token is None:
        await websocket.close(
            code=WS_CLOSE_POLICY_VIOLATION,
            reason="Missing token",
        )
        return

    db = SessionLocal()

    try:
        try:
            payload = decode_access_token(token)
            user_id = int(payload["sub"])
        except (ValueError, TypeError, KeyError) as exc:
            raise AuthenticationError("Invalid or expired token") from exc

        user = get_user_by_id(db, user_id)
        if user is None:
            raise AuthenticationError("User not found")

        room = get_room_by_code(db, room_code)
        if room is None:
            raise RoomNotFoundError("Room not found")

        if not room.is_active:
            raise RoomInactiveError("Room is inactive")

        username = user.username

    except WebSocketError as exc:
        await websocket.close(code=exc.code, reason=str(exc))
        return

    except Exception:
        logger.exception("Handshake failed")
        await websocket.close(
            code=WS_CLOSE_INTERNAL_ERROR,
            reason="Internal server error",
        )
        return

    finally:
        db.close()

    await manager.connect(
        websocket=websocket,
        room_code=room_code,
        user_id=user_id,
        username=username,
    )

    heartbeat_manager.start(websocket)

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                message = parse_message(raw)
            except MessageValidationError as exc:
                await send_json(
                    websocket,
                    ErrorMessage(
                        code="validation_error",
                        message=str(exc),
                    ),
                )
                continue

            participant = manager.get_participant_by_ws(websocket)
            if participant is None:
                break

            try:
                await dispatch_message(
                    websocket,
                    participant,
                    message,
                )

            except GracefulDisconnect:
                logger.info("Participant left: user_id=%s", user_id)
                break

            except TargetNotFoundError as exc:
                await send_json(
                    websocket,
                    ErrorMessage(
                        code="target_not_found",
                        message=str(exc),
                    ),
                )

            except WebSocketError as exc:
                await send_json(
                    websocket,
                    ErrorMessage(
                        code="signaling_error",
                        message=str(exc),
                    ),
                )

            except Exception:
                logger.exception("Dispatch error: user_id=%s", user_id)
                await send_json(
                    websocket,
                    ErrorMessage(
                        code="internal_error",
                        message="Internal server error",
                    ),
                )

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: user_id=%s", user_id)

    except Exception:
        logger.exception("WebSocket loop failed: user_id=%s", user_id)

    finally:
        await heartbeat_manager.stop(websocket)
        await manager.disconnect(websocket)
