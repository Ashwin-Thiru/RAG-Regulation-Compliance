"""
main.py — Pathway Streaming Pipeline Entry Point
=================================================
Starts the real-time compliance RAG server.

Usage:
    python src/main.py

Environment Variables (set in .env):
    GDRIVE_FOLDER_ID         Google Drive folder ID to monitor
    GOOGLE_CREDENTIALS_PATH  Path to service account credentials JSON
    EMBEDDING_MODEL          SentenceTransformer model (default: all-MiniLM-L6-v2)
    EMBEDDING_DEVICE         cuda or cpu (default: cuda)
    VECTOR_STORE_HOST        Server host (default: 127.0.0.1)
    VECTOR_STORE_PORT        Server port (default: 8000)
"""

import logging
import os
import sys

import pathway as pw
from dotenv import load_dotenv
from pathway.xpacks.llm.vector_store import VectorStoreServer

from utils.embeddings import build_embedder
from utils.parser import build_parser

load_dotenv()

GDRIVE_FOLDER_ID: str = os.getenv("GDRIVE_FOLDER_ID", "")
SERVICE_ACCOUNT_FILE: str = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DEVICE: str = os.getenv("EMBEDDING_DEVICE", "cuda")
SERVER_HOST: str = os.getenv("VECTOR_STORE_HOST", "127.0.0.1")
SERVER_PORT: int = int(os.getenv("VECTOR_STORE_PORT", "8000"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("compliance_rag.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def validate_config() -> None:
    """Validate required config before starting. Raises clear errors if missing."""
    if not GDRIVE_FOLDER_ID:
        raise EnvironmentError(
            "GDRIVE_FOLDER_ID is not set. Add it to your .env file."
        )
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(
            f"Credentials not found at '{SERVICE_ACCOUNT_FILE}'. "
            "Set GOOGLE_CREDENTIALS_PATH in your .env file."
        )
    logger.info("Configuration validated successfully.")


def build_pipeline() -> VectorStoreServer:
    """
    Construct the full Pathway streaming RAG pipeline.

    Stages:
        1. Ingest  — Stream files from Google Drive
        2. Parse   — Extract structured chunks via Docling
        3. Map     — Normalize schema for the vector store
        4. Embed   — Generate vectors locally on CUDA
        5. Serve   — Expose a live vector search endpoint

    Returns:
        A configured VectorStoreServer ready to run.
    """
    logger.info("Connecting to Google Drive folder: %s", GDRIVE_FOLDER_ID)
    data_source = pw.io.gdrive.read(
        object_id=GDRIVE_FOLDER_ID,
        service_user_credentials_file=SERVICE_ACCOUNT_FILE,
        with_metadata=True,
        mode="streaming",
    )

    logger.info("Initializing Docling parser.")
    parser = build_parser()
    chunks = (
        data_source
        .select(
            doc_chunks=parser(pw.this.data),
            metadata=pw.this._metadata,
        )
        .flatten(pw.this.doc_chunks)
    )

    documents = chunks.select(
        data=pw.this.doc_chunks[0],
        _metadata=pw.this.metadata,
    )

    logger.info("Loading embedder: %s on %s", EMBEDDING_MODEL, EMBEDDING_DEVICE)
    embedder = build_embedder(model=EMBEDDING_MODEL, device=EMBEDDING_DEVICE)

    logger.info("Pipeline built successfully.")
    return VectorStoreServer(documents, embedder=embedder)


def main() -> None:
    """Entry point: validate config, build pipeline, start server."""
    logger.info("=" * 60)
    logger.info("  Real-Time Compliance RAG — Pathway + Groq")
    logger.info("=" * 60)

    validate_config()
    vector_store = build_pipeline()

    logger.info("Starting server at http://%s:%d", SERVER_HOST, SERVER_PORT)
    logger.info("Listening for Google Drive changes. Press Ctrl+C to stop.")

    vector_store.run_server(host=SERVER_HOST, port=SERVER_PORT)
    pw.run()


if __name__ == "__main__":
    main()
