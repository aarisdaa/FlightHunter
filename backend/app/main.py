import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import engine, Base, SessionLocal
from app import models  # noqa: F401  (registers all tables)
from app.routes.flights import router as flights_router
from app.routes.watches import router as watches_router
from app.services.tracker import refresh_all

Base.metadata.create_all(bind=engine)

REFRESH_MINUTES = int(os.getenv("REFRESH_MINUTES", "60"))  # 0 = disable auto refresh


def _refresh_job():
    db = SessionLocal()
    try:
        refresh_all(db)
    finally:
        db.close()


async def _loop():
    while True:
        await asyncio.sleep(REFRESH_MINUTES * 60)
        try:
            await asyncio.to_thread(_refresh_job)
        except Exception as e:  # keep the loop alive
            print("auto refresh failed:", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_loop()) if REFRESH_MINUTES > 0 else None
    yield
    if task:
        task.cancel()


app = FastAPI(title="FlightHunter API", version="1.1.0", lifespan=lifespan)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

app.include_router(flights_router)
app.include_router(watches_router)


@app.get("/")
def root():
    return {"message": "FlightHunter API is running!"}


@app.get("/config")
def config():
    return {"price_provider": os.getenv("PRICE_PROVIDER", "mock")}


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "detail": str(e)}
