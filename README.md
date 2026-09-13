<div align="center">

# 𝘿𝙤𝙤𝙧𝘿𝙖𝙧𝙨𝙝𝙖𝙣

**WebRTC · WebSockets · FastAPI**

</div>

### Real-time video conferencing built with FastAPI, WebRTC, and WebSockets.

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![WebRTC](https://img.shields.io/badge/WebRTC-Real--Time-111827?style=flat-square&logo=webrtc&logoColor=white)](https://webrtc.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square&logo=opensourceinitiative&logoColor=white)](LICENSE)

Doordarshan is a full-stack video conferencing application built around real-time communication, clean interaction patterns, and a focused meeting experience.

It combines a FastAPI backend, WebSocket signaling, browser-native WebRTC, PostgreSQL, and a lightweight frontend to deliver authenticated rooms, participant management, live audio/video, screen sharing, chat, and meeting scheduling.

---

## Overview

Doordarshan is built around a straightforward meeting workflow:

**Sign in → Create or join a room → Connect participants → Communicate in real time**

The application keeps the meeting experience intentionally focused while maintaining a backend architecture that separates API endpoints, business services, persistence, WebSocket communication, and WebRTC handling.

It is designed as an open-source foundation that can evolve toward a larger-scale collaboration platform without sacrificing the simplicity of the core experience.

---

## Core Features

### Real-Time Meetings

- Browser-based video and audio communication
- WebRTC peer connections
- WebSocket-based signaling
- Automatic peer negotiation
- ICE candidate exchange
- Connection-state monitoring and recovery
- Camera and microphone controls
- Screen sharing
- Audio-only fallback when camera access is unavailable

### Rooms & Participants

- Create meeting rooms
- Automatically generated room codes
- Join rooms using a code
- Leave active rooms
- View connected participants
- Real-time participant join/leave updates
- Participant count synchronization

### Communication

- In-room chat
- Real-time direct messages through the WebSocket layer
- Chat unread indicators
- Participant and chat sidebar
- Connection status feedback

### Authentication

- User registration
- Email/password authentication
- JWT access tokens
- Password hashing using Argon2
- Protected API and WebSocket access
- Session-aware frontend authentication

### Meeting Management

- Schedule meetings
- List scheduled meetings
- Retrieve meeting details
- Delete meetings
- Associate meetings with application users and rooms

### Backend Foundation

- PostgreSQL persistence
- SQLAlchemy ORM
- Alembic migrations
- Pydantic schemas and settings
- Service and CRUD layers
- API versioning under `/api/v1`
- Request logging
- Rate-limiting middleware
- Automated tests and coverage tooling
- Static frontend served directly by FastAPI

---

## UI/UX

Doordarshan follows a communication-first interface philosophy inspired by established conferencing products while maintaining its own visual identity.

### Dashboard

The dashboard acts as the meeting control center, providing immediate access to:

- New Room
- Join by Code
- Schedule Meeting
- Existing rooms
- Scheduled meetings

The layout keeps primary actions visible without overwhelming the user.

### Meeting Room

The meeting interface is designed around the active call:

```text
┌─────────────────────────────────────────────────────────────┐
│ Doordarshan     Room Name / Code          Live • Participants│
├───────────────────────────────────────────────┬─────────────┤
│                                               │             │
│                 Video Grid                    │   People    │
│                                               │   / Chat    │
│                                               │             │
│                                               │             │
├───────────────────────────────────────────────┴─────────────┤
│       Mute     Camera     Share     Chat          Leave      │
└─────────────────────────────────────────────────────────────┘
```

### Interaction Details

- Clear meeting-state indicators
- Persistent room context
- Focused call controls
- Responsive video grid
- People and chat panels
- Permission recovery messaging
- Toast notifications for important events
- Visual connection-state feedback
- Keyboard-friendly form interactions
- Consistent spacing, typography, and component hierarchy

The frontend uses **Inter** for primary UI typography and **JetBrains Mono** for technical and code-oriented elements.

---
## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI |
| ASGI Server | Uvicorn |
| Real-Time Transport | WebSockets |
| Media Communication | WebRTC |
| ORM | SQLAlchemy 2 |
| Database | PostgreSQL |
| Database Driver | Psycopg 3 |
| Migrations | Alembic |
| Validation | Pydantic |
| Configuration | Pydantic Settings |
| Authentication | JWT |
| Password Security | Argon2 |
| Frontend | HTML, CSS, JavaScript |
| TURN / ICE | Metered |
| Testing | Pytest, pytest-asyncio |
| Quality | Ruff, Black, Mypy |
| Deployment | Render-compatible |

---

## Architecture

Doordarshan follows a layered backend architecture that keeps transport, application logic, and persistence concerns separated.

```text
                         ┌─────────────────────┐
                         │      Browser UI      │
                         │ HTML / CSS / JS      │
                         └──────────┬──────────┘
                                    │
                 ┌──────────────────┴──────────────────┐
                 │                                     │
                 ▼                                     ▼
        ┌─────────────────┐                   ┌─────────────────┐
        │ REST API /v1    │                   │ WebSocket /ws   │
        │ Authentication  │                   │ Signaling       │
        │ Rooms           │                   │ Chat            │
        │ Meetings        │                   │ Presence        │
        │ Participants    │                   │ Heartbeats      │
        └────────┬────────┘                   └────────┬────────┘
                 │                                     │
                 └──────────────────┬──────────────────┘
                                    ▼
                         ┌─────────────────────┐
                         │      Services       │
                         │ Auth / Room /       │
                         │ Meeting / Recording │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                         │       CRUD          │
                         │ Persistence Logic   │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                         │     SQLAlchemy      │
                         │      PostgreSQL     │
                         └─────────────────────┘

          WebSocket Signaling ─────► WebRTC Peer Connections
                                    │
                                    ▼
                              Audio / Video
                              Screen Sharing
```

---

## Project Structure

```text
doordarshan/
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   └── v1/
│   │       ├── api.py
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── ice.py
│   │           ├── meetings.py
│   │           ├── participants.py
│   │           ├── recordings.py
│   │           ├── rooms.py
│   │           └── users.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── logging_config.py
│   │   ├── room_code.py
│   │   └── security.py
│   │
│   ├── crud/
│   │   ├── crud_meeting.py
│   │   ├── crud_participant.py
│   │   ├── crud_recording.py
│   │   ├── crud_room.py
│   │   └── crud_user.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   ├── base_class.py
│   │   ├── init_db.py
│   │   └── session.py
│   │
│   ├── middlewares/
│   │   ├── rate_limiter.py
│   │   └── request_logger.py
│   │
│   ├── models/
│   │   ├── chat_message.py
│   │   ├── meeting.py
│   │   ├── participant.py
│   │   ├── recording.py
│   │   ├── room.py
│   │   └── user.py
│   │
│   ├── schemas/
│   │   ├── meeting.py
│   │   ├── participant.py
│   │   ├── recording.py
│   │   ├── room.py
│   │   ├── signaling.py
│   │   ├── token.py
│   │   └── user.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── meeting_service.py
│   │   ├── notification_service.py
│   │   ├── recording_service.py
│   │   └── room_service.py
│   │
│   ├── utils/
│   │   ├── email.py
│   │   ├── helpers.py
│   │   └── validators.py
│   │
│   ├── webrtc/
│   │   ├── ice_servers.py
│   │   ├── media_handler.py
│   │   └── sfu.py
│   │
│   ├── ws/
│   │   ├── chat.py
│   │   ├── connection_manager.py
│   │   ├── constants.py
│   │   ├── endpoints.py
│   │   ├── enums.py
│   │   ├── events.py
│   │   ├── exceptions.py
│   │   ├── handlers.py
│   │   ├── heartbeat.py
│   │   ├── messages.py
│   │   ├── signaling.py
│   │   ├── utils.py
│   │   └── validators.py
│   │
│   └── main.py
│
├── client/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── dashboard.js
│   │   ├── media.js
│   │   ├── room.js
│   │   ├── webrtc.js
│   │   └── websocket.js
│   ├── dashboard.html
│   ├── index.html
│   ├── register.html
│   └── room.html
│
├── alembic/
│   └── versions/
│
├── tests/
│   ├── api/
│   └── ws/
│
├── .env.example
├── alembic.ini
├── Makefile
├── pyproject.toml
└── LICENSE
```

---

## Core Functionality

### Authentication Flow

```text
User
 │
 ├── Register
 │      ↓
 │   Password hashing
 │      ↓
 │   PostgreSQL
 │
 └── Login
        ↓
     JWT issued
        ↓
     Token stored in browser
        ↓
     Protected API / WebSocket access
```

### Room Flow

```text
Create Room
     ↓
Generate Room Code
     ↓
Persist Room
     ↓
Join with Code
     ↓
Participant Created
     ↓
WebSocket Connection
     ↓
Presence Synchronization
     ↓
WebRTC Negotiation
     ↓
Live Communication
```

### WebRTC Signaling

Doordarshan uses WebSockets as the signaling channel rather than transporting media through the application server.

The browser handles the media connection using `RTCPeerConnection`, while the backend coordinates:

- Offers
- Answers
- ICE candidates
- Participant presence
- Connection lifecycle events
- Room messaging

This keeps media transport separate from the application's real-time control plane.

---

## API Surface

The backend is versioned under:

```text
/api/v1
```

Primary API domains include:

```text
/auth
/rooms
/rooms/{room_code}/join
/rooms/{room_code}/leave
/rooms/{room_code}/participants
/meetings
/recordings
/ice
/users
```

FastAPI's generated API documentation is available during local development at:

```text
/docs
```

and:

```text
/redoc
```

---

## Installation

### Requirements

Make sure the following are installed:

- Python 3.11+
- PostgreSQL
- Git
- A modern browser with WebRTC support

For production deployments, a PostgreSQL provider such as Neon can be used.

---

### Clone the Repository

```bash
git clone https://github.com/aryanap07/doordarshan.git
cd doordarshan
```

---

### Create a Virtual Environment

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

---

### Install Dependencies

For development:

```bash
pip install -e ".[dev]"
```

For a standard installation:

```bash
pip install .
```

---

## Configuration

Create an environment file:

```bash
cp .env.example .env
```

Configure the required values:

```env
APP_NAME=Doordarshan

SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DATABASE?sslmode=require

METERED_USERNAME=YOUR_METERED_USERNAME
METERED_CREDENTIAL=YOUR_METERED_CREDENTIAL
```

### Configuration Reference

| Variable | Purpose |
|---|---|
| `APP_NAME` | Application name |
| `SECRET_KEY` | JWT signing secret |
| `ALGORITHM` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access-token lifetime |
| `DATABASE_URL` | PostgreSQL connection string |
| `METERED_USERNAME` | TURN service username |
| `METERED_CREDENTIAL` | TURN service credential |

Do not commit `.env` or production credentials to the repository.

---

## Database Setup

Apply the existing Alembic migrations:

```bash
alembic upgrade head
```

Create a new migration after model changes:

```bash
alembic revision --autogenerate -m "describe the change"
```

Revert the latest migration:

```bash
alembic downgrade -1
```

---

## Run Locally

Start the development server:

```bash
make run
```

Or directly with Uvicorn:

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

---

## Development Commands

The project includes a Makefile for common development workflows.

```bash
make help
make dev
make run
make serve
make test
make coverage
make format
make lint
make check
make migrate
make revision
make downgrade
make reset-db
make clean
```

### Quality Checks

Run the complete development check:

```bash
make check
```

This combines formatting, linting, type checking, and tests.

---

## Testing

Tests are organized by application layer:

```text
tests/
├── api/
│   ├── test_auth.py
│   ├── test_meetings.py
│   └── test_rooms.py
│
└── ws/
    └── test_signaling.py
```

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

Generate an HTML coverage report:

```bash
make coverage
```

---

## Project Workflow

```text
                    ┌─────────────┐
                    │    User     │
                    └──────┬──────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Authentication │
                  └───────┬────────┘
                          │
               ┌──────────┴──────────┐
               │                     │
               ▼                     ▼
         Create Room            Join Room
               │                     │
               └──────────┬──────────┘
                          ▼
                 ┌─────────────────┐
                 │ WebSocket Room  │
                 │   Connection    │
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │   Signaling     │
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │     WebRTC      │
                 │ Audio / Video   │
                 │ Screen Sharing  │
                 └────────┬────────┘
                          │
                ┌─────────┴─────────┐
                ▼                   ▼
             Chat              Participants
```

---

## Deployment

Doordarshan can be deployed as a FastAPI application on platforms such as Render with a managed PostgreSQL database and TURN infrastructure.

### Render

Build command:

```bash
pip install -e . && alembic upgrade head
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Configure all production environment variables through the deployment platform rather than committing them to the repository.

---

## Security Considerations

Doordarshan includes several foundational security measures:

- JWT-based authentication
- Argon2 password hashing
- Protected API dependencies
- Authenticated WebSocket connections
- Request validation through Pydantic
- Input validation on API resources
- Rate-limiting middleware
- Configurable token expiration
- Environment-based secret management

Production deployments should use HTTPS/WSS, strong secrets, restricted database access, and correctly configured TURN credentials.

---

## Roadmap

### Near Term

- Improve meeting controls and participant UX
- Expand automated test coverage
- Strengthen WebRTC failure recovery
- Improve room lifecycle handling
- Expand accessibility support
- Refine responsive layouts

### Mid Term

- Persistent chat history
- Meeting recording pipeline
- Enhanced notification workflows
- Better meeting scheduling controls
- Advanced participant moderation
- Improved observability and diagnostics

### Long Term

- Scalable multi-node real-time architecture
- Dedicated media infrastructure
- Horizontal WebSocket scaling
- Advanced meeting administration
- Production-grade recording infrastructure
- Rich collaboration features

---

## Contributing

Contributions are welcome and should follow the existing project architecture.

### Development Process

```text
Fork
  ↓
Create Feature Branch
  ↓
Implement Focused Changes
  ↓
Run Tests
  ↓
Run Formatting & Linting
  ↓
Update Migrations When Required
  ↓
Open Pull Request
  ↓
Review
  ↓
Merge
```

### Contribution Guidelines

Keep pull requests focused and easy to review.

Before submitting:

```bash
make check
```

When modifying database models, include the corresponding Alembic migration.

For larger architectural or behavior changes, explain the motivation, implementation approach, and expected impact in the pull request description.

---

## License

Doordarshan is released under the **MIT License**.

See the full license text in [LICENSE](LICENSE).

---

## Developer

**Doordarshan** is an independently developed open-source project.

Built with a focus on:

**Real-Time Systems · Backend Architecture · WebRTC · WebSockets · Developer Experience**

**Developer:** [@aryanap07](https://github.com/aryanap07)

---

## Project Status

**Development Status:** Alpha

Doordarshan is actively evolving toward a more complete production-ready conferencing platform. Core authentication, room management, real-time signaling, WebRTC communication, chat, scheduling, database persistence, testing infrastructure, and deployment foundations are already present.
