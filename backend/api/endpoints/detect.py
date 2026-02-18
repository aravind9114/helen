from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from backend.services.logging import logger
from backend.services.storage import save_uploaded_image
from backend.ai.vision.detector import YOLODetector
from backend.services.replacement_engine import ReplacementEngine
from backend.services.vendor_links import VendorLinks

router = APIRouter()

# Initialize services (singleton)
yolo_detector = YOLODetector()
replacement_engine = ReplacementEngine()
vendor_links = VendorLinks()

@router.post("/vision/detect")
async def detect_furniture(
    image: UploadFile = File(...),
    budget: int = Form(...),
):
    """Detect furniture and suggest replacements."""
    logger.info("=== Furniture Detection Request ===")
    logger.info(f"Budget: {budget}")
    
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        image_data = await image.read()
        image_path = save_uploaded_image(image_data, image.filename)
        logger.info(f"Saved upload: {image_path.name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")
    
    try:
        detections = yolo_detector.detect_furniture(image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")
    
    try:
        suggestions, remaining_budget = replacement_engine.suggest_replacements(detections, budget)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestion generation failed: {str(e)}")
    
    # Get online suggestions for each detected category using vendor directory or web search
    from backend.services.web_suggest import WebSuggest
    web_suggest = WebSuggest()
    
    online_suggestions = {}
    for detection in detections:
        category = detection["category"]
        if category not in online_suggestions:
            try:
                # Try VendorLinks matches first
                links = vendor_links.get_vendor_links(category)
                
                # If no static links, fall back to Web Search
                if not links.get("results"):
                    logger.info(f"Using WebSuggest for {category}")
                    links = web_suggest.search_suggestions(category, budget=budget)
                
                online_suggestions[category] = links
                logger.info(f"✓ Loaded {len(online_suggestions[category]['results'])} links for {category}")
            except Exception as e:
                logger.warning(f"Links failed for {category}: {e}")
                online_suggestions[category] = {"results": [], "cache": "error", "latency_ms": 0}
    
    logger.info(f"✓ Detection complete: {len(detections)} items, {len(suggestions)} suggestions")
    logger.info("=== Request Complete ===")
    
    return {
        "detections": detections,
        "suggestions": suggestions,
        "online_suggestions": online_suggestions,
        "remaining_budget": remaining_budget
    }
