# backend/api/schemas.py
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------- Choices ----------
class ChoiceCreate(BaseModel):
    label: str = Field(..., min_length=1, max_length=10)  # "A","B",...
    text_en: str = Field(..., min_length=1)
    text_zh: str | None = None


class ChoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    label: str
    text_en: str
    text_zh: str | None


# ---------- Questions ----------
class QuestionCreate(BaseModel):
    stem_en: str = Field(..., min_length=1)
    stem_zh: str = Field(..., min_length=1)
    explanation_en: str | None = None
    explanation_zh: str | None = None
    difficulty: int = Field(default=1, ge=1, le=5)
    domain: str | None = None
    question_type: Literal["single", "multi"] = "single"
    active: bool = True

    choices: list[ChoiceCreate] = Field(..., min_length=2)
    answers: list[str] = Field(..., min_length=1)  # labels, e.g. ["A"] or ["A","C"]


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stem_en: str
    stem_zh: str
    explanation_en: str | None
    explanation_zh: str | None
    difficulty: int
    domain: str | None
    question_type: str
    active: bool
    created_at: datetime

    choices: list[ChoiceOut]
    # return correct answer labels for now (later you can hide this)
    answer_labels: list[str] = []


class AttemptCreate(BaseModel):
    user_id: str = "local"
    question_id: int
    selected_choice_ids: list[int] = Field(default_factory=list)


class AttemptResult(BaseModel):
    question_id: int
    user_id: str
    selected_choice_ids: list[int]
    is_correct: bool
    correct_choice_ids: list[int]
    correct_labels: list[str]
    domain: str | None
    explanation_en: str | None
    explanation_zh: str | None


class DomainScore(BaseModel):
    domain: str
    answered: int
    correct: int
    incorrect: int
    percentage: float


class AttemptSummary(BaseModel):
    user_id: str
    total_questions: int
    total_answered: int
    total_correct: int
    total_incorrect: int
    total_unanswered: int
    overall_percentage: float
    by_domain: list[DomainScore]
