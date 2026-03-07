from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 declarative base."""

    pass


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stem_en: Mapped[str] = mapped_column(Text, nullable=False)
    stem_zh: Mapped[str] = mapped_column(Text, nullable=False)
    explanation_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation_zh: Mapped[str | None] = mapped_column(Text, nullable=True)

    difficulty: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Example: "Design High-Performing Architectures"
    domain: Mapped[str | None] = mapped_column(Text, nullable=True)

    # "single" | "multi"
    question_type: Mapped[str] = mapped_column(Text, nullable=False, default="single")

    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    choices: Mapped[list[Choice]] = relationship(
        "Choice",
        back_populates="question",
        cascade="all, delete-orphan",
    )

    answers: Mapped[list[QuestionAnswer]] = relationship(
        "QuestionAnswer",
        back_populates="question",
        cascade="all, delete-orphan",
    )

    attempts: Mapped[list[Attempt]] = relationship(
        "Attempt",
        back_populates="question",
        cascade="all, delete-orphan",
    )


class Choice(Base):
    __tablename__ = "choices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # "A", "B", "C", "D"
    label: Mapped[str] = mapped_column(Text, nullable=False)

    text_en: Mapped[str] = mapped_column(Text, nullable=False)
    text_zh: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # One question should not have duplicate labels like two "A"
    __table_args__ = (UniqueConstraint("question_id", "label", name="uq_choices_question_label"),)

    # Relationships
    question: Mapped[Question] = relationship("Question", back_populates="choices")

    answered_by: Mapped[list[QuestionAnswer]] = relationship(
        "QuestionAnswer",
        back_populates="choice",
    )


class QuestionAnswer(Base):
    """
    Join table for correct answers.
    Supports multi-select by allowing multiple rows per question.
    """

    __tablename__ = "question_answers"

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    choice_id: Mapped[int] = mapped_column(
        ForeignKey("choices.id", ondelete="CASCADE"),
        primary_key=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    question: Mapped[Question] = relationship("Question", back_populates="answers")
    choice: Mapped[Choice] = relationship("Choice", back_populates="answered_by")


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # No auth yet: use "local" or a cookie-based id later
    user_id: Mapped[str] = mapped_column(Text, nullable=False, default="local", index=True)

    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # store selected choice ids as JSON array, e.g. [12, 13]
    selected_choice_ids: Mapped[list[int]] = mapped_column(
        MutableList.as_mutable(JSONB),
        nullable=False,
        default=list,
    )

    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    question: Mapped[Question] = relationship("Question", back_populates="attempts")
