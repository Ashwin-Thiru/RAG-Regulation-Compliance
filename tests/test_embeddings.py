import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from unittest.mock import patch

class TestGetAvailableDevice:
    def test_cpu_when_cuda_unavailable(self):
        with patch("torch.cuda.is_available", return_value=False), \
             patch("torch.backends.mps.is_available", return_value=False):
            from utils.embeddings import get_available_device
            assert get_available_device("cuda") == "cpu"
    def test_cuda_when_available(self):
        with patch("torch.cuda.is_available", return_value=True), \
             patch("torch.cuda.get_device_name", return_value="RTX 4090"):
            from utils.embeddings import get_available_device
            assert get_available_device("cuda") == "cuda"
    def test_cpu_preferred_returns_cpu(self):
        from utils.embeddings import get_available_device
        assert get_available_device("cpu") == "cpu"
