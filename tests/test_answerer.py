import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import pytest
from answerer import build_context_string, extract_sources

@pytest.fixture()
def sample_chunks():
    return [
        {"text": "Tier 1 capital ratio minimum is 6% under Basel III.", "dist": 0.08, "metadata": {"name": "basel3.pdf"}},
        {"text": "Leverage ratio requires minimum 3% Tier 1 capital.", "dist": 0.14, "metadata": {"name": "basel3.pdf"}},
        {"text": "GDPR Article 83 fines up to 20M or 4% global turnover.", "dist": 0.22, "metadata": {"name": "gdpr_2023.pdf"}},
    ]

class TestBuildContextString:
    def test_returns_string(self, sample_chunks):
        assert isinstance(build_context_string(sample_chunks), str)
    def test_contains_all_text(self, sample_chunks):
        result = build_context_string(sample_chunks)
        assert "Tier 1 capital" in result
        assert "GDPR Article 83" in result
    def test_includes_source_names(self, sample_chunks):
        result = build_context_string(sample_chunks)
        assert "basel3.pdf" in result
        assert "gdpr_2023.pdf" in result
    def test_empty_returns_empty_string(self):
        assert build_context_string([]) == ""

class TestExtractSources:
    def test_deduplicates(self, sample_chunks):
        assert extract_sources(sample_chunks).count("basel3.pdf") == 1
    def test_preserves_order(self, sample_chunks):
        sources = extract_sources(sample_chunks)
        assert sources[0] == "basel3.pdf"
        assert sources[1] == "gdpr_2023.pdf"
    def test_empty_input(self):
        assert extract_sources([]) == []
    def test_missing_metadata(self):
        assert extract_sources([{"text": "x", "dist": 0.1, "metadata": {}}]) == ["Unknown"]
