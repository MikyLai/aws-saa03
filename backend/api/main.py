import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from api.db import engine  # noqa: E402
from api.models import Base  # noqa: E402
from api.routers import health, questions  # noqa: E402

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


# @app.on_event("startup")
# def create_tables() -> None:
#     Base.metadata.create_all(bind=engine)
