from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Flight(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True)

    airline = Column(String(100), nullable=False)

    origin = Column(String(10), nullable=False)

    destination = Column(String(10), nullable=False)

    departure_date = Column(DateTime, nullable=False)

    price = Column(Numeric(10, 2), nullable=False)

    currency = Column(String(3), default="THB")

    created_at = Column(
        DateTime,
        server_default=func.now()
    )