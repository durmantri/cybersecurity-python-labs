from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from labs.lab03.config import APP_DESCRIPTION, APP_TITLE
from labs.lab03.database import initialize_database
from labs.lab03.routers import categories, records
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекст життєвого циклу: ініціалізація бази даних під час запуску сервера."""

    initialize_database()
    yield


app = FastAPI(
    title=f"{APP_TITLE}. Варіант: {VARIANT_NUMBER}",
    description=APP_DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/ping", tags=["System"])
def ping():
    """Перевірка доступності API."""
    return {"status": "ok"}


@app.get("/student", tags=["System"])
def get_student_info():
    """Повертає дані студента із shared/student.py."""
    return {
        "student_name": STUDENT_NAME,
        "group_name": GROUP_NAME,
        "variant_number": VARIANT_NUMBER,
    }


app.include_router(categories.router)
app.include_router(records.router)


if __name__ == "__main__":
    uvicorn.run(
        "labs.lab03.main:app", host="127.0.0.1", port=8000, reload=True, log_config=None
    )
