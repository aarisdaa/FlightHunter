from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Watch(Base):
    """A route + date the user wants to track."""
    __tablename__ = "watches"

    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String(3), nullable=False)
    destination = Column(String(3), nullable=False)
    departure_date = Column(Date, nullable=False)
    target_price = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default="THB")
    created_at = Column(DateTime, server_default=func.now())

    snapshots = relationship(
        "PriceSnapshot",
        back_populates="watch",
        cascade="all, delete-orphan",
        order_by="PriceSnapshot.checked_at",
    )


class PriceSnapshot(Base):
    """One price check for a watch (the price history)."""
    __tablename__ = "price_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    watch_id = Column(Integer, ForeignKey("watches.id", ondelete="CASCADE"), index=True, nullable=False)
    airline = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    checked_at = Column(DateTime, server_default=func.now())

    watch = relationship("Watch", back_populates="snapshots")
