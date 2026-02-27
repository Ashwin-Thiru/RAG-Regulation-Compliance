import logging
from pathway.xpacks.llm.parsers import DoclingParser

logger = logging.getLogger(__name__)

def build_parser(chunk: bool = True) -> DoclingParser:
    """
    Build and return a DoclingParser configured for regulatory PDFs.
    Handles multi-column layouts, nested tables, footnotes, and cross-references.

    Args:
        chunk: Split documents into semantic passages. Defaults to True.

    Returns:
        A configured DoclingParser instance.
    """
    logger.info("Building Docling parser (chunk=%s).", chunk)
    return DoclingParser(chunk=chunk)

__all__ = ["build_parser"]
