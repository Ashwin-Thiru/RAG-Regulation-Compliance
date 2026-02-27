# 🛡 Real-Time Compliance Agent

## 🚨 Problem: Compliance Latency Gap

Financial regulations change overnight.

Example:
In 2026, AML threshold changed from **$10,000 → $5,000**.

Traditional RAG systems:
- Require full re-indexing
- Experience downtime
- Return outdated answers

In compliance systems, outdated knowledge = financial risk.

---

## ⚡ Solution: Streaming RAG

This system transforms static indexing into **real-time intelligence**.

### 🔄 Live Google Drive Monitoring
- Uses `pathway.io.gdrive`
- Streams document updates instantly
- No full re-indexing required

### ⚙ Incremental Indexing
- Only modified segments are re-embedded
- Zero downtime
- Updates within seconds

---

## 🔐 Privacy-First Architecture

- Local CUDA GPU embeddings (`all-MiniLM-L6-v2`)
- No external embedding API calls
- Zero indexing cost
- Sensitive audit data never leaves environment

---

## 🧠 Financial Intelligence Layer

- Structured parsing using `DoclingParser`
- Groq Llama 3.3 70B acts as Senior Auditor
- Highlights key thresholds in bold
- Provides Top-K evidence with similarity scores
- Includes document citations (e.g., AML_Policy_V2_2026.pdf)

---

## 📊 Validated Results

During live audit testing:

- ₹ 8.59 crore irregularities identified
    - ₹ 6.42 crore excess payments
    - ₹ 2.17 crore statutory recovery failures

All responses include:
- Source citation
- Similarity score
- Evidence-backed transparency

---

## 🏗 Architecture

Google Drive (Streaming Source)
→ Pathway Connector
→ DoclingParser
→ SentenceTransformer (CUDA GPU)
→ VectorStoreServer
→ Groq Llama 3.3 70B
→ Evidence-Backed Audit Report

---

## 🚀 How to Run

```bash
pip install -r requirements.txt
python main.py
```

---

## 🎯 Competitive Advantage

| Feature | Traditional RAG | This Project |
|----------|----------------|--------------|
| Real-time updates | ❌ | ✅ |
| Incremental indexing | ❌ | ✅ |
| Zero downtime | ❌ | ✅ |
| Local GPU embedding | ❌ | ✅ |
| Evidence citations | Partial | ✅ |

---

## 🔮 Future Enhancements

- Compliance change detection alerts
- Slack/Email integration
- Risk scoring engine
- Multi-source ingestion (S3, SharePoint)
