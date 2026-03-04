from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import health, questions
from api.db import engine
from sqlalchemy import text

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
def read_root():
    return {"message": "AWS SAA-03 Backend API"}

@app.on_event("startup")
def test_connection():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        print("DB connected successfully!")
