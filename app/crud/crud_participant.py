from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.participant import Participant
from app.models.room import Room
from app.models.user import User


def get_participant(
    db: Session,
    room_id: int,
    user_id: int,
) -> Participant | None:

    return db.scalar(
        select(Participant).where(
            Participant.room_id == room_id,
            Participant.user_id == user_id,
            Participant.left_at.is_(None),
        )
    )


def join_room(
    db: Session,
    room: Room,
    user: User,
) -> Participant:

    participant = get_participant(
        db=db,
        room_id=room.id,
        user_id=user.id,
    )

    if participant is not None:
        return participant

    participant = Participant(
        room_id=room.id,
        user_id=user.id,
    )

    db.add(participant)
    db.commit()
    db.refresh(participant)

    return participant


def leave_room(
    db: Session,
    participant: Participant,
) -> Participant:

    participant.left_at = datetime.now(UTC)

    db.commit()
    db.refresh(participant)

    return participant


def get_room_participants(
    db: Session,
    room_id: int,
) -> list[Participant]:

    return list(
        db.scalars(
            select(Participant).where(
                Participant.room_id == room_id,
                Participant.left_at.is_(None),
            )
        ).all()
    )
