# doordarshan

[![Build](https://img.shields.io/github/actions/workflow/status/aryanap07/doordarshan/ci.yml?branch=main)](https://github.com/aryanap07/doordarshan/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.12+-blue)](https://www.python.org/downloads/release/python-3121/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/aryanap07/doordarshan/pulls)

## Description

A FastAPI WebRTC video conferencing backend for secure real-time meetings.

**Tech stack:** FastAPI | WebRTC | PostgreSQL | Redis | LiveKit

## Features

- 1-on-1 video calling
- Group calls via LiveKit SFU
- In-call text chat (RTCDataChannel)
- Screen sharing
- JWT authentication
- Room management

## Project Structure

```
/workspaces/doordarshan/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── rooms.py
│   │   └── signaling.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   └── db/
│       ├── __init__.py
│       └── session.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── .env.example
├── .env
├── .gitignore
└── requirements.txt
```

## Prerequisites

- Python 3.12+
- PostgreSQL
- Redis
- Docker (optional)

## Installation

1. Clone the repo:
   ```bash
git clone https://github.com/aryanap07/doordarshan.git
cd doordarshan
```
2. Create a virtual environment:
   ```bash
python -m venv .venv
source .venv/bin/activate
```
3. Install dependencies:
   ```bash
pip install -r requirements.txt
```
4. Copy `.env.example` to `.env`:
   ```bash
cp .env.example .env
```
5. Run the server:
   ```bash
uvicorn app.main:app --reload
```

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `APP_NAME` | Application name | `doordarshan` |
| `DEBUG` | Debug mode toggle | `True` |
| `SECRET_KEY` | FastAPI secret key | `your-secret-key-here` |
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql+asyncpg://user:password@localhost:5432/doordarshan` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `JWT_SECRET` | JWT signing secret | `your-jwt-secret` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRE_MINUTES` | JWT expiry in minutes | `30` |
| `LIVEKIT_API_KEY` | LiveKit API key | `your-livekit-key` |
| `LIVEKIT_API_SECRET` | LiveKit API secret | `your-livekit-secret` |
| `LIVEKIT_URL` | LiveKit server URL | `ws://localhost:7880` |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Check service health |
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Authenticate and issue JWT |
| `GET` | `/ws/{room_id}` | WebSocket signaling endpoint for room | 

## Roadmap

- **Phase 1:** Signaling MVP (2-3 weeks)
- **Phase 2:** Auth & Rooms (2-3 weeks)
- **Phase 3:** Core Features (3-4 weeks)
- **Phase 4:** Scale & Deploy (4+ weeks)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

MIT License
