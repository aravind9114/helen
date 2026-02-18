"""
Room Type Classifier using Hugging Face Pipeline.
"""
from transformers import pipeline
from PIL import Image
from pathlib import Path
import time
from backend.services.logging import logger
from backend.room_type_detection.cache_utils import setup_hf_cache, enable_offline_mode
from backend.room_type_detection.label_mapping import normalize_room_label

# Model Selection
# 'alessandroseni/room-type-detection' is a good lightweight choice
MODEL_ID = "alessandroseni/room-type-detection"

class RoomClassifier:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RoomClassifier, cls).__new__(cls)
            cls._instance.pipeline = None
            cls._instance.model_path = None
        return cls._instance

    def __init__(self):
        # Force CPU execution for 4GB VRAM optimization
        self.device = "cpu"
        self.model_name = "microsoft/resnet-50" 
        self.processor = None
        self.model = None

    def initialize(self):
        """Initialize pipeline (lazy loading)."""
        if self.pipeline:
            return

        start = time.time()
        logger.info(f"[RoomClassifier] Loading model: {MODEL_ID}")
        
        # Setup Cache
        setup_hf_cache()
        
        try:
            # Try loading from cache first
            self.pipeline = pipeline(
                "image-classification",
                model=MODEL_ID,
                device=-1  # Force CPU
            )
            logger.info(f"[RoomClassifier] Loaded in {time.time() - start:.2f}s")
        except Exception as e:
            logger.error(f"[RoomClassifier] Failed to load model: {e}")
            raise

    def classify(self, image_path: Path):
        """
        Classify image room type.
        Returns: canonical_label, confidence, top_k_list
        """
        if not self.pipeline:
            self.initialize()
            
        try:
            image = Image.open(image_path).convert("RGB")
            
            start = time.time()
            # Run inference
            results = self.pipeline(image, top_k=3)
            inference_time = (time.time() - start) * 1000
            
            logger.info(f"[RoomClassifier] Results: {results} ({inference_time:.1f}ms)")
            
            if not results:
                return "Unknown", 0.0, []
                
            top_result = results[0]
            canonical = normalize_room_label(top_result['label'])
            confidence = top_result['score']
            
            # Format top candidates
            candidates = [
                {
                    "label": normalize_room_label(r['label']),
                    "raw_label": r['label'],
                    "score": r['score']
                }
                for r in results
            ]
            
            return canonical, confidence, candidates
            
        except Exception as e:
            logger.error(f"[RoomClassifier] Inference failed: {e}")
            return "Unknown", 0.0, []

room_classifier = RoomClassifier()
