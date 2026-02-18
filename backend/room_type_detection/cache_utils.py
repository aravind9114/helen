"""
Utilities for managing Hugging Face cache.
"""
import os
from pathlib import Path
from backend.core.config import settings

def setup_hf_cache():
    """Configure HF cache directory."""
    cache_dir = Path("backend/.hf_cache").resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    os.environ["HF_HOME"] = str(cache_dir)
    return cache_dir

def enable_offline_mode():
    """Force offline mode for HF Hub."""
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
