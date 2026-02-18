"""
Configuration file for the FastAPI backend.
Handles environment variables and app settings.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Tokens (optional for online providers)
    replicate_api_token: str | None = None
    hf_api_token: str | None = None
    
    # Storage paths
    # Adjusted base_dir to point to parent of 'core' which is 'backend'
    base_dir: Path = Path(__file__).resolve().parent.parent
    storage_dir: Path = base_dir / "storage"
    uploads_dir: Path = storage_dir / "uploads"
    generated_dir: Path = storage_dir / "generated"
    
    # Model configuration
    diffusers_model: str = "runwayml/stable-diffusion-v1-5"
    image_width: int = 512
    image_height: int = 512
    
    # OPTIMISED SETTINGS FOR ACCURACY & STRUCTURE
    num_inference_steps: int = 35      # Keep high for detail
    guidance_scale: float = 7.0        # Slightly lower to allow more prompt adherence
    img2img_strength: float = 0.58    # Lowered from 0.75 to preserve walls/windows better
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # HARDWARE OPTIMIZATION
    low_vram: bool = True  # Enable 4GB Optimization Mode
    
    # Default Generation Params (Overridden if low_vram is True)
    num_inference_steps: int = 20      # Optimized for speed/memory
    guidance_scale: float = 7.5
    img2img_strength: float = 0.55     # Balance structure/creativity

    # Ollama Settings
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global settings instance
settings = Settings()

# Auto-detect Hardware Profile (STRICT OVERRIDE)
# We do this AFTER loading settings to ensure Hardware > .env
try:
    import torch
    if torch.cuda.is_available():
        vram_bytes = torch.cuda.get_device_properties(0).total_memory
        vram_gb = vram_bytes / (1024**3)
        if vram_gb <= 4.5:
            # Enforce LOW_VRAM for < 4.5GB cards
            settings.low_vram = True
            print(f"[MemoryProfile] LOW_VRAM activated ({vram_gb:.2f}GB)")
        else:
            settings.low_vram = False
            print(f"[MemoryProfile] NORMAL mode activated ({vram_gb:.2f}GB)")
    else:
        settings.low_vram = True
        print("[MemoryProfile] CPU Mode (LOW_VRAM settings applied)")
except Exception as e:
    print(f"[MemoryProfile] Detection failed: {e}")

# Ensure storage directories exist
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.generated_dir.mkdir(parents=True, exist_ok=True)
(settings.storage_dir / "masks").mkdir(parents=True, exist_ok=True)


# Prompt templates (Optimized for Structure Preservation)
PROMPT_TEMPLATE = (
    "raw photo, dslr, soft lighting, "
    "{room_type} interior redesign, {style} style, "
    "high resolution, photorealistic, 8k, "
    "detailed texture, ray tracing, "
    "architectural photography, magazine quality"
)

NEGATIVE_PROMPT = (
    "low quality, blurry, distorted, "
    "cartoon, illustration, painting, cgi, 3d render, "
    "watermark, text, signature, duplicate, "
    "bad anatomy, deformed, disfigured, "
    "oversaturated, high contrast"
)


# Budget estimation rules (based on style)
BUDGET_ESTIMATES = {
    "Minimalist": 150000,
    "Modern": 250000,
    "Vintage": 200000,
    "Professional": 300000,
}
