from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import CurrentUser, DBSession
from app.crud.crud_meeting import (
    create_meeting,
    delete_meeting,
    get_meeting_by_id,
    get_meetings,
    update_meeting,
)
from app.models.meeting import Meeting
from app.schemas.meeting import MeetingCreate, MeetingResponse

router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"],
)


@router.post(
    "",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_meeting(
    meeting_data: MeetingCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> Meeting:
    return create_meeting(
        db=db,
        meeting=meeting_data,
        host_id=current_user.id,
    )


@router.get(
    "",
    response_model=list[MeetingResponse],
)
def list_meetings(
    db: DBSession,
) -> list[Meeting]:
    return get_meetings(db)


@router.get(
    "/{meeting_id}",
    response_model=MeetingResponse,
)
def get_meeting(
    meeting_id: int,
    db: DBSession,
) -> Meeting:
    meeting = get_meeting_by_id(db, meeting_id)

    if meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found",
        )

    return meeting


@router.put(
    "/{meeting_id}",
    response_model=MeetingResponse,
)
def update_meeting_endpoint(
    meeting_id: int,
    meeting_data: MeetingCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> Meeting:
    meeting = get_meeting_by_id(db, meeting_id)

    if meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found",
        )

    if meeting.host_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the meeting host can update this meeting.",
        )

    return update_meeting(
        db=db,
        meeting=meeting,
        meeting_data=meeting_data,
    )


@router.delete(
    "/{meeting_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_meeting_endpoint(
    meeting_id: int,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    meeting = get_meeting_by_id(db, meeting_id)

    if meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found",
        )

    if meeting.host_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the meeting host can delete this meeting.",
        )

    delete_meeting(db, meeting)
