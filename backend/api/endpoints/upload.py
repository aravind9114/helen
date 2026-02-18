from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.storage import save_uploaded_image
from backend.room_type_detection.room_classifier import room_classifier

router = APIRouter()

@router.post("/api/upload")
async def upload_image(image: UploadFile = File(...)):
    try:
        # Save image
        content = await image.read()
        saved_path = save_uploaded_image(content, image.filename)
        
        # Run Room Classification
        room_type, confidence, candidates = room_classifier.classify(saved_path)
        
        return {
            "status": "success", 
            "image_path": f"/uploads/{saved_path.name}",
            "filename": saved_path.name,
            # Room Detection Results
            "detected_room_type": room_type,
            "room_confidence": confidence,
            "room_top3": candidates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
