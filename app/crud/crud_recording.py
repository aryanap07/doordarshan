from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.recording import Recording
from app.schemas.recording import RecordingCreate


def get_recording_by_id(db: Session, recording_id: int) -> Recording | None:
    return db.scalar(select(Recording).where(Recording.id == recording_id))


def get_recordings(db: Session) -> list[Recording]:
    return list(db.scalars(select(Recording)).all())


def create_recording(
    db: Session,
    recording: RecordingCreate,
    creator_id: int,
) -> Recording:
    db_recording = Recording(
        meeting_id=recording.meeting_id,
        creator_id=creator_id,
        file_url=recording.file_url,
        duration_seconds=recording.duration_seconds,
    )

    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)

    return db_recording


def delete_recording(db: Session, recording: Recording) -> None:
    db.delete(recording)
    db.commit()
