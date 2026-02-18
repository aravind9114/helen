import torch
import numpy as np
import cv2
import os
import gc
from typing import Optional
from pathlib import Path
from ultralytics import SAM
from backend.services.logging import logger
from backend.core.config import settings
from backend.utils.memory import memory_manager

class SamSegmenter:
    def __init__(self):
        self.model = None
        # STRICT RULE: SAM must ALWAYS run on CPU for both profiles
        self.device = "cpu"
        self.model_name = "sam_b.pt"

    def initialize(self):
        """Lazy load SAM model on CPU."""
        if self.model is not None:
            return

        logger.info(f"Loading Ultralytics SAM model ({self.model_name})...")
        try:
            self.model = SAM(self.model_name)
            # FORCE CPU - Never allow CUDA
            self.model.to("cpu")
            
            # Log strictly as requested
            logger.info("[SAM] device=cpu dtype=float32 (LOW_VRAM)")
            
            # We do NOT register with memory_manager because it doesn't use VRAM
            logger.info("SAM model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load SAM model: {e}")
            raise RuntimeError(f"Could not load SAM model. Error: {e}")

    def generate_mask(self, image_path: Path, x: Optional[int] = None, y: Optional[int] = None, box: Optional[list] = None) -> Path:
        """
        Generate mask from a single point click or box using Ultralytics SAM.
        Returns path to saved mask.
        """
        self.initialize()
        
        # Prepare prompts
        kwargs = {
            "source": str(image_path),
            "device": "cpu", # Explicitly CPU
            "retina_masks": True,
            "verbose": False
        }
        
        if box:
            kwargs["bboxes"] = [box]
        elif x is not None and y is not None:
            kwargs["points"] = [[x, y]]
            kwargs["labels"] = [1]
        else:
            raise ValueError("Must provide either point (x,y) or box.")

        # Predict
        try:
            results = self.model(**kwargs)
            
            # Extract mask
            if results[0].masks is None:
                raise ValueError("No mask detected at this point.")
                
            # Get the first mask (usually the best one)
            mask_tensor = results[0].masks.data[0]
            
            # Convert to numpy uint8 (0 or 255)
            mask_np = mask_tensor.cpu().numpy().astype(np.uint8) * 255
            
            # Ensure mask is same size as original image
            orig_h, orig_w = results[0].orig_shape
            # Resize if needed (SAM sometimes returns smaller masks)
            if mask_np.shape[:2] != (orig_h, orig_w):
                 mask_np = cv2.resize(mask_np, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST)

            # Dilate mask slightly to cover edges for inpainting
            kernel = np.ones((5, 5), np.uint8)
            mask_dilated = cv2.dilate(mask_np, kernel, iterations=2)
            
            # Save mask
            mask_filename = f"mask_{int(os.path.getmtime(image_path))}_{x}_{y}.png"
            mask_path = settings.storage_dir / "masks" / mask_filename
            mask_path.parent.mkdir(parents=True, exist_ok=True)
            
            cv2.imwrite(str(mask_path), mask_dilated)
            logger.info(f"Generated mask saved to {mask_path}")
            
            return mask_path
            
        finally:
            # CLEANUP: No need to offload since it's already CPU
            pass
            # We don't need SAM again immediately usually.
            if self.model:
                 logger.info("Offloading SAM to CPU...")
                 self.model.to("cpu")
                 torch.cuda.empty_cache()
                 # We need to tell memory manager it's gone?
                 # Actually, memory manager tracks it. We just moved it.
                 # But next time ensure_gpu("sam") is called, it might try to offload others.
                 # Since we manually offloaded, we are good.
                 pass

# Global instance
sam_segmenter = SamSegmenter()
