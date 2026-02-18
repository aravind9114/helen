from fastapi import APIRouter, HTTPException
from backend.core.schemas import SegmentRequest
from backend.core.utils import resolve_path
from backend.ai.segmentation.sam_service import sam_segmenter
from backend.services.logging import logger

router = APIRouter()

@router.post("/edit/segment")
async def segment_object(request: SegmentRequest):
    """Generate mask from click point using SAM."""
    try:
        full_path = resolve_path(request.image_path)
        
        if request.box:
            logger.info(f"Segmenting {request.image_path} with box {request.box}")
            mask_path = sam_segmenter.generate_mask(full_path, box=request.box)
        else:
            logger.info(f"Segmenting {request.image_path} at {request.x}, {request.y}")
            mask_path = sam_segmenter.generate_mask(full_path, x=request.x, y=request.y)
        
        return {
            "mask_url": f"/masks/{mask_path.name}", 
            "mask_path": str(mask_path)
        }
    except Exception as e:
        logger.error(f"Segmentation failed: {e}")
        raise HTTPException(500, str(e))
