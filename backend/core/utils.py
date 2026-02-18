from pathlib import Path
from fastapi import HTTPException
from backend.core.config import settings
from backend.services.logging import logger

def resolve_path(path_str: str) -> Path:
    """Find file in known directories."""
    clean_name = Path(path_str).name
    
    # Check absolute path first if provided
    if Path(path_str).exists():
        return Path(path_str).resolve()
        
    # Check candidates
    candidates = [
        # Images
        settings.uploads_dir / clean_name,
        Path("storage/uploads") / clean_name,
        settings.generated_dir / clean_name,
        Path("storage/generated") / clean_name,
        # Masks
        settings.storage_dir / "masks" / clean_name,
        Path("storage/masks") / clean_name,
        # Legacy/Misc
        Path("uploads") / clean_name,
        Path("backend/storage/uploads") / clean_name,
    ]
    
    for p in candidates:
        if p.exists():
            return p.resolve()
            
    # Raise 404 if not found
    logger.error(f"File not found: {path_str}. Checked: {[str(c) for c in candidates]}")
    raise HTTPException(404, f"File not found: {path_str}")
