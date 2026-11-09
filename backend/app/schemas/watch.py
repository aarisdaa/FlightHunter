from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, field_validator


class WatchCreate(BaseModel):
    origin: str
    destination: str
    departure_date: date
    target_price: Optional[Decimal] = None
    currency: str = "THB"

    @field_validator("origin", "destination")
    @classmethod
    def iata(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) != 3 or not v.isalpha():
            raise ValueError("Use a 3-letter airport code, e.g. BKK")
        return v

    @field_validator("departure_date")
    @classmethod
    def not_past(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Departure date cannot be in the past")
        return v

    @field_validator("target_price")
    @classmethod
    def positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Target price must be greater than 0")
        return v


class SnapshotResponse(BaseModel):
    id: int
    airline: str
    price: Decimal
    checked_at: datetime

    class Config:
        from_attributes = True


class WatchResponse(BaseModel):
    id: int
    origin: str
    destination: str
    departure_date: date
    target_price: Optional[Decimal]
    currency: str
    created_at: datetime
    airline: Optional[str] = None
    latest_price: Optional[Decimal] = None
    lowest_price: Optional[Decimal] = None
    highest_price: Optional[Decimal] = None
    change_pct: Optional[float] = None
    below_target: bool = False
    checks: int = 0
    history: List[SnapshotResponse] = []
