from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.watch import Watch
from app.schemas.watch import WatchCreate, WatchResponse, SnapshotResponse
from app.services.stats import summarize
from app.services.tracker import refresh_watch

router = APIRouter(prefix="/watches", tags=["Watches"])


def to_response(w: Watch) -> dict:
    snaps = w.snapshots
    data = {
        "id": w.id, "origin": w.origin, "destination": w.destination,
        "departure_date": w.departure_date, "target_price": w.target_price,
        "currency": w.currency, "created_at": w.created_at,
        "airline": snaps[-1].airline if snaps else None,
        "history": snaps,
    }
    data.update(summarize([s.price for s in snaps], w.target_price))
    return data


def get_or_404(db: Session, watch_id: int) -> Watch:
    w = db.query(Watch).filter(Watch.id == watch_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Watch not found")
    return w


@router.post("/", response_model=WatchResponse, status_code=201)
def create_watch(payload: WatchCreate, db: Session = Depends(get_db)):
    if payload.origin == payload.destination:
        raise HTTPException(status_code=422, detail="Origin and destination must differ")
    w = Watch(**payload.model_dump())
    db.add(w)
    db.commit()
    db.refresh(w)
    refresh_watch(db, w)          # first price check right away
    db.refresh(w)
    return to_response(w)


@router.get("/", response_model=list[WatchResponse])
def list_watches(db: Session = Depends(get_db)):
    return [to_response(w) for w in db.query(Watch).order_by(Watch.departure_date).all()]


@router.get("/{watch_id}", response_model=WatchResponse)
def get_watch(watch_id: int, db: Session = Depends(get_db)):
    return to_response(get_or_404(db, watch_id))


@router.get("/{watch_id}/history", response_model=list[SnapshotResponse])
def get_history(watch_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, watch_id).snapshots


@router.post("/{watch_id}/refresh", response_model=WatchResponse)
def refresh(watch_id: int, db: Session = Depends(get_db)):
    w = get_or_404(db, watch_id)
    refresh_watch(db, w)
    db.refresh(w)
    return to_response(w)


@router.delete("/{watch_id}")
def delete_watch(watch_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, watch_id))
    db.commit()
    return {"message": "Watch deleted successfully"}
