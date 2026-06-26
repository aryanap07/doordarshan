from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.room_code import generate_room_code
from app.models.room import Room
from app.schemas.room import RoomCreate


def get_room_by_code(db: Session, room_code: str) -> Room | None:
    return db.scalar(select(Room).where(Room.room_code == room_code))


def get_rooms(db: Session) -> list[Room]:
    return list(db.scalars(select(Room)).all())


def create_room(
    db: Session,
    room: RoomCreate,
    host_id: int,
) -> Room:
    room_code = generate_room_code()

    while get_room_by_code(db, room_code):
        room_code = generate_room_code()

    db_room = Room(
        room_code=room_code,
        title=room.title,
        host_id=host_id,
    )

    db.add(db_room)
    db.commit()
    db.refresh(db_room)

    return db_room


def delete_room(
    db: Session,
    room: Room,
) -> None:
    db.delete(room)
    db.commit()
