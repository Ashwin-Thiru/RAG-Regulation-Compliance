Real-Time Compliance RAG
-> An intelligent, streaming RAG (Retrieval-Augmented Generation) pipeline designed for financial institutions to automate the analysis of regulatory documents and audit reports in real-time.

Project Overview
-> Financial regulations change rapidly. Traditional RAG systems suffer from "Indexing Latency"—where the AI is only as smart as the last time you manually updated the database.

-> This project solves that by using Pathway’s streaming connectors to establish a live link with Google Drive. When a compliance officer updates a policy PDF, the AI agent is updated instantly without restarting the system.

Key Features
-> Live Data Sync: Continuous indexing of Google Drive folders.
-> Local Embedding: Powered by SentenceTransformer on CUDA—no data leaves your local environment for vectorization.
-> High-Speed Reasoning: Leverages Groq’s Llama-3.3-70B to provide expert-level compliance analysis.
-> Audit-Ready Citations: Every response includes "Top-K" semantic evidence and document citations for verification.

Technical Architecture
-> Ingestion: pathway.io.gdrive monitors specific Folder/File IDs in streaming mode.
-> Parsing: DoclingParser chunks complex financial PDFs, maintaining structural integrity.
-> Vector Store: Pathway’s unified VectorStoreServer manages embeddings and similarity searches.
-> Inference: A dedicated answerer.py script queries the Pathway server and uses Groq to generate a "Senior Compliance Officer" formatted report.

Example Output
"""
User Question: "What is the current threshold for flagging a single transaction?"

Groq Compliance Report: 
Current Threshold: The current threshold is $5,000. This is a reduction from the 2025 limit of $10,000, as per the AML_Policy_V2_2026.pdf update.

Semantic Evidence:

Rank 1 (Sim: 0.667): AML_Policy_V2_2026.pdf - "Standard Alert Trigger: now lowered to $5,000..."
"""

Problem Statement Addressed
-> Regulatory compliance departments struggle with massive volumes of legal text. This project demonstrates how Pathway can:

Process streaming legal updates.

Index documents continuously.


Provide compliance teams with an LLM interface that has zero-day knowledge of policy changes.
