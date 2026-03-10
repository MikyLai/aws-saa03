from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from api.db import get_db
from api.models import Attempt, Question, QuestionAnswer
from api.schemas import AttemptCreate, AttemptResult, AttemptSummary, DomainScore

router = APIRouter(prefix="/attempts", tags=["attempts"])


@router.post("/", response_model=AttemptResult, status_code=status.HTTP_201_CREATED)
def create_attempt(payload: AttemptCreate, db: Session = Depends(get_db)) -> AttemptResult:
    # load question with choices + correct answers
    stmt = (
        select(Question)
        .where(Question.id == payload.question_id)
        .options(
            selectinload(Question.choices),
            selectinload(Question.answers).selectinload(QuestionAnswer.choice),
        )
    )
    question = db.execute(stmt).scalars().first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # validate selected choices belong to this question
    valid_choice_ids = {choice.id for choice in question.choices}
    invalid_ids = [cid for cid in payload.selected_choice_ids if cid not in valid_choice_ids]
    if invalid_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Selected choice id(s) do not belong to question {payload.question_id}: {invalid_ids}",
        )

    selected_ids = sorted(set(payload.selected_choice_ids))
    correct_choice_ids = sorted({qa.choice_id for qa in question.answers})

    is_correct = set(selected_ids) == set(correct_choice_ids)

    attempt = Attempt(
        user_id=payload.user_id,
        question_id=payload.question_id,
        selected_choice_ids=selected_ids,
        is_correct=is_correct,
    )
    db.add(attempt)
    db.commit()

    correct_labels = sorted([qa.choice.label for qa in question.answers])

    return AttemptResult(
        question_id=question.id,
        user_id=payload.user_id,
        selected_choice_ids=selected_ids,
        is_correct=is_correct,
        correct_choice_ids=correct_choice_ids,
        correct_labels=correct_labels,
        domain=question.domain,
        explanation_en=question.explanation_en,
        explanation_zh=question.explanation_zh,
    )


@router.get("/summary", response_model=AttemptSummary)
def get_attempt_summary(
    user_id: str = Query("local"),
    db: Session = Depends(get_db),
) -> AttemptSummary:
    # total question count
    total_questions = db.execute(select(func.count()).select_from(Question)).scalar_one()

    # load all attempts for this user, newest first
    attempts_stmt = (
        select(Attempt, Question)
        .join(Question, Attempt.question_id == Question.id)
        .where(Attempt.user_id == user_id)
        .order_by(Attempt.created_at.desc(), Attempt.id.desc())
    )
    rows = db.execute(attempts_stmt).all()

    # keep only latest attempt per question
    latest_by_question: dict[int, tuple[Attempt, Question]] = {}
    for attempt, question in rows:
        if attempt.question_id not in latest_by_question:
            latest_by_question[attempt.question_id] = (attempt, question)

    latest_attempts = list(latest_by_question.values())

    total_answered = len(latest_attempts)
    total_correct = sum(1 for attempt, _ in latest_attempts if attempt.is_correct)
    total_incorrect = total_answered - total_correct
    total_unanswered = max(total_questions - total_answered, 0)

    overall_percentage = round((total_correct / total_answered) * 100, 2) if total_answered else 0.0

    domain_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"answered": 0, "correct": 0})
    for attempt, question in latest_attempts:
        domain = question.domain or "Unknown"
        domain_counts[domain]["answered"] += 1
        if attempt.is_correct:
            domain_counts[domain]["correct"] += 1

    by_domain: list[DomainScore] = []
    for domain, counts in sorted(domain_counts.items()):
        answered = counts["answered"]
        correct = counts["correct"]
        incorrect = answered - correct
        percentage = round((correct / answered) * 100, 2) if answered else 0.0

        by_domain.append(
            DomainScore(
                domain=domain,
                answered=answered,
                correct=correct,
                incorrect=incorrect,
                percentage=percentage,
            )
        )

    return AttemptSummary(
        user_id=user_id,
        total_questions=total_questions,
        total_answered=total_answered,
        total_correct=total_correct,
        total_incorrect=total_incorrect,
        total_unanswered=total_unanswered,
        overall_percentage=overall_percentage,
        by_domain=by_domain,
    )
