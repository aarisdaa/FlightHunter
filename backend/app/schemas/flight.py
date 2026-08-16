from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class FlightCreate(BaseModel):
    airline: str
    origin: str
    destination: str
    departure_date: datetime
    price: Decimal
    currency: str = "THB"


class FlightResponse(FlightCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True