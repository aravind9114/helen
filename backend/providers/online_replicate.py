"""
Online provider using Replicate API.
Requires REPLICATE_API_TOKEN environment variable.
"""
import time
from pathlib import Path
import base64

from backend.core.config import settings
from backend.services.logging import logger
from backend.services.storage import save_generated_image

try:
    import replicate
    REPLICATE_AVAILABLE = True
except ImportError:
    REPLICATE_AVAILABLE = False


class ReplicateProvider:
    """Online provider using Replicate API."""
    
    def __init__(self):
        self.client = None
    
    def initialize(self):
        """Initialize Replicate client."""
        if not REPLICATE_AVAILABLE:
            raise RuntimeError("Replicate SDK not installed. Install with: pip install replicate")
        
        if not settings.replicate_api_token:
            raise RuntimeError(
                "Replicate not configured. Please add REPLICATE_API_TOKEN to .env "
                "or switch to Offline mode."
            )
        
        self.client = replicate.Client(api_token=settings.replicate_api_token)
        logger.info("✓ Replicate provider initialized")
    
    def generate_image(
        self,
        image_path: Path,
        room_type: str,
        style: str
    ) -> tuple[Path, float]:
        """
        Generate redesigned interior image using Replicate.
        
        Args:
            image_path: Path to input image
            room_type: Type of room
            style: Design style
            
        Returns:
            Tuple of (output_image_path, time_taken_seconds)
        """
        self.initialize()
        
        start_time = time.time()
        
        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        image_uri = f"data:image/jpeg;base64,{image_data}"
        
        # Build prompt
        prompt = (
            f"A {style} {room_type} Editorial Style Photo, Symmetry, Straight On, "
            f"Modern Living Room, Large Window, Leather, Glass, Metal, Wood Paneling, "
            f"Neutral Palette, Ikea, Natural Light, Apartment, Afternoon, Serene, "
            f"Contemporary, 4k"
        )
        
        logger.info(f"Calling Replicate API with {style} {room_type}...")
        
        # Run model
        model = "jagilley/controlnet-hough:854e8727697a057c525cdb45ab037f64ecca770a1769cc52287c2e56472a247b"
        output = self.client.run(
            model,
            input={
                "image": image_uri,
                "prompt": prompt,
                "a_prompt": "best quality, extremely detailed, photo from Pinterest, interior, cinematic photo, ultra-detailed, ultra-realistic, award-winning",
            }
        )
        
        # Download result (second image is the final output)
        if not output or len(output) < 2:
            raise RuntimeError("Replicate API returned unexpected output")
        
        import requests
        from PIL import Image
        import io
        
        result_url = output[1] if len(output) > 1 else output[0]
        response = requests.get(result_url)
        response.raise_for_status()
        
        result_image = Image.open(io.BytesIO(response.content))
        output_path = save_generated_image(result_image, prefix="replicate")
        
        time_taken = time.time() - start_time
        logger.info(f"✓ Replicate image generated in {time_taken:.1f}s")
        
        return output_path, time_taken


# Global provider instance
replicate_provider = ReplicateProvider()
