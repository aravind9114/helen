from fastapi import APIRouter, HTTPException
from backend.core.schemas import InpaintRequest
from backend.core.utils import resolve_path
from backend.ai.diffusion.inpaint import inpaint_provider
from backend.services.logging import logger

router = APIRouter()

@router.post("/edit/inpaint")
async def inpaint_object(request: InpaintRequest):
    """Replace object using Stable Diffusion Inpainting."""
    logger.info(f"Inpainting {request.image_path} with prompt: {request.prompt}")
    try:
        image_path = resolve_path(request.image_path)
        mask_path = resolve_path(request.mask_path)
        
        # Inpaint
        output_path = inpaint_provider.inpaint(image_path, mask_path, request.prompt, request.strength)
        
        return {
            "image_url": f"/generated/{output_path.name}",
            "image_path": str(output_path)
        }
    except Exception as e:
        logger.error(f"Inpainting failed: {e}")
        raise HTTPException(500, str(e))
