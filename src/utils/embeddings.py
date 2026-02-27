import logging
import torch
from pathway.xpacks.llm.embedders import SentenceTransformerEmbedder

logger = logging.getLogger(__name__)

def get_available_device(preferred: str = "cuda") -> str:
    """
    Detect best available compute device, falling back gracefully.
    Order: cuda -> mps (Apple Silicon) -> cpu

    Args:
        preferred: Caller's preferred device. Defaults to 'cuda'.

    Returns:
        Device string: 'cuda', 'mps', or 'cpu'.
    """
    if preferred == "cuda" and torch.cuda.is_available():
        logger.info("CUDA available — using GPU: %s", torch.cuda.get_device_name(0))
        return "cuda"
    elif preferred == "mps" and torch.backends.mps.is_available():
        logger.info("MPS (Apple Silicon) available.")
        return "mps"
    else:
        if preferred != "cpu":
            logger.warning("Device '%s' unavailable. Falling back to CPU.", preferred)
        return "cpu"

def build_embedder(
    model: str = "all-MiniLM-L6-v2",
    device: str = "cuda",
) -> SentenceTransformerEmbedder:
    """
    Build a SentenceTransformerEmbedder with automatic device fallback.
    All embeddings computed locally — no data leaves your environment.

    Args:
        model:  SentenceTransformer model name. Defaults to 'all-MiniLM-L6-v2'.
        device: Preferred device ('cuda', 'mps', 'cpu'). Defaults to 'cuda'.

    Returns:
        A configured SentenceTransformerEmbedder instance.
    """
    resolved = get_available_device(preferred=device)
    logger.info("Loading model '%s' on device '%s'.", model, resolved)
    return SentenceTransformerEmbedder(model=model, device=resolved)

__all__ = ["build_embedder", "get_available_device"]
