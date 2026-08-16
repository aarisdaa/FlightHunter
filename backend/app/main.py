from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine, Base
from app.models import Flight

from app.routes.flights import router as flights_router


app = FastAPI(
    title="FlightHunter API",
    version="1.0.0"
)


Base.metadata.create_all(bind=engine)

app.include_router(flights_router)


@app.get("/")
def root():

    return {
        "message": "FlightHunter API is running!"
    }


@app.get("/health")
def health_check():

    try:

        with engine.connect() as connection:

            connection.execute(text("SELECT 1"))

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