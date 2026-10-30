from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(
    prefix="/ice",
    tags=["ICE"],
)


@router.get("/config")
async def get_ice_config():
    return {
        "iceServers": [
            {
                "urls": [
                    "stun:global.relay.metered.ca:80",
                ]
            },
            {
                "urls": [
                    "turn:global.relay.metered.ca:80",
                    "turn:global.relay.metered.ca:80?transport=tcp",
                    "turn:global.relay.metered.ca:443",
                    "turns:global.relay.metered.ca:443?transport=tcp",
                ],
                "username": settings.metered_username,
                "credential": settings.metered_credential,
            },
        ]
    }
