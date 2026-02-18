"""
Global GPU Memory Manager.
Ensures only one heavy model is loaded on VRAM at a time.
"""
import torch
import gc
from typing import Any, Optional
from backend.services.logging import logger
from backend.core.config import settings

class MemoryManager:
    """Manages GPU resources to prevent OOM on 4GB cards."""
    
    _current_model: Optional[str] = None
    _loaded_models: dict = {}

    @classmethod
    def register_model(cls, name: str, model_instance: Any):
        """Keep track of a loaded model instance."""
        cls._loaded_models[name] = model_instance
        cls._current_model = name
        logger.info(f"MemoryManager: Registered {name}")

    @classmethod
    def offload_all(cls, force: bool = False):
        """Move all tracked models to CPU and clear cache."""
        if not cls._loaded_models:
            return

        # STRICT GUARD: Never offload in NORMAL mode unless forced
        if not settings.low_vram and not force:
            return

        logger.info(f"MemoryManager: Offloading all models (Low VRAM: {settings.low_vram}, Forced: {force})...")
        
        for name, model in cls._loaded_models.items():
            try:
                if hasattr(model, "to"):
                    model.to("cpu")
                elif hasattr(model, "cpu"):
                    model.cpu()
                logger.debug(f"Offloaded {name}")
            except Exception as e:
                logger.warning(f"Failed to offload {name}: {e}")

        cls._loaded_models.clear()
        cls._current_model = None
        
        cls.force_cleanup()

    @classmethod
    def ensure_gpu(cls, name: str):
        """
        Ensure strict sequential execution.
        """
        if cls._current_model == name:
            return

        if cls._current_model is not None:
            # LOW_VRAM: Enforce strict switching (Offload previous)
            if settings.low_vram:
                logger.info(f"MemoryManager: Switching {cls._current_model} -> {name}")
                cls.offload_all()
            else:
                # NORMAL MODE: Do NOT offload. Allow models to coexist on GPU.
                pass
        
        cls._current_model = name
        # The caller is responsible for actually moving their model to CUDA
        # This method just ensures the SLOT is free.

    @classmethod
    def force_cleanup(cls):
        """Aggressive VRAM cleanup."""
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        logger.debug("MemoryManager: VRAM Flushed")

memory_manager = MemoryManager()
