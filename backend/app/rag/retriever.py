"""
Retrieval layer for the Incident Pattern Intelligence Agent.

Uses BM25 (rank_bm25) over a combined corpus of regulatory excerpts and
incident descriptions as the default retriever -- this is a real, standard
information-retrieval baseline (the same "lexical retrieval" half of the
hybrid BM25 + vector search setups described in the hackathon brief), it
needs no API key or model download, and its quality is easy to measure
honestly with recall@k on a held-out question set (see eval.py).

The interface is intentionally pluggable: swap `BM25Retriever` for a dense
embedding retriever (e.g. sentence-transformers + FAISS/Chroma, or an OpenAI
embeddings call) by implementing the same `retrieve(query, top_k)` method --
that upgrade path is documented in the README as a next step.
"""
from dataclasses import dataclass
from typing import List
import json
import re

from rank_bm25 import BM25Okapi

from app.core.config import DATA_DIR


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


@dataclass
class Document:
    doc_id: str
    doc_type: str  # "regulation" | "incident"
    source: str
    text: str
    metadata: dict


class BM25Retriever:
    def __init__(self):
        self.documents: List[Document] = []
        self._bm25 = None
        self._load_corpus()
        self._build_index()

    def _load_corpus(self):
        reg_path = DATA_DIR / "regulations.json"
        inc_path = DATA_DIR / "incidents.json"

        regulations = json.loads(reg_path.read_text())
        for reg in regulations:
            self.documents.append(Document(
                doc_id=reg["id"],
                doc_type="regulation",
                source=reg["source"],
                text=reg["text"],
                metadata={},
            ))

        incidents = json.loads(inc_path.read_text())
        for inc in incidents:
            self.documents.append(Document(
                doc_id=f"incident-{inc['id']}",
                doc_type="incident",
                source=f"Near-miss report #{inc['id']} ({inc['location']})",
                text=inc["description"],
                metadata={
                    "category": inc["category"],
                    "category_label": inc["category_label"],
                    "severity": inc["severity"],
                },
            ))

    def _build_index(self):
        tokenized = [_tokenize(doc.text) for doc in self.documents]
        self._bm25 = BM25Okapi(tokenized)

    def retrieve(self, query: str, top_k: int = 5) -> List[dict]:
        tokenized_query = _tokenize(query)
        scores = self._bm25.get_scores(tokenized_query)
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        results = []
        for idx in ranked:
            doc = self.documents[idx]
            results.append({
                "doc_id": doc.doc_id,
                "doc_type": doc.doc_type,
                "source": doc.source,
                "text": doc.text,
                "score": round(float(scores[idx]), 4),
                "metadata": doc.metadata,
            })
        return results


# Module-level singleton so the index is built once per process.
_retriever_instance: BM25Retriever | None = None


def get_retriever() -> BM25Retriever:
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = BM25Retriever()
    return _retriever_instance
