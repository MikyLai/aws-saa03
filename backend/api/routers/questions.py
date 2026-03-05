from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.db import get_db
from api.models import Question

router = APIRouter(prefix="/questions", tags=["questions"])

@router.get("/")
def get_questions():
    return {"questions": []}

@router.get("/{question_id}")
def get_question(question_id: int):
    return {"question_id": question_id, "content": ""}
