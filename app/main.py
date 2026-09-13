from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import api_router
from app.ws.endpoints import router as ws_router

app = FastAPI(title="Doordarshan")

CLIENT_DIR = Path(__file__).resolve().parent.parent / "client"

app.mount("/css", StaticFiles(directory=CLIENT_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=CLIENT_DIR / "js"), name="js")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return FileResponse(CLIENT_DIR / "index.html")

@app.get("/login")
async def login():
    return FileResponse(CLIENT_DIR / "index.html")

@app.get("/register")
async def register():
    return FileResponse(CLIENT_DIR / "register.html")

@app.get("/dashboard")
async def dashboard():
    return FileResponse(CLIENT_DIR / "dashboard.html")

@app.get("/room")
async def room():
    return FileResponse(CLIENT_DIR / "room.html")

app.include_router(api_router, prefix="/api/v1")
app.include_router(ws_router)