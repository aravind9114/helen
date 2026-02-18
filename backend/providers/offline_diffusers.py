import torch
from PIL import Image
from pathlib import Path
import time
import gc

from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
from backend.core.config import settings, PROMPT_TEMPLATE, NEGATIVE_PROMPT
from backend.services.logging import logger
from backend.services.storage import resize_image, save_generated_image
from backend.utils.memory import memory_manager


class OfflineDiffusersProvider:
    """Offline image-to-image provider using Stable Diffusion."""
    
    def __init__(self):
        self.pipeline = None
        # Determine device and dtype based on strict hardware profile
        if torch.cuda.is_available():
            self.device = "cuda"
            self.dtype = torch.float16
            logger.info(f"[SD] CUDA Mode. Using float16. Low VRAM: {settings.low_vram}")
        else:
            self.device = "cpu"
            self.dtype = torch.float32
            logger.info("[SD] CPU Mode. Using float32.")
        
    def initialize(self):
        """Initialize the Stable Diffusion pipeline (lazy loading)."""
        # NORMAL MODE: Keep resident if already loaded
        if not settings.low_vram and self.pipeline is not None:
            return

        # Ensure GPU slot is ours (Only if we need to load or re-load)
        memory_manager.ensure_gpu("sd_img2img")
        
        if self.pipeline is not None:
            return  # Already initialized
        
        logger.info("Initializing offline Diffusers provider...")
        
        # Load pipeline (RTX 4060 works great with float16)
        logger.info(f"Loading model: {settings.diffusers_model}")
        
        try:
            self.pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
                settings.diffusers_model,
                torch_dtype=self.dtype,
                safety_checker=None,
                use_safetensors=True
            )
            
            # Use DPM++ 2M Karras Scheduler for better realism
            self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(self.pipeline.scheduler.config, use_karras_sigmas=True)
            
            # OPTIMIZATION: 4GB VRAM Specifics
            if self.device == "cuda":
                self.pipeline.to("cuda")
                self.pipeline.enable_attention_slicing()
                self.pipeline.enable_vae_slicing()
                # self.pipeline.enable_model_cpu_offload() # Conflict with manual management? 
                # Better to keep it on GPU while active, then kill it.
                if hasattr(self.pipeline, "enable_xformers_memory_efficient_attention"):
                    try:
                        self.pipeline.enable_xformers_memory_efficient_attention()
                    except:
                        pass
            
            memory_manager.register_model("sd_img2img", self.pipeline)
            logger.info("✓ Model loaded successfully!")
            
        except Exception as e:
            logger.error(f"Failed to load SD model: {e}")
            raise

    
    def generate_prompt(self, room_type: str, style: str) -> tuple[str, str]:
        """
        Generate prompt and negative prompt based on parameters.
        
        Args:
            room_type: Type of room (e.g., "Living Room")
            style: Design style (e.g., "Modern")
            
        Returns:
            Tuple of (prompt, negative_prompt)
        """
        prompt = PROMPT_TEMPLATE.format(
            room_type=room_type.lower(),
            style=style.lower()
        )
        return prompt, NEGATIVE_PROMPT
    
    def generate_image(
        self,
        image_path: Path,
        room_type: str,
        style: str,
        strength: float = 0.65
    ) -> tuple[Path, float]:
        """
        Generate redesigned interior image.
        """
        # Initialize pipeline if needed
        self.initialize()
        
        start_time = time.time()
        
        # Load and resize input image
        # STRICT RULE: Cap resolution for VRAM safety
        target_size = (512, 512)
        if not settings.low_vram and self.device == "cuda":
            # NORMAL mode allow up to 640 if possible, but 512 is safest
            # We stick to 512 as per "Otherwise keep 512" rule for simplicity/safety
            pass
            
        input_image = Image.open(image_path).convert("RGB")
        input_image = input_image.resize(target_size)
        
        prompt, negative_prompt = self.generate_prompt(room_type, style)
        
        # Override strength/steps based on profile
        if settings.low_vram:
            strength = settings.img2img_strength
            # STRICT CAP: steps <= 20
            num_steps = min(settings.num_inference_steps, 20)
        else:
            # NORMAL MODE: steps <= 30
            num_steps = min(30, settings.num_inference_steps)
            
        # CPU Fallback Cap
        if self.device == "cpu":
            num_steps = min(num_steps, 12)
            
        try:
            with torch.inference_mode():
                output = self.pipeline(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    image=input_image,
                    strength=strength,
                    guidance_scale=settings.guidance_scale,
                    num_inference_steps=num_steps
                ).images[0]
                
            # Post-generation cleanup
            if settings.low_vram:
                # LOW_VRAM: Clean up immediately
                torch.cuda.empty_cache()

            # Save
            output_path = save_generated_image(output, prompt)
            
            return output_path, time.time() - start_time
            
        except torch.cuda.OutOfMemoryError:
            logger.warning("OOM Detected! Retrying with lower steps...")
            torch.cuda.empty_cache()
            gc.collect()
            
            # Retry with minimal settings
            with torch.inference_mode():
                output = self.pipeline(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    image=input_image,
                    strength=strength,
                    guidance_scale=settings.guidance_scale,
                    num_inference_steps=15 # Safe mode
                ).images[0]
                
            output_path = save_generated_image(output, prompt)
            return output_path, time.time() - start_time
        logger.info(f"Processing image: {image_path.name} | Strength: {strength}")
        init_image = resize_image(
            image_path,
            settings.image_width,
            settings.image_height
        )
        
        # Generate prompts
        prompt, negative_prompt = self.generate_prompt(room_type, style)
        logger.info(f"Prompt: {prompt}")
        
        # Run inference
        logger.info("Generating image with Stable Diffusion...")
        result = self.pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=init_image,
            strength=strength,
            num_inference_steps=settings.num_inference_steps,
            guidance_scale=settings.guidance_scale,
        )
        
        # Save generated image
        output_image = result.images[0]
        output_path = save_generated_image(output_image, prefix="offline")
        
        time_taken = time.time() - start_time
        logger.info(f"✓ Image generated in {time_taken:.1f}s: {output_path.name}")
        
        return output_path, time_taken


# Global provider instance (singleton)
offline_provider = OfflineDiffusersProvider()
