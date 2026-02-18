from ultralytics import YOLO
import torch
from pathlib import Path
from backend.services.logging import logger

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
        "tv": "tv"
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._load_model()
    
    def _load_model(self):
        """Load YOLOv8 model once"""
        logger.info("Loading YOLOv8 model...")
        
        # Detect device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"YOLO using device: {device}")
        
        # Load YOLOv8n (nano - fastest)
        self._model = YOLO("yolov8n.pt")
        self._model.to(device)
        
        logger.info("✓ YOLO model loaded")
    
    def detect_furniture(self, image_path: Path, confidence_threshold: float = 0.35):
        """
        Detect furniture in image
        Returns: list of detections
        """
        logger.info(f"Running YOLO detection on: {image_path.name}")
        
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
        return detections
