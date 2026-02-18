import cv2
import numpy as np
from pathlib import Path
from backend.services.logging import logger
from backend.core.config import settings

class WallPainter:
    """Non-AI fast recoloring for walls."""
    
    def hex_to_hsv(self, hex_color: str):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        # Convert RGB to HSV (OpenCV uses H:0-179, S:0-255, V:0-255)
        hsv_pixel = np.uint8([[[b, g, r]]])
        hsv = cv2.cvtColor(hsv_pixel, cv2.COLOR_BGR2HSV)[0][0]
        return hsv

    def recolor_wall(self, image_path: Path, mask_path: Path, color_hex: str) -> Path:
        """
        Recolor wall using HSV preservation (keeps texture, changes hue/sat).
        """
        logger.info(f"Recoloring wall to {color_hex}")
        
        # Load images
        image = cv2.imread(str(image_path))
        mask = cv2.imread(str(mask_path), 0)  # Load as grayscale
        
        # Resize mask to match image
        mask = cv2.resize(mask, (image.shape[1], image.shape[0]))
        
        # Convert image to HSV
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv_image)
        
        # Target color
        target_h, target_s, target_v = self.hex_to_hsv(color_hex)
        
        # Create new H and S channels based on target
        # We blend original V (brightness) with target V to keep shadows
        new_h = np.full_like(h, target_h)
        new_s = np.full_like(s, target_s)
        
        # Apply changes ONLY where mask is white (>0)
        h = np.where(mask > 0, new_h, h)
        s = np.where(mask > 0, new_s, s)
        # Mix V (brightness) - preserve 70% original texture/shadows, add 30% target brightness
        v = np.where(mask > 0, (v.astype(float)*0.7 + target_v*0.3).astype(np.uint8), v)

        # Merge back
        final_hsv = cv2.merge([h, s, v])
        final_bgr = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        
        # Soft blending for edges
        # Convert mask to float 0-1
        mask_float = mask.astype(float) / 255.0
        mask_float = cv2.GaussianBlur(mask_float, (3, 3), 0)
        mask_3ch = np.dstack([mask_float]*3)
        
        # Blend: final = blended * mask + original * (1-mask)
        output = (final_bgr * mask_3ch + image * (1 - mask_3ch)).astype(np.uint8)
        
        # Save output
        output_filename = f"recolor_{image_path.name}"
        output_path = settings.generated_dir / output_filename
        cv2.imwrite(str(output_path), output)
        
        return output_path

wall_painter = WallPainter()
