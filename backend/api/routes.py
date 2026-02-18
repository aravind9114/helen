from fastapi import APIRouter
from backend.api.endpoints import generate, inpaint, segment, detect, recolor, upload, plan, history, budget, detect_room

router = APIRouter()

# Combine all endpoints
router.include_router(generate.router, tags=["generate"])
router.include_router(inpaint.router, tags=["edit"])
router.include_router(segment.router, tags=["segment"])
router.include_router(detect.router, tags=["detect"]) # YOLO
router.include_router(detect_room.router, tags=["room-detect"]) # Classifier
router.include_router(recolor.router, tags=["recolor"])
router.include_router(upload.router, tags=["upload"])
router.include_router(plan.router, tags=["plan"])
router.include_router(history.router, tags=["history"])
router.include_router(budget.router, tags=["budget"])
