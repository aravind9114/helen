import torch
from pathlib import Path
from PIL import Image
from diffusers import StableDiffusionInpaintPipeline
from backend.core.config import settings
from backend.services.logging import logger
from backend.utils.memory import memory_manager
import gc

class InpaintProvider:
    def __init__(self):
        self.pipeline = None
        # Determine device and dtype based on strict hardware profile
        if torch.cuda.is_available():
            self.device = "cuda"
            self.dtype = torch.float16
            logger.info(f"[Inpaint] CUDA Mode. Using float16. Low VRAM: {settings.low_vram}")
        else:
            self.device = "cpu"
            self.dtype = torch.float32
            logger.info("[Inpaint] CPU Mode. Using float32.")

    def initialize(self):
        """Lazy load Inpainting pipeline."""
        # NORMAL MODE: Keep resident if already loaded
        if not settings.low_vram and self.pipeline is not None:
            return

        # Ensure GPU slot
        memory_manager.ensure_gpu("sd_inpaint")
        
        if self.pipeline is not None:
            return

        logger.info(f"Loading Inpainting model: {settings.diffusers_model}")
        
        # Use standard inpainting model or base model
        model_id = "runwayml/stable-diffusion-inpainting"
        
        try:
            self.pipeline = StableDiffusionInpaintPipeline.from_pretrained(
                model_id,
                torch_dtype=self.dtype,
                safety_checker=None,
                use_safetensors=True
            )
            
            if self.device == "cuda":
                self.pipeline.to("cuda")
                self.pipeline.enable_attention_slicing()
                self.pipeline.enable_vae_slicing()
                # self.pipeline.enable_model_cpu_offload() 
                if hasattr(self.pipeline, "enable_xformers_memory_efficient_attention"):
                    try:
                        self.pipeline.enable_xformers_memory_efficient_attention()
                    except:
                        pass
                
            memory_manager.register_model("sd_inpaint", self.pipeline)
            logger.info("Inpainting model loaded.")
        except Exception as e:
            logger.error(f"Failed to load inpaint model: {e}")
            raise

    def inpaint(self, image_path: Path, mask_path: Path, prompt: str, strength: float = 1.0) -> Path:
        self.initialize()
        
        # Open images
        image = Image.open(image_path).convert("RGB")
        mask_image = Image.open(mask_path).convert("L") # Mask must be grayscale
        
        # Prepare mask and image
        # STRICT RULE: Cap resolution at 512x512
        target_size = (512, 512)
        
        # Resize inputs -> Strictly 512x512 for optimization
        # (Even for Normal mode, keeping 512 for inpainting consistency is better)
        image_resized = image.resize(target_size, Image.Resampling.LANCZOS)
        mask_resized = mask_image.resize(target_size, Image.Resampling.NEAREST)
        
        # Enhanced prompt
        enhanced_prompt = f"((({prompt}))), high quality, 4k, realistic"
        negative_prompt = "low quality, blurry, distorted, bad perspective, bad masking, watermark, text"
        
        num_inference_steps = kwargs.get("num_inference_steps", 20)
        
        if settings.low_vram:
            # STRICT CAP: steps <= 20
            num_inference_steps = min(num_inference_steps, 20)
        else:
             # NORMAL MODE: up to 30
             num_inference_steps = min(30, num_inference_steps)

        # CPU Fallback Cap
        if self.device == "cpu":
            num_inference_steps = min(num_inference_steps, 12)

        # Inpainting execution
        try:
            with torch.inference_mode():
                output = self.pipeline(
                    prompt=enhanced_prompt,
                    negative_prompt=negative_prompt,
                    image=image_resized,
                    mask_image=mask_resized,
                    num_inference_steps=num_inference_steps,
                    strength=strength,      
                    guidance_scale=8.0     
                ).images[0]
            
            if settings.low_vram:
                torch.cuda.empty_cache()
                
        except torch.cuda.OutOfMemoryError:
             logger.warning("OOM during inpainting. Retrying with lower specs...")
             torch.cuda.empty_cache()
             gc.collect()
             with torch.inference_mode():
                output = self.pipeline(
                    prompt=enhanced_prompt,
                    negative_prompt=negative_prompt,
                    image=image_resized,
                    mask_image=mask_resized,
                    num_inference_steps=15, # Safe mode
                    strength=strength,      
                    guidance_scale=7.0     
                ).images[0]

        # Save output
        output_filename = f"edit_{image_path.name}"
        output_path = settings.generated_dir / output_filename
        output.save(output_path)
        
        return output_path

# Global instance
inpaint_provider = InpaintProvider()
