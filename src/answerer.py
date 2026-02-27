"""
answerer.py — Compliance Query Client
======================================
Connects to the Pathway VectorStoreServer, retrieves relevant chunks,
and generates formal compliance responses via Groq Llama-3.3-70B.

Usage:
    python src/answerer.py

Requires:
    - src/main.py server running at http://127.0.0.1:8000
    - GROQ_API_KEY set in .env
"""

import logging
import os
import sys
from typing import Optional

import requests
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
VECTOR_STORE_URL: str = os.getenv("VECTOR_STORE_URL", "http://127.0.0.1:8000/v1/retrieve")
TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "3"))
GROQ_MODEL: str = "llama-3.3-70b-versatile"
LLM_TEMPERATURE: float = 0.1
REQUEST_TIMEOUT: int = 10

SYSTEM_PROMPT: str = (
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def validate_config() -> None:
    """Ensure GROQ_API_KEY is present before starting."""
    if not GROQ_API_KEY:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. Add it to your .env file."
        )


def retrieve_context(question: str, top_k: int = TOP_K) -> list[dict]:
    """
    Query the Pathway VectorStoreServer for the top-k relevant chunks.

    Args:
        question: Natural language compliance query.
        top_k:    Number of chunks to retrieve.

    Returns:
        List of result dicts with 'text', 'dist', and 'metadata'.

    Raises:
        ConnectionError: If the Pathway server is unreachable.
        ValueError:      If the response format is unexpected.
    """
    payload = {"query": question, "k": top_k}
    try:
        response = requests.post(
            VECTOR_STORE_URL, json=payload, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        results = response.json()
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Cannot reach VectorStoreServer at {VECTOR_STORE_URL}. "
            "Ensure src/main.py is running."
        )
    except requests.exceptions.Timeout:
        raise ConnectionError(f"Request timed out after {REQUEST_TIMEOUT}s.")
    except requests.exceptions.HTTPError as exc:
        raise ValueError(f"Server error: {exc}") from exc

    if not isinstance(results, list):
        raise ValueError(f"Unexpected response format: {type(results)}")

    logger.info("Retrieved %d chunks.", len(results))
    return results


def build_context_string(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into a labelled context block for the LLM.

    Args:
        chunks: List of chunk dicts from retrieve_context().

    Returns:
        Formatted string with source attribution per chunk.
    """
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        source = chunk.get("metadata", {}).get("name", "Unknown")
        text = chunk.get("text", "").strip()
        parts.append(f"[Source {i}: {source}]\n{text}")
    return "\n\n---\n\n".join(parts)


def extract_sources(chunks: list[dict]) -> list[str]:
    """
    Extract unique source document names in retrieval order.

    Args:
        chunks: List of chunk dicts from retrieve_context().

    Returns:
        Deduplicated list of source filenames.
    """
    seen: set[str] = set()
    sources: list[str] = []
    for chunk in chunks:
        name = chunk.get("metadata", {}).get("name", "Unknown")
        if name not in seen:
            seen.add(name)
            sources.append(name)
    return sources


def generate_compliance_response(question: str, context: str) -> str:
    """
    Send context + question to Groq and return the compliance response.

    Args:
        question: The user's compliance query.
        context:  Formatted text from retrieved document chunks.

    Returns:
        LLM response string.
    """
    groq_client = Groq(api_key=GROQ_API_KEY)
    completion = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=LLM_TEMPERATURE,
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
    return completion.choices[0].message.content


def get_compliance_answer(
    question: str,
) -> tuple[Optional[list[dict]], str, list[str]]:
    """
    Full pipeline: retrieve → build context → generate response.

    Args:
        question: Natural language compliance query.

    Returns:
        Tuple of (chunks, answer, sources).
        chunks is None if retrieval failed entirely.
    """
    try:
        chunks = retrieve_context(question)
    except (ConnectionError, ValueError) as exc:
        logger.error("Retrieval failed: %s", exc)
        return None, str(exc), []

    context = build_context_string(chunks)
    sources = extract_sources(chunks)

    try:
        answer = generate_compliance_response(question, context)
    except Exception as exc:
        logger.error("LLM generation failed: %s", exc)
        return chunks, f"LLM error: {exc}", sources

    return chunks, answer, sources


def display_semantic_results(chunks: list[dict]) -> None:
    """Print ranked chunk results with similarity scores."""
    print("\n🧠 TOP-K SEMANTIC SEARCH RESULTS (Evidence)")
    print("─" * 55)
    for rank, chunk in enumerate(chunks, start=1):
        similarity = round(1 - chunk.get("dist", 1.0), 4)
        source = chunk.get("metadata", {}).get("name", "Unknown")
        snippet = chunk.get("text", "")[:180].replace("\n", " ")
        print(f"  Rank {rank} | Similarity: {similarity:.4f} | Source: {source}")
        print(f"  Snippet: {snippet}…\n")


def display_citations(sources: list[str]) -> None:
    """Print cited source documents."""
    print("📚 CITATIONS")
    print("─" * 55)
    for source in sources:
        print(f"  ✅ {source}")


def run_demo() -> None:
    """Interactive REPL for querying the compliance agent."""
    validate_config()

    print("\n" + "=" * 60)
    print("  🏦 PATHWAY + GROQ: REAL-TIME COMPLIANCE AGENT")
    print("=" * 60)
    print(f"  Vector Store : {VECTOR_STORE_URL}")
    print(f"  LLM Model    : {GROQ_MODEL}  |  Top-K : {TOP_K}")
    print("=" * 60)
    print("Type 'exit' to quit.\n")

    while True:
        print("─" * 60)
        try:
            query = input("🤖 Compliance Query: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nShutting down. Goodbye!")
            break

        if not query:
            continue
        if query.lower() in {"exit", "quit"}:
            print("Shutting down. Goodbye!")
            break

        print("\n🔍 [1/3] Querying vector store…")
        chunks, answer, sources = get_compliance_answer(query)

        if chunks is None:
            print(f"\n❌ Error: {answer}")
            continue

        print("\n📋 [2/3] COMPLIANCE REPORT")
        print("─" * 55)
        print(answer)

        print("\n[3/3] EVIDENCE & CITATIONS")
        display_semantic_results(chunks)
        display_citations(sources)


if __name__ == "__main__":
    run_demo()
