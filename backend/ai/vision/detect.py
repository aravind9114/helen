import cv2
from pathlib import Path
from typing import List, Dict, Any
from ultralytics import YOLO
from backend.services.logging import logger

class ObjectDetector:
    def __init__(self, model_name: str = "yolov8n.pt"):
        self.model_name = model_name
        self.model = None

    def initialize(self):
        if self.model is None:
            logger.info(f"Loading YOLO model: {self.model_name}")
            self.model = YOLO(self.model_name)

    def detect_objects(self, image_path: str) -> List[Dict[str, Any]]:
        self.initialize()
        results = self.model(image_path)
        
        detections = []
        for r in results:
            for box in r.boxes:
                # Get label and confidence
                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]
                conf = float(box.conf[0])
                
                # Filter low confidence
                if conf < 0.4:
                    continue
                
                # Filter only indoor objects (simplified list)
                relevant_labels = [
                    'chair', 'couch', 'potted plant', 'bed', 'dining table', 
                    'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
                    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 
                    'book', 'clock', 'vase', 'scissors', 'teddy bear', 
                    'hair drier', 'toothbrush'
                ]
                
                # Or just allow everything and filter in frontend?
                # Let's verify if label is relevant for furniture/interior
                # YOLOv8n is COCO, so it has generic objects.
                
                # Get coordinates
                xyxy = box.xyxy[0].tolist()
                
                detections.append({
                    "label": label,
                    "confidence": conf,
                    "box": xyxy # [x1, y1, x2, y2]
                })
        
        return detections

# Global instance
detector = ObjectDetector()
