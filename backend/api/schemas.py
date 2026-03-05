# backend/api/schemas.py
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------- Choices ----------
class ChoiceCreate(BaseModel):
    label: str = Field(..., min_length=1, max_length=10)  # "A","B",...
    text: str = Field(..., min_length=1)


class ChoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    label: str
    text: str


# ---------- Questions ----------
class QuestionCreate(BaseModel):
    stem: str = Field(..., min_length=1)
    explanation: str | None = None
    difficulty: int = Field(default=1, ge=1, le=5)
    domain: str | None = None
    question_type: Literal["single", "multi"] = "single"
    active: bool = True

    choices: list[ChoiceCreate] = Field(..., min_length=2)
    answers: list[str] = Field(..., min_length=1)  # labels, e.g. ["A"] or ["A","C"]


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stem: str
    explanation: str | None
    difficulty: int
    domain: str | None
    question_type: str
    active: bool
    created_at: datetime

    choices: list[ChoiceOut]
    # return correct answer labels for now (later you can hide this)
    answer_labels: list[str] = []
