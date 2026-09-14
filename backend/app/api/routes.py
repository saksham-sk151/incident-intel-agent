import json
import time

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import DATA_DIR, TOP_K_DEFAULT
from app.core.db import get_db
from app.models.incident import Incident, IncidentOut, IncidentCreate
from app.rag.retriever import get_retriever
from app.rag.generator import generate_answer
from app.analytics.scoring import compute_recurrence_priority, compute_location_hotspots

router = APIRouter()


# ---------- Incidents CRUD ----------

@router.get("/incidents", response_model=list[IncidentOut])
def list_incidents(
    response: Response,
    category: str | None = None,
    location: str | None = None,
    min_severity: int | None = None,
    search: str | None = None,
    ids: str | None = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Incident)

    if ids:
        # Exact-set lookup (e.g. "show me the reports that were cited in
        # this answer") bypasses the other filters and pagination -- you
        # asked for these specific rows, so that's what you get.
        id_list = [int(x) for x in ids.split(",") if x.strip().isdigit()]
        rows = query.filter(Incident.id.in_(id_list)).all()
        # preserve the caller's requested order rather than DB order
        rows_by_id = {r.id: r for r in rows}
        ordered = [rows_by_id[i] for i in id_list if i in rows_by_id]
        response.headers["X-Total-Count"] = str(len(ordered))
        return ordered

    if category:
        query = query.filter(Incident.category == category)
    if location:
        query = query.filter(Incident.location == location)
    if min_severity is not None:
        query = query.filter(Incident.severity >= min_severity)
    if search:
        query = query.filter(Incident.description.ilike(f"%{search}%"))

    total = query.count()
    response.headers["X-Total-Count"] = str(total)

    rows = (
        query.order_by(Incident.days_ago.asc())
        .offset(offset)
        .limit(min(limit, 100))
        .all()
    )
    return rows


@router.get("/incidents/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/incidents", response_model=IncidentOut, status_code=201)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    incident = Incident(**payload.model_dump())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


# ---------- RAG ask endpoint ----------

class AskRequest(BaseModel):
    question: str
    top_k: int = TOP_K_DEFAULT


class AskResponse(BaseModel):
    question: str
    answer: str
    mode: str
    citations: list[dict]
    retrieved: list[dict]
    latency_ms: float


@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty")

    start = time.perf_counter()
    retriever = get_retriever()
    passages = retriever.retrieve(payload.question, top_k=payload.top_k)
    result = generate_answer(payload.question, passages)
    latency_ms = (time.perf_counter() - start) * 1000

    return AskResponse(
        question=payload.question,
        answer=result["answer"],
        mode=result["mode"],
        citations=result["citations"],
        retrieved=passages,
        latency_ms=round(latency_ms, 2),
    )


# ---------- Analytics ----------

@router.get("/analytics/top-risks")
def top_risks():
    return compute_recurrence_priority()


@router.get("/analytics/hotspots")
def hotspots():
    return compute_location_hotspots()


# ---------- Regulations (read-only reference corpus) ----------

@router.get("/regulations")
def list_regulations():
    path = DATA_DIR / "regulations.json"
    return json.loads(path.read_text())
