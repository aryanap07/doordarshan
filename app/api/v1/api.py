from fastapi import APIRouter

from app.api.v1.endpoints import auth, meetings, participants, recordings, rooms, users

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(rooms.router)
api_router.include_router(participants.router)
api_router.include_router(meetings.router)
api_router.include_router(recordings.router)
