from dotenv import load_dotenv

load_dotenv()

from api.db import engine
from api.models import Base
from api.routers import health, questions
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="AWS SAA-03 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(questions.router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "AWS SAA-03 Backend API"}


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
