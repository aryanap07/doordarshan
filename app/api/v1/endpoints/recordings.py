from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import CurrentUser, DBSession
from app.crud.crud_meeting import get_meeting_by_id
from app.crud.crud_recording import (
    create_recording,
    delete_recording,
    get_recording_by_id,
    get_recordings,
)
from app.models.recording import Recording
from app.schemas.recording import RecordingCreate, RecordingResponse

router = APIRouter(
    prefix="/recordings",
    tags=["Recordings"],
)


@router.post(
    "",
    response_model=RecordingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_recording(
    recording_data: RecordingCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> Recording:
    meeting = get_meeting_by_id(db, recording_data.meeting_id)
    if meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found",
        )

    return create_recording(
        db=db,
        recording=recording_data,
        creator_id=current_user.id,
    )


@router.get(
    "",
    response_model=list[RecordingResponse],
)
def list_recordings(
    db: DBSession,
) -> list[Recording]:
    return get_recordings(db)


@router.get(
    "/{recording_id}",
    response_model=RecordingResponse,
)
def get_recording(
    recording_id: int,
    db: DBSession,
) -> Recording:
    recording = get_recording_by_id(db, recording_id)

    if recording is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found",
        )

    return recording


@router.delete(
    "/{recording_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_recording_endpoint(
    recording_id: int,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    recording = get_recording_by_id(db, recording_id)

    if recording is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found",
        )

    if recording.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator can delete this recording.",
        )

    delete_recording(db, recording)
