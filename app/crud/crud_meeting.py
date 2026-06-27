from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.meeting import Meeting
from app.schemas.meeting import MeetingCreate


def get_meeting_by_id(db: Session, meeting_id: int) -> Meeting | None:
    return db.scalar(select(Meeting).where(Meeting.id == meeting_id))


def get_meetings(db: Session) -> list[Meeting]:
    return list(db.scalars(select(Meeting)).all())


def create_meeting(
    db: Session,
    meeting: MeetingCreate,
    host_id: int,
) -> Meeting:
    db_meeting = Meeting(
        title=meeting.title,
        description=meeting.description,
        host_id=host_id,
        room_id=meeting.room_id,
    )

    if meeting.scheduled_at is not None:
        db_meeting.scheduled_at = meeting.scheduled_at

    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)

    return db_meeting


def update_meeting(
    db: Session,
    meeting: Meeting,
    meeting_data: MeetingCreate,
) -> Meeting:
    meeting.title = meeting_data.title
    meeting.description = meeting_data.description
    meeting.room_id = meeting_data.room_id
    meeting.scheduled_at = meeting_data.scheduled_at

    db.commit()
    db.refresh(meeting)

    return meeting


def delete_meeting(db: Session, meeting: Meeting) -> None:
    db.delete(meeting)
    db.commit()
