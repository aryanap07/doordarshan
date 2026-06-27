from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.meeting import Meeting
    from app.models.participant import Participant
    from app.models.recording import Recording
    from app.models.room import Room


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    rooms: Mapped[list[Room]] = relationship(
        back_populates="host",
        cascade="all, delete-orphan",
    )

    participants: Mapped[list[Participant]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    meetings: Mapped[list[Meeting]] = relationship(
        back_populates="host",
        cascade="all, delete-orphan",
    )

    recordings: Mapped[list[Recording]] = relationship(
        back_populates="creator",
        cascade="all, delete-orphan",
    )
