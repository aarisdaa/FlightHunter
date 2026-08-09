from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine


app = FastAPI(
    title="FlightHunter API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "FlightHunter API is running!"
    }


@app.get("/health")
def health_check():

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT 1")
            )

            result.fetchone()

        return {
            "status": "ok",
            "database": "connected"
        }

    except Exception as e:

        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(e)
        }