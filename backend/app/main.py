import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import DATA_DIR
from app.core.db import Base, engine, SessionLocal
from app.models.incident import Incident
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_db_if_empty()
    yield


app = FastAPI(
    title="Incident Pattern Intelligence Agent",
    description=(
        "A RAG-powered safety intelligence API: answers questions over "
        "near-miss reports and industrial safety regulations with cited "
        "sources, plus a severity/recency-weighted recurrence analytics "
        "layer. Synthetic demo data -- see README for provenance."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo project; restrict this in a real deployment
    allow_methods=["*"],
    allow_headers=["*"],
    # Browsers hide all but a handful of "safe" response headers from
    # fetch()/XHR unless the server explicitly opts in via CORS -- without
    # this, X-Total-Count is visible to curl (no CORS involved) but silently
    # null to frontend JS, which is exactly the bug that broke pagination.
    expose_headers=["X-Total-Count"],
)


def seed_db_if_empty():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Incident).count() == 0:
            data = json.loads((DATA_DIR / "incidents.json").read_text())
            for row in data:
                db.add(Incident(
                    id=row["id"],
                    category=row["category"],
                    category_label=row["category_label"],
                    location=row["location"],
                    description=row["description"],
                    severity=row["severity"],
                    outcome=row["outcome"],
                    days_ago=row["days_ago"],
                ))
            db.commit()
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(router, prefix="/api")
