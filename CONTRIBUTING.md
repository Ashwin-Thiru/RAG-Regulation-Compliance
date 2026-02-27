# Contributing to Real-Time Compliance RAG

## Getting Started
1. Fork the repo and clone locally
2. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
3. Install deps: `pip install -r requirements.txt && pip install pytest ruff bandit`
4. Copy env file: `cp .env.example .env` and fill in your values

## Before Submitting a PR
Run all checks locally first:
```bash
ruff check src/ tests/   # lint
pytest tests/ -v          # unit tests
bandit -r src/ -ll        # security scan
```

## Commit Message Format
Follow Conventional Commits:
```
feat: add SharePoint document connector
fix: handle empty metadata in extract_sources
test: add unit tests for DoclingParser wrapper
chore: pin dependency versions
docs: update setup instructions
refactor: extract device detection into utils
```

## Good First Issues
Check the Roadmap section in README.md.
Open issues are labelled `good first issue` in the tracker.
