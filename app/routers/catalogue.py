"""Public catalogue: services, districts and nearest MeeSeva centres."""
from math import asin, cos, radians, sin, sqrt

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.assistant import score_services, service_card
from app.database import get_db
from app.models import Centre, District, Service

router = APIRouter(prefix="/api", tags=["catalogue"])


@router.get("/services")
def list_services(lang: str = "en", q: str = "", category: str = "", db: Session = Depends(get_db)):
    """All services, or those matching a search in any of the four languages."""
    if q.strip():
        svcs = [s for s, _ in score_services(db, q)]
    else:
        svcs = db.query(Service).order_by(Service.category, Service.name_en).all()
    if category:
        svcs = [s for s in svcs if s.category == category]
    return [{"id": s.id, "code": s.code, "name": s.name(lang), "name_en": s.name_en,
             "category": s.category, "fee_inr": s.fee_inr, "sla_days": s.sla_days} for s in svcs]


@router.get("/services/{service_id}")
def get_service(service_id: int, lang: str = "en", db: Session = Depends(get_db)):
    svc = db.get(Service, service_id)
    if not svc:
        raise HTTPException(404, "Service not found")
    return service_card(svc, lang) | {"description": svc.description_en}


@router.get("/districts")
def districts(db: Session = Depends(get_db)):
    return [{"id": d.id, "name_en": d.name_en, "name_te": d.name_te}
            for d in db.query(District).order_by(District.name_en)]


def _km(lat1, lng1, lat2, lng2) -> float:
    """Great-circle distance (haversine), in km."""
    dlat, dlng = radians(lat2 - lat1), radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return 6371 * 2 * asin(sqrt(a))


@router.get("/centres")
def centres(district_id: int | None = None, lat: float | None = Query(None, ge=-90, le=90),
            lng: float | None = Query(None, ge=-180, le=180), limit: int = Query(5, ge=1, le=20),
            db: Session = Depends(get_db)):
    """Nearest centres to the citizen's location, or the centres in a district."""
    qry = db.query(Centre)
    if district_id:
        qry = qry.filter(Centre.district_id == district_id)
    rows = []
    for c in qry.all():
        dist = round(_km(lat, lng, c.lat, c.lng), 1) if lat is not None and lng is not None else None
        rows.append({"id": c.id, "name": c.name, "address": c.address, "district": c.district.name_en,
                     "open_hours": c.open_hours, "lat": c.lat, "lng": c.lng, "distance_km": dist,
                     "map_url": f"https://www.google.com/maps/search/?api=1&query={c.lat},{c.lng}"})
    rows.sort(key=lambda r: (r["distance_km"] is None, r["distance_km"] or 0, r["name"]))
    return rows[:limit]
