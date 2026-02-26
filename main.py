import pathway as pw
from pathway.xpacks.llm.parsers import DoclingParser
# Replace the Gemini import with this:
from pathway.xpacks.llm.embedders import SentenceTransformerEmbedder
from pathway.xpacks.llm.vector_store import VectorStoreServer
import os
from dotenv import load_dotenv

load_dotenv()

OBJECT_ID = '1dvtPaHqjlQgQRbeqqi3yMfpOBFWVzDq3'
SERVICE_ACCOUNT_FILE = '/home/ashwin/credentials.json'

def run_compliance_pipeline():
    # 1. Ingest
    data_source = pw.io.gdrive.read(
        object_id=OBJECT_ID,
        service_user_credentials_file=SERVICE_ACCOUNT_FILE,
        with_metadata=True,
        mode="streaming"
    )

    # 2. Parse
    parser = DoclingParser(chunk=True)
    chunks = data_source.select(
        doc_chunks=parser(pw.this.data),
        metadata=pw.this._metadata
    ).flatten(pw.this.doc_chunks)

    # 3. Schema Mapping
    documents = chunks.select(
        data=pw.this.doc_chunks[0],
        _metadata=pw.this.metadata
    )

    # 4. FREE LOCAL EMBEDDER (Uses your CUDA GPU)
    # This replaces the Gemini call entirely. No API key needed.
    embedder = SentenceTransformerEmbedder(
        model="all-MiniLM-L6-v2",
        device="cuda"  # Leveraging your GPU!
    )

    # 5. Store & Serve
    vector_store = VectorStoreServer(
        documents,
        embedder=embedder,
    )

    vector_store.run_server(host="127.0.0.1", port=8000)
    
    print("🚀 Local Compliance RAG is LIVE. No API limits!")
    pw.run()

if __name__ == "__main__":
    run_compliance_pipeline()