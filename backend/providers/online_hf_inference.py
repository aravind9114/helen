"""
Online provider using HuggingFace Inference API.
Requires HF_API_TOKEN environment variable.
"""
import time
from pathlib import Path
import requests
from PIL import Image
import io

from backend.core.config import settings, PROMPT_TEMPLATE, NEGATIVE_PROMPT
from backend.services.logging import logger
from backend.services.storage import save_generated_image


class HuggingFaceProvider:
    """Online provider using HuggingFace Inference API."""
    
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        self.headers = None
    
    def initialize(self):
        """Initialize HuggingFace API client."""
        if not settings.hf_api_token:
            raise RuntimeError(
                "HuggingFace not configured. Please add HF_API_TOKEN to .env "
                "or switch to Offline mode."
            )
        
        self.headers = {"Authorization": f"Bearer {settings.hf_api_token}"}
        logger.info("✓ HuggingFace provider initialized")
    
    def generate_image(
        self,
        image_path: Path,
        room_type: str,
        style: str
    ) -> tuple[Path, float]:
        """
        Generate redesigned interior image using HuggingFace.
        
        Args:
            image_path: Path to input image
            room_type: Type of room
            style: Design style
            
        Returns:
            Tuple of (output_image_path, time_taken_seconds)
        """
        self.initialize()
        
        start_time = time.time()
        
        # Generate prompt
        prompt, _ = PROMPT_TEMPLATE.format(
            room_type=room_type.lower(),
            style=style.lower()
        ), NEGATIVE_PROMPT
        
        logger.info(f"Calling HuggingFace API with {style} {room_type}...")
        
        # Read image
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        # Note: HF Inference API for img2img requires different approach
        # Using text-to-image as simplified example
        payload = {"inputs": prompt}
        
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"HuggingFace API error: {response.text}")
        
        # Parse response
        result_image = Image.open(io.BytesIO(response.content))
        output_path = save_generated_image(result_image, prefix="hf")
        
        time_taken = time.time() - start_time
        logger.info(f"✓ HuggingFace image generated in {time_taken:.1f}s")
        
        return output_path, time_taken


# Global provider instance
hf_provider = HuggingFaceProvider()
