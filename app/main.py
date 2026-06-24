from fastapi import FastAPI

from app.api.v1.endpoints.auth import router as auth_router


app = FastAPI(
    title="DoorDarshan",
)


app.include_router(
    auth_router,
    prefix="/api/v1",
)