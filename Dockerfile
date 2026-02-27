FROM python:3.11-slim AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runtime
LABEL org.opencontainers.image.title="Real-Time Compliance RAG"
LABEL org.opencontainers.image.description="Streaming regulatory intelligence with Pathway & Groq"
LABEL org.opencontainers.image.licenses="MIT"
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /install /usr/local
COPY src/ ./src/
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000', timeout=5)" || exit 1
CMD ["python", "src/main.py"]
