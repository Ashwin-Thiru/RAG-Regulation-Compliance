"""
api.py — FastAPI Backend with SSE Streaming
============================================
Provides REST + Server-Sent Events endpoints for the React UI.

Endpoints:
    GET  /api/health      — Pipeline + Groq status check
    GET  /api/documents   — List indexed documents from vector store
    POST /api/query       — SSE stream: steps + token-by-token answer

Usage:
    uvicorn src.api:app --host 0.0.0.0 --port 8080 --reload
"""

import json
import logging
import os
import time as _time
from typing import AsyncGenerator

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from groq import Groq
from pydantic import BaseModel

load_dotenv()

GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
VECTOR_STORE_URL: str = os.getenv("VECTOR_STORE_URL", "http://127.0.0.1:8000/v1/retrieve")
VECTOR_STORE_STATS_URL: str = os.getenv("VECTOR_STORE_STATS_URL", "http://127.0.0.1:8000/v1/statistics")
TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "3"))
GROQ_MODEL: str = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You are a Senior Financial Audit & Compliance Officer with deep expertise "
    "in regulatory frameworks (Basel III/IV, SEC, GDPR, SEBI, FINRA). "
    "Answer compliance questions with precision and professionalism.\n\n"
    "Guidelines:\n"
    "- Base answers strictly on provided context. Do not speculate.\n"
    "- Bold key thresholds, percentages, and deadlines using **markdown**.\n"
    "- State clearly if context is insufficient to answer.\n"
    "- Cite specific document sections or regulation numbers where visible.\n"
    "- Flag contradictions or ambiguities between source documents.\n"
    "- Use formal, jurisdiction-appropriate language."
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Compliance RAG API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


def retrieve_chunks(question: str, top_k: int = TOP_K) -> list[dict]:
    payload = {"query": question, "k": top_k}
    response = requests.post(VECTOR_STORE_URL, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def sse_event(event_type: str, data: dict) -> str:
    """Format a Server-Sent Event string."""
    return f"data: {json.dumps({'type': event_type, **data})}\n\n"


@app.get("/api/health")
def health():
    """Check if Pathway vector store and Groq are reachable."""
    pathway_ok = False
    groq_ok = bool(GROQ_API_KEY)

    try:
        r = requests.get(VECTOR_STORE_STATS_URL, timeout=3)
        pathway_ok = r.status_code == 200
    except Exception:
        pathway_ok = False

    return {
        "pathway": pathway_ok,
        "groq": groq_ok,
        "model": GROQ_MODEL,
    }


@app.get("/api/documents")
def list_documents():
    """Return list of documents currently indexed in the vector store."""
    try:
        # Query with a generic term to get all docs and extract unique sources
        payload = {"query": "regulation compliance audit", "k": 50}
        r = requests.post(VECTOR_STORE_URL, json=payload, timeout=10)
        r.raise_for_status()
        chunks = r.json()

        seen = set()
        docs = []
        for chunk in chunks:
            name = chunk.get("metadata", {}).get("name", "Unknown")
            if name not in seen:
                seen.add(name)
                docs.append({"name": name, "chunks": 0})

        # Count chunks per doc
        for chunk in chunks:
            name = chunk.get("metadata", {}).get("name", "Unknown")
            for doc in docs:
                if doc["name"] == name:
                    doc["chunks"] += 1

        return {"documents": docs, "total": len(docs)}
    except Exception as e:
        return {"documents": [], "total": 0, "error": str(e)}


async def stream_query(question: str) -> AsyncGenerator[str, None]:
    """
    SSE generator — every event fires immediately after the REAL operation completes.
    No fake delays. Timing shown in UI reflects actual system performance.

    Event flow:
        step(embed, active)   → real encode call → step(embed, done, ms)
        step(retrieve, active) → real HTTP to vector store → step(retrieve, done, ms)
        chunk(rank, source, similarity, snippet) × N   ← real chunk data
        step(llm, active)     → real Groq stream opens → step(llm, done, ms)
        token(text) × N       ← real streamed tokens from Groq
        sources([...])        ← final citation list
        done()
    """

    # ── Step 1: Embed query ─────────────────────────────────────────────────
    # The vector store embeds the query internally when we POST to /v1/retrieve.
    # We fire "active" right before the HTTP request, "done" right after — so
    # the timing the user sees is the REAL round-trip to the vector store.
    yield sse_event("step", {
        "id": "embed",
        "status": "active",
        "label": "Embedding query into vector space..."
    })

    # ── Step 2: Retrieve from vector store ──────────────────────────────────
    # Single HTTP call to Pathway — embeds the query AND retrieves top-k.
    # We fire "retrieve active" before the call, capture real elapsed time.
    yield sse_event("step", {
        "id": "retrieve",
        "status": "active",
        "label": f"Searching live vector index (top-{TOP_K})..."
    })

    t0 = _time.perf_counter()
    try:
        chunks = retrieve_chunks(question)
    except Exception as e:
        yield sse_event("error", {"message": f"Vector store unreachable: {e}"})
        return
    elapsed_retrieve = round((_time.perf_counter() - t0) * 1000)  # real ms

    # Both embed + retrieve done — report real elapsed time
    yield sse_event("step", {
        "id": "embed",
        "status": "done",
        "label": "Query embedded",
        "ms": elapsed_retrieve   # same round-trip covers both
    })
    yield sse_event("step", {
        "id": "retrieve",
        "status": "done",
        "label": f"Retrieved {len(chunks)} chunks",
        "ms": elapsed_retrieve
    })

    # ── Step 3: Surface each real chunk immediately ─────────────────────────
    # No loop delay — each chunk event fires as soon as we process that chunk.
    sources_list = []
    seen_sources: set[str] = set()
    context_parts = []

    for i, chunk in enumerate(chunks, start=1):
        source = chunk.get("metadata", {}).get("name", "Unknown")
        text = chunk.get("text", "").strip()
        similarity = round(1 - chunk.get("dist", 1.0), 4)
        snippet = text[:160].replace("\n", " ")

        # Fire immediately — this is real data, no sleep
        yield sse_event("chunk", {
            "rank": i,
            "source": source,
            "similarity": similarity,
            "snippet": snippet
        })

        context_parts.append(f"[Source {i}: {source}]\n{text}")
        if source not in seen_sources:
            seen_sources.add(source)
            sources_list.append({"name": source, "similarity": similarity})

    context = "\n\n---\n\n".join(context_parts)

    # ── Step 4: Open Groq stream ─────────────────────────────────────────────
    # Fire "active" before the API call. "done" fires the moment the first
    # token arrives — that's the real TTFT (time-to-first-token) from Groq.
    yield sse_event("step", {
        "id": "llm",
        "status": "active",
        "label": f"Connecting to {GROQ_MODEL} via Groq..."
    })

    t1 = _time.perf_counter()
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        stream = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=0.1,
            stream=True,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"RETRIEVED CONTEXT:\n{context}\n\n"
                        f"COMPLIANCE QUESTION: {question}"
                    ),
                },
            ],
        )
    except Exception as e:
        yield sse_event("error", {"message": f"Groq connection failed: {e}"})
        return

    # ── Step 5: Stream real tokens ───────────────────────────────────────────
    first_token = True
    for chunk_data in stream:
        token = chunk_data.choices[0].delta.content
        if token:
            if first_token:
                # "done" fires on REAL first token — actual TTFT
                elapsed_ttft = round((_time.perf_counter() - t1) * 1000)
                yield sse_event("step", {
                    "id": "llm",
                    "status": "done",
                    "label": "Streaming response...",
                    "ms": elapsed_ttft
                })
                first_token = False
            yield sse_event("token", {"text": token})

    # ── Done ─────────────────────────────────────────────────────────────────
    yield sse_event("sources", {"sources": sources_list})
    yield sse_event("done", {})


@app.post("/api/query")
async def query_endpoint(body: QueryRequest):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured.")

    return StreamingResponse(
        stream_query(body.question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
