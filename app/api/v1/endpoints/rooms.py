from fastapi import APIRouter, HTTPException, Response, status

from app.api.dependencies import CurrentUser, DBSession
from app.crud.crud_room import (
    create_room,
    delete_room,
    get_room_by_code,
    get_rooms,
)
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomResponse

router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"],
)


@router.post(
    "",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_room(
    room: RoomCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> Room:
    return create_room(
        db=db,
        room=room,
        host_id=current_user.id,
    )


@router.get(
    "",
    response_model=list[RoomResponse],
)
def list_rooms(
    db: DBSession,
) -> list[Room]:
    return get_rooms(db)


@router.get(
    "/{room_code}",
    response_model=RoomResponse,
)
def get_room(
    room_code: str,
    db: DBSession,
) -> Room:
    room = get_room_by_code(db, room_code)

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    return room


@router.delete(
    "/{room_code}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_room(
    room_code: str,
    db: DBSession,
    current_user: CurrentUser,
) -> Response:
    room = get_room_by_code(db, room_code)

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    if room.host_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the room host can delete this room.",
        )

    delete_room(db, room)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
