# Doordarshan

> An open-source video conferencing backend built with **FastAPI**, **WebRTC Signaling**, **WebSockets**, **SQLAlchemy**, and **Alembic**.

Doordarshan is a modern backend service that powers real-time video conferencing applications. It provides secure authentication, meeting management, participant management, room management, and WebRTC signaling over WebSockets.

The goal of this project is to create a clean, scalable, and production-ready backend that is easy to understand, extend, and contribute to.

---

# Table of Contents

- [Introduction](#introduction)
- [Project Goals](#project-goals)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Database Migrations](#database-migrations)
- [Running the Project](#running-the-project)
- [API Overview](#api-overview)
- [WebSocket Signaling](#websocket-signaling)
- [Authentication](#authentication)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Style](#code-style)
- [Security](#security)
- [Future Roadmap](#future-roadmap)
- [Contributing](#contributing)
- [License](#license)

---

# Introduction

Video conferencing applications require much more than video streaming.

A complete backend needs to handle:

- User Authentication
- Meeting Creation
- Room Management
- Participant Tracking
- Secure API Access
- WebRTC Signaling
- Database Management

Doordarshan provides all of these components using modern Python technologies while keeping the codebase simple enough for students and contributors.

---

# Project Goals

This project aims to:

- Learn backend architecture
- Understand WebRTC signaling
- Build scalable APIs
- Practice clean software engineering
- Follow open-source coding standards
- Create a backend suitable for real-world video conferencing applications

---

# Features

## Authentication

- User Registration
- Secure Login
- JWT Authentication
- Password Hashing
- Protected API Routes

---

## Meeting Management

- Create Meetings
- Retrieve Meeting Information
- Update Meetings
- Delete Meetings

---

## Room Management

- Create Rooms
- Join Rooms
- Leave Rooms
- Room Code Generation

---

## Participant Management

- Track Participants
- Participant CRUD Operations
- Active Participant Management

---

## WebRTC Signaling

The project includes a WebSocket signaling server responsible for exchanging:

- SDP Offer
- SDP Answer
- ICE Candidates
- Join Messages
- Leave Messages
- Direct Peer Messages

This signaling layer enables browsers to establish peer-to-peer WebRTC connections.

---

## Database

Supports:

- SQLite
- PostgreSQL

Database schema is managed using Alembic migrations.

---

# Technology Stack

| Technology | Purpose |
|------------|---------|
| FastAPI | REST API Framework |
| WebSockets | Real-time Communication |
| WebRTC | Peer-to-Peer Video Calls |
| SQLAlchemy | ORM |
| Alembic | Database Migrations |
| Pydantic | Data Validation |
| JWT | Authentication |
| Argon2 | Password Hashing |
| Uvicorn | ASGI Server |

---

# System Architecture

```
Client
   │
   │ REST API
   ▼
FastAPI Backend
   │
   ├──────── Authentication
   ├──────── Meetings
   ├──────── Rooms
   ├──────── Participants
   └──────── Recordings

           │

WebSocket Signaling Server

           │

      WebRTC Peers

           │

      SQLite / PostgreSQL
```

---

# Project Structure

```
doordarshan/

│
├── app/
│   ├── api/
│   ├── core/
│   ├── crud/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── ws/
│   └── main.py
│
├── alembic/
│
├── tests/
│
├── scripts/
│
├── pyproject.toml
├── Makefile
├── README.md
└── LICENSE
```

---

# Installation

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/doordarshan.git

cd doordarshan
```

---

## 2. Create Virtual Environment

Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

Linux / macOS

```bash
python -m venv .venv

source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -e ".[dev]"
```

---

# Environment Variables

Create a `.env` file.

Example:

```env
APP_NAME=Doordarshan

SECRET_KEY=your_super_secret_key

DATABASE_URL=sqlite:///./doordarshan.db

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## SECRET_KEY

The `SECRET_KEY` is used to digitally sign JWT authentication tokens.

It ensures that:

- Tokens cannot be modified
- Users cannot forge authentication
- Server can verify every login token

**Never commit your SECRET_KEY to GitHub.**

---

# Database Migrations

Create migration

```bash
make revision
```

Apply migrations

```bash
make migrate
```

Rollback

```bash
make downgrade
```

Alembic keeps the database schema synchronized with your SQLAlchemy models.

---

# Running the Project

Development server

```bash
make run
```

or

```bash
uvicorn app.main:app --reload
```

Server starts at

```
http://127.0.0.1:8000
```

Swagger documentation

```
http://127.0.0.1:8000/docs
```

ReDoc

```
http://127.0.0.1:8000/redoc
```

---

# API Overview

Current API modules include:

```
Authentication

Users

Meetings

Rooms

Participants

Recordings

Health Check
```

Each endpoint follows RESTful principles and returns JSON responses.

---

# WebSocket Signaling

WebRTC cannot establish peer-to-peer connections without exchanging signaling messages.

Doordarshan includes a dedicated WebSocket signaling server.

Supported message types include:

- Offer
- Answer
- ICE Candidate
- Join
- Leave
- Direct Messages

Typical signaling flow:

```
User A

↓

Offer

↓

WebSocket Server

↓

User B

↓

Answer

↓

WebSocket Server

↓

User A

↓

ICE Candidate Exchange

↓

Peer Connection Established
```

---

# Authentication

Authentication uses JWT.

Workflow:

```
Register

↓

Login

↓

Receive JWT Token

↓

Include Token

Authorization: Bearer <token>

↓

Access Protected APIs
```

Passwords are securely hashed using Argon2 before being stored in the database.

---

# Development Workflow

Useful Make commands:

Install

```bash
make install
```

Development Dependencies

```bash
make dev
```

Run Server

```bash
make run
```

Run Tests

```bash
make test
```

Format Code

```bash
make format
```

Lint

```bash
make lint
```

Run All Checks

```bash
make check
```

Build Package

```bash
make build
```

---

# Testing

Run the test suite:

```bash
pytest
```

With coverage:

```bash
pytest --cov=app
```

---

# Code Style

This project follows modern Python development practices.

Tools used:

- Black
- Ruff
- MyPy
- Pytest

Please ensure all checks pass before opening a Pull Request.

---

# Security

Current security measures include:

- JWT Authentication
- Password Hashing (Argon2)
- Input Validation with Pydantic
- SQLAlchemy ORM
- Typed Models
- Environment Variables
- Protected Routes

---

# Future Roadmap

Planned features include:

- Video Recording
- Screen Sharing
- Chat Messaging
- File Sharing
- TURN/STUN Integration
- Docker Support
- Kubernetes Deployment
- Redis Pub/Sub
- Horizontal Scaling
- Monitoring
- CI/CD Pipeline
- Production Deployment

---

# Contributing

Contributions are welcome.

Steps:

1. Fork the repository.
2. Create a new branch.
3. Implement your feature.
4. Run formatting and tests.
5. Commit your changes.
6. Push your branch.
7. Open a Pull Request.

Please keep your code clean, documented, and consistent with the existing project structure.

---

# License

This project is licensed under the MIT License.

See the `LICENSE` file for more information.

---

# Acknowledgements

Built with ❤️ using

- FastAPI
- SQLAlchemy
- Alembic
- WebRTC
- WebSockets
- Pydantic
- Python

---

**Doordarshan** is an educational and open-source project intended to demonstrate how modern backend technologies can be combined to build a scalable real-time video conferencing platform.

