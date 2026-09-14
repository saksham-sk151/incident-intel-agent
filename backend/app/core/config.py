import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# SQLite by default so the project runs with zero setup. Swap DATABASE_URL to a
# Postgres DSN (e.g. postgresql+psycopg2://user:pass@host/db) for a production-style
# deployment -- the SQLAlchemy models are database-agnostic.
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR / 'incident_intel.db'}")

# Optional: set one of these to enable real LLM-generated (not just extractive)
# answers. Without a key, the /ask endpoint still works and returns a cited,
# extractive answer built from the top-retrieved passages -- so the system is
# fully runnable and demoable with no secrets required.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Google deprecates specific Gemini model names faster than any doc (including
# this one) stays current -- if you see a "model X is no longer available"
# error, set GEMINI_MODEL to whatever name the error message recommends
# instead of editing code, e.g.: export GEMINI_MODEL="gemini-X-flash"
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")

TOP_K_DEFAULT = int(os.environ.get("TOP_K_DEFAULT", "5"))
