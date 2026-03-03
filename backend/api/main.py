from fastapi import FastAPI
from api.routers import health, questions

app = FastAPI(title="AWS SAA-03 API")

app.include_router(health.router)
app.include_router(questions.router)

@app.get("/")
def read_root():
    return {"message": "AWS SAA-03 Backend API"}
