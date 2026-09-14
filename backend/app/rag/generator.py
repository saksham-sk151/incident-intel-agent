"""
Generation layer: turns retrieved passages into an answer.

If OPENAI_API_KEY or GEMINI_API_KEY is set, this calls that provider to
generate a real, synthesized answer grounded in the retrieved passages.
Without a key, it falls back to an *extractive* answer: the top passages,
clearly cited, stitched into a short summary. This means the project is
honestly demoable with zero secrets, while still leaving a real upgrade
path to a generative model documented for later (interview-defensible: you
can explain exactly what changes when a key is added, because the
retrieval and prompt-construction logic is identical either way).
"""
from typing import List

from app.core.config import OPENAI_API_KEY, GEMINI_API_KEY, GEMINI_MODEL


def _build_prompt(question: str, passages: List[dict]) -> str:
    context = "\n\n".join(
        f"[{i+1}] ({p['source']}): {p['text']}" for i, p in enumerate(passages)
    )
    return (
        "You are a safety intelligence assistant for an industrial plant. "
        "Answer the question using ONLY the numbered context passages below. "
        "Cite passages inline using [n]. If the passages don't contain the "
        "answer, say so plainly.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )


def _extractive_fallback(question: str, passages: List[dict], reason: str = "no LLM key configured") -> str:
    if not passages:
        return "No relevant passages were retrieved for this question."
    lines = [f"Based on the {len(passages)} most relevant retrieved passages "
             f"({reason}, so this is an extractive summary rather "
             f"than a generated one):"]
    for i, p in enumerate(passages):
        tag = "REGULATION" if p["doc_type"] == "regulation" else "INCIDENT"
        lines.append(f"[{i+1}] ({tag} - {p['source']}) {p['text']}")
    return "\n".join(lines)


def _call_openai(prompt: str) -> str | None:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[LLM call failed, falling back to extractive answer: {e}]"


def _call_gemini(prompt: str) -> str | None:
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        resp = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        return resp.text
    except Exception as e:
        return f"[LLM call failed, falling back to extractive answer: {e}]"


def generate_answer(question: str, passages: List[dict]) -> dict:
    prompt = _build_prompt(question, passages)
    mode = "extractive"
    answer = None

    # Gemini checked first: it has a genuinely free tier (no billing account
    # required), which makes it the easier default for a student project.
    # Set OPENAI_API_KEY instead (or as well) to prefer OpenAI.
    if GEMINI_API_KEY:
        answer = _call_gemini(prompt)
        mode = "generative (gemini)"
    elif OPENAI_API_KEY:
        answer = _call_openai(prompt)
        mode = "generative (openai)"

    if not answer or answer.startswith("[LLM call failed"):
        if answer and answer.startswith("[LLM call failed"):
            # Surface the real error so it's obvious *why* generation didn't
            # happen (bad key, quota, network) instead of looking identical
            # to the "no key configured" case.
            answer = _extractive_fallback(question, passages, reason=f"generation failed ({answer})")
        else:
            answer = _extractive_fallback(question, passages)
        mode = "extractive"

    return {
        "answer": answer,
        "mode": mode,
        "citations": [{"n": i + 1, "doc_id": p["doc_id"], "source": p["source"]}
                      for i, p in enumerate(passages)],
    }
