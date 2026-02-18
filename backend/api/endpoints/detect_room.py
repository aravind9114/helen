from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.storage import save_uploaded_image
from backend.room_type_detection.room_classifier import room_classifier
from backend.services.logging import logger

router = APIRouter()

@router.post("/api/room-detect")
async def detect_room_type(image: UploadFile = File(...)):
    """
    Explicitly detect room type from uploaded image.
    """
    try:
        # Save temp image
        content = await image.read()
        saved_path = save_uploaded_image(content, image.filename)
        
        # Run classification
        room_type, confidence, candidates = room_classifier.classify(saved_path)
        
        return {
            "detected_room_type": room_type,
            "room_confidence": confidence,
            "room_top3": candidates
        }
    except Exception as e:
        logger.error(f"Room detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
