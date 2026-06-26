from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import CurrentUser, DBSession
from app.crud.crud_participant import (
    get_participant,
    get_room_participants,
    join_room,
    leave_room,
)
from app.crud.crud_room import get_room_by_code
from app.models.participant import Participant
from app.schemas.participant import ParticipantResponse

router = APIRouter(
    prefix="/rooms",
    tags=["Participants"],
)


@router.post(
    "/{room_code}/join",
    response_model=ParticipantResponse,
    status_code=status.HTTP_200_OK,
)
def join_room_endpoint(
    room_code: str,
    db: DBSession,
    current_user: CurrentUser,
) -> Participant:
    room = get_room_by_code(db, room_code)

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found.",
        )

    return join_room(
        db=db,
        room=room,
        user=current_user,
    )


@router.post(
    "/{room_code}/leave",
    response_model=ParticipantResponse,
)
def leave_room_endpoint(
    room_code: str,
    db: DBSession,
    current_user: CurrentUser,
) -> Participant:
    room = get_room_by_code(db, room_code)

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found.",
        )

    participant = get_participant(
        db=db,
        room_id=room.id,
        user_id=current_user.id,
    )

    if participant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found.",
        )

    return leave_room(
        db=db,
        participant=participant,
    )


@router.get(
    "/{room_code}/participants",
    response_model=list[ParticipantResponse],
)
def list_participants(
    room_code: str,
    db: DBSession,
) -> list[Participant]:
    room = get_room_by_code(db, room_code)

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found.",
        )

    return get_room_participants(
        db=db,
        room_id=room.id,
    )
