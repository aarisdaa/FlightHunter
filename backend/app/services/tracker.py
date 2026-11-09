from sqlalchemy.orm import Session

from app.models.watch import Watch, PriceSnapshot
from app.services.provider import get_provider


def refresh_watch(db: Session, watch: Watch) -> PriceSnapshot:
    airline, price = get_provider().quote(watch.origin, watch.destination, watch.departure_date)
    snap = PriceSnapshot(watch_id=watch.id, airline=airline, price=price)
    db.add(snap)
    db.commit()
    db.refresh(snap)
    return snap


def refresh_all(db: Session) -> int:
    from datetime import date
    watches = db.query(Watch).filter(Watch.departure_date >= date.today()).all()
    for w in watches:
        refresh_watch(db, w)
    return len(watches)
