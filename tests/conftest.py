"""Shared, isolated fixtures for the Doordarshan test suite."""

from __future__ import annotations

import os
from collections.abc import Callable, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# These values must be set before importing application modules because the
# Settings and SQLAlchemy engine objects are created at import time.
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-only-secret-key-never-use-in-production-0123456789"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["METERED_USERNAME"] = "test-metered-user"
os.environ["METERED_CREDENTIAL"] = "test-metered-credential"
os.environ["APP_NAME"] = "Doordarshan Test"

from app.core.security import create_access_token, hash_password  # noqa: E402
from app.db.base import Base, get_db  # noqa: E402
from app.models import Meeting, Recording, Room, User  # noqa: E402

# Import all models before create_all so every mapped table is registered.


@pytest.fixture
def test_engine() -> Generator[Engine, None, None]:
    """Create a fresh in-memory database for each test."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def session_factory(test_engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


@pytest.fixture
def client(
    test_engine: Engine,
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    """Provide an API client whose HTTP and WebSocket sessions use test DB."""
    from app.main import app
    from app.ws import connection_manager, endpoints

    def override_get_db() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(endpoints, "SessionLocal", session_factory)

    # The WebSocket manager is a process-wide singleton; clear it between tests.
    connection_manager.manager._rooms.clear()
    connection_manager.manager._reverse.clear()

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        connection_manager.manager._rooms.clear()
        connection_manager.manager._reverse.clear()


@pytest.fixture
def make_user(session_factory: sessionmaker[Session]) -> Callable[..., User]:
    """Factory for persisted users with real password hashes."""

    def factory(
        *,
        username: str = "testuser",
        email: str = "testuser@example.com",
        password: str = "correct-horse-battery",
    ) -> User:
        with session_factory() as session:
            user = User(
                username=username,
                email=email,
                password_hash=hash_password(password),
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    return factory


@pytest.fixture
def make_room(session_factory: sessionmaker[Session]) -> Callable[..., Room]:
    def factory(
        *,
        host: User,
        title: str = "Architecture Review",
        room_code: str = "ROOM1234",
        is_active: bool = True,
    ) -> Room:
        with session_factory() as session:
            room = Room(
                host_id=host.id,
                title=title,
                room_code=room_code,
                is_active=is_active,
            )
            session.add(room)
            session.commit()
            session.refresh(room)
            return room

    return factory


@pytest.fixture
def make_meeting(session_factory: sessionmaker[Session]) -> Callable[..., Meeting]:
    def factory(
        *,
        host: User,
        room: Room | None = None,
        title: str = "Sprint Planning",
    ) -> Meeting:
        with session_factory() as session:
            meeting = Meeting(
                host_id=host.id,
                room_id=room.id if room else None,
                title=title,
                description="Test meeting",
                is_active=True,
            )
            session.add(meeting)
            session.commit()
            session.refresh(meeting)
            return meeting

    return factory


@pytest.fixture
def make_recording(session_factory: sessionmaker[Session]) -> Callable[..., Recording]:
    def factory(
        *,
        meeting: Meeting,
        creator: User,
        file_url: str = "https://cdn.example.test/recordings/test.mp4",
        duration_seconds: int = 120,
    ) -> Recording:
        with session_factory() as session:
            recording = Recording(
                meeting_id=meeting.id,
                creator_id=creator.id,
                file_url=file_url,
                duration_seconds=duration_seconds,
            )
            session.add(recording)
            session.commit()
            session.refresh(recording)
            return recording

    return factory


@pytest.fixture
def make_token() -> Callable[[User], str]:
    return lambda user: create_access_token(str(user.id))


@pytest.fixture
def auth_headers(make_token: Callable[[User], str]) -> Callable[[User], dict[str, str]]:
    return lambda user: {"Authorization": f"Bearer {make_token(user)}"}


@pytest.fixture(autouse=True)
def assert_no_production_database_configuration() -> Generator[None, None, None]:
    """Guard against accidental use of a developer's configured database."""
    database_url = os.environ["DATABASE_URL"].lower()
    assert database_url.startswith("sqlite+")
    assert "memory" in database_url
    yield
