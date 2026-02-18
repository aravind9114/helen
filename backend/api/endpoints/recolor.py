from fastapi import APIRouter, HTTPException
from backend.core.schemas import RecolorRequest
from backend.core.utils import resolve_path
from backend.ai.vision.wall_paint import wall_painter
from backend.services.logging import logger

router = APIRouter()

@router.post("/edit/recolor")
async def recolor_wall(request: RecolorRequest):
    """Recolor wall using OpenCV (Fast)."""
    logger.info(f"Recoloring {request.image_path} to {request.color_hex}")
    try:
        image_path = resolve_path(request.image_path)
        mask_path = resolve_path(request.mask_path)
        
        output_path = wall_painter.recolor_wall(image_path, mask_path, request.color_hex)
        
        return {
            "image_url": f"/generated/{output_path.name}",
            "image_path": str(output_path)
        }
    except Exception as e:
        logger.error(f"Recoloring failed: {e}")
        raise HTTPException(500, str(e))
