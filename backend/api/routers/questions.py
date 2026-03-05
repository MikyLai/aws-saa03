# backend/api/routers/questions.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from api.db import get_db
from api.models import Question, Choice, QuestionAnswer
from api.schemas import QuestionCreate, QuestionOut

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/", response_model=list[QuestionOut])
def list_questions(db: Session = Depends(get_db)):
    stmt = (
        select(Question)
        .options(selectinload(Question.choices), selectinload(Question.answers).selectinload(QuestionAnswer.choice))
        .order_by(Question.id.asc())
    )
    questions = db.execute(stmt).scalars().all()

    out: list[QuestionOut] = []
    for q in questions:
        answer_labels = [qa.choice.label for qa in q.answers]
        item = QuestionOut.model_validate(q)
        item.answer_labels = sorted(answer_labels)
        out.append(item)
    return out


@router.get("/{question_id}", response_model=QuestionOut)
def get_question(question_id: int, db: Session = Depends(get_db)):
    stmt = (
        select(Question)
        .where(Question.id == question_id)
        .options(selectinload(Question.choices), selectinload(Question.answers).selectinload(QuestionAnswer.choice))
    )
    q = db.execute(stmt).scalars().first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    item = QuestionOut.model_validate(q)
    item.answer_labels = sorted([qa.choice.label for qa in q.answers])
    return item


@router.post("/", response_model=QuestionOut, status_code=status.HTTP_201_CREATED)
def create_question(payload: QuestionCreate, db: Session = Depends(get_db)):
    # 1) create Question
    q = Question(
        stem=payload.stem,
        explanation=payload.explanation,
        difficulty=payload.difficulty,
        domain=payload.domain,
        question_type=payload.question_type,
        active=payload.active,
    )
    db.add(q)
    db.flush()  # get q.id

    # 2) create choices
    label_to_choice: dict[str, Choice] = {}
    for c in payload.choices:
        choice = Choice(question_id=q.id, label=c.label.strip(), text=c.text)
        db.add(choice)
        db.flush()  # get choice.id
        label_to_choice[choice.label] = choice

    # 3) validate answers
    wanted = [a.strip() for a in payload.answers]
    missing = [a for a in wanted if a not in label_to_choice]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Answer label(s) not found in choices: {missing}",
        )

    # if single, enforce 1 answer
    if payload.question_type == "single" and len(wanted) != 1:
        raise HTTPException(status_code=400, detail="Single-choice question must have exactly 1 answer")

    # 4) create answer mapping rows
    for label in set(wanted):
        db.add(QuestionAnswer(question_id=q.id, choice_id=label_to_choice[label].id))

    db.commit()

    # reload with relationships for response
    stmt = (
        select(Question)
        .where(Question.id == q.id)
        .options(selectinload(Question.choices), selectinload(Question.answers).selectinload(QuestionAnswer.choice))
    )
    q2 = db.execute(stmt).scalars().first()
    item = QuestionOut.model_validate(q2)
    item.answer_labels = sorted([qa.choice.label for qa in q2.answers])
    return item