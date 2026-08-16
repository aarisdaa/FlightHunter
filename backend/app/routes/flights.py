from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.flight import Flight
from app.schemas.flight import FlightCreate, FlightResponse


router = APIRouter(
    prefix="/flights",
    tags=["Flights"]
)


@router.post("/", response_model=FlightResponse)
def create_flight(
    flight: FlightCreate,
    db: Session = Depends(get_db)
):

    new_flight = Flight(
        airline=flight.airline,
        origin=flight.origin,
        destination=flight.destination,
        departure_date=flight.departure_date,
        price=flight.price,
        currency=flight.currency
    )

    db.add(new_flight)
    db.commit()
    db.refresh(new_flight)

    return new_flight


@router.get("/", response_model=list[FlightResponse])
def get_flights(
    db: Session = Depends(get_db)
):

    return db.query(Flight).all()


@router.get("/{flight_id}", response_model=FlightResponse)
def get_flight(
    flight_id: int,
    db: Session = Depends(get_db)
):

    flight = db.query(Flight).filter(
        Flight.id == flight_id
    ).first()

    if not flight:
        raise HTTPException(
            status_code=404,
            detail="Flight not found"
        )

    return flight

@router.put("/{flight_id}", response_model=FlightResponse)
def update_flight(
    flight_id: int,
    flight_data: FlightCreate,
    db: Session = Depends(get_db)
):
    flight = db.query(Flight).filter(
        Flight.id == flight_id
    ).first()

    if not flight:
        raise HTTPException(
            status_code=404,
            detail="Flight not found"
        )

    flight.airline = flight_data.airline
    flight.origin = flight_data.origin
    flight.destination = flight_data.destination
    flight.departure_date = flight_data.departure_date
    flight.price = flight_data.price
    flight.currency = flight_data.currency

    db.commit()
    db.refresh(flight)

    return flight


@router.delete("/{flight_id}")
def delete_flight(
    flight_id: int,
    db: Session = Depends(get_db)
):
    flight = db.query(Flight).filter(
        Flight.id == flight_id
    ).first()

    if not flight:
        raise HTTPException(
            status_code=404,
            detail="Flight not found"
        )

    db.delete(flight)
    db.commit()

    return {
        "message": "Flight deleted successfully"
    }