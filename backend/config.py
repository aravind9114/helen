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
    base_dir: Path = Path(__file__).parent
    storage_dir: Path = base_dir / "storage"
    uploads_dir: Path = storage_dir / "uploads"
    generated_dir: Path = storage_dir / "generated"
    
    # Model configuration
    diffusers_model: str = "runwayml/stable-diffusion-v1-5"
    image_width: int = 512
    image_height: int = 512
    
    # OPTIMISED SETTINGS FOR ACCURACY & STRUCTURE
    num_inference_steps: int = 50     # Keep high for detail
    guidance_scale: float = 6.0        # Slightly lower to allow more prompt adherence
    img2img_strength: float = 0.58    # Lowered from 0.75 to preserve walls/windows better
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global settings instance
settings = Settings()

# Ensure storage directories exist
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.generated_dir.mkdir(parents=True, exist_ok=True)


# Prompt templates (Optimized for Structure Preservation)
# Removed "wide angle", Added "preserve structure"
PROMPT_TEMPLATE = (
    "photorealistic {room_type} interior redesign, {style} style, "
    "preserve room structure and walls, keep same layout and same wall color, "
    "replace all existing furniture with {style} furniture, "
    "new bed, new side tables, new decor, different furniture design, "
    "architectural photography, natural lighting, highly detailed"
)


# Negative prompts to prevent architectural hallucinations
NEGATIVE_PROMPT = (
    "changing walls, changing windows, different layout, architectural changes, "
    "same old furniture, old bed, duplicate furniture, "
    "low quality, distorted, blurry, cartoon, sketch"
)


# Budget estimation rules (based on style)
BUDGET_ESTIMATES = {
    "Minimalist": 150000,
    "Modern": 250000,
    "Vintage": 200000,
    "Professional": 300000,
}
