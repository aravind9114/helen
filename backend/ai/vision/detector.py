from ultralytics import YOLO
import torch
import gc
from pathlib import Path
from backend.services.logging import logger
from backend.core.config import settings
from backend.utils.memory import memory_manager

class YOLODetector:
    """Singleton YOLO detector for furniture detection"""
    
    _instance = None
    _model = None
    
    # YOLO to internal category mapping
    CATEGORY_MAP = {
        "couch": "sofa",
        "dining table": "table",
        "chair": "chair",
        "bed": "bed",
        "tv": "tv",
        "potted plant": "decor",
        "vase": "decor",
        "book": "decor",
        "keyboard": "office",
        "mouse": "office",
        "monitor": "tv",
        "laptop": "office",
        "sink": "kitchen",
        "refrigerator": "kitchen",
        "clock": "decor"
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass # Lazy load
    
    def _load_model(self):
        """Load YOLOv8 model"""
        # NORMAL MODE: Keep resident
        if not settings.low_vram and self._model is not None:
             return

        # Ensure GPU slot is available
        memory_manager.ensure_gpu("yolov8")
        
        if self._model is None:
            logger.info("Loading YOLOv8 model...")
            self._model = YOLO("yolov8n.pt") # Nano is tiny
            self._model.to("cuda")
            logger.info("✓ YOLO model loaded")
        
        memory_manager.register_model("yolov8", self._model)
    
    def detect_furniture(self, image_path: Path, confidence_threshold: float = 0.35):
        """
        Detect furniture in image
        Returns: list of detections
        """
        logger.info(f"Running YOLO detection on: {image_path.name}")
        
        self._load_model()
        
        # Run inference
        results = self._model(str(image_path), conf=confidence_threshold, verbose=False)
        
        detections = []
        
        # Process results
        for result in results:
            boxes = result.boxes
            names = result.names
            
            for box in boxes:
                cls_id = int(box.cls[0])
                label = names[cls_id]
                confidence = float(box.conf[0])
                bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                
                # Only include mapped furniture categories
                if label in self.CATEGORY_MAP:
                    detections.append({
                        "label": label,
                        "category": self.CATEGORY_MAP[label],
                        "confidence": round(confidence, 2),
                        "bbox": [round(x, 1) for x in bbox]
                    })
        
        logger.info(f"✓ Detected {len(detections)} furniture items")
        
        # STRICT CLEANUP for LOW_VRAM
        if settings.low_vram:
            if self._model:
                self._model.to("cpu")
                # self._model = None # Optional: Keep object but offload
            torch.cuda.empty_cache()
            gc.collect()
        
        return detections
