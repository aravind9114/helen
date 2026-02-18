from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import time

from backend.services.logging import logger
from backend.services.storage import save_uploaded_image
from backend.services.budget import estimate_cost, check_budget_status
from backend.providers.offline_diffusers import offline_provider
from backend.providers.online_replicate import replicate_provider
from backend.providers.online_hf_inference import hf_provider
from backend.llm.agents.prompt import prompt_agent

router = APIRouter()

@router.post("/api/generate")
async def generate_design(
    image: UploadFile = File(...),
    room_type: str = Form(...),
    style: str = Form(...),
    budget: int = Form(...),
    provider: str = Form(...),
    strength: float = Form(0.55),
):
    """
    Generate interior design based on uploaded image and parameters.
    """
    start_time = time.time()
    
    try:
        # Log request
        logger.info(f"=== New generation request ===")
        logger.info(f"Provider: {provider}")
        logger.info(f"Room type: {room_type}")
        logger.info(f"Style: {style}")
        logger.info(f"Budget: {budget}")
        
        # Validate provider
        if provider not in ["offline", "replicate", "hf"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider: {provider}. Must be 'offline', 'replicate', or 'hf'"
            )
        
        # Save uploaded image
        image_data = await image.read()
        if not image_data:
            raise HTTPException(status_code=400, detail="Empty image file")
        
        image_path = save_uploaded_image(image_data, image.filename or "upload.jpg")
        logger.info(f"Saved upload: {image_path.name}")
        
        # Estimate cost
        estimated_cost = estimate_cost(style)
        budget_status = check_budget_status(estimated_cost, budget)
        logger.info(f"Estimated cost: {estimated_cost} | Budget: {budget} | Status: {budget_status}")
        
        # Generate image based on provider
        output_path = None
        generation_time = 0.0
        
        try:
            if provider == "offline":
                # Optimize prompt
                base_prompt = f"{room_type} in {style} style"
                try:
                    optimized = await prompt_agent.optimize_prompt(base_prompt, style)
                    final_prompt = optimized.get("optimized_prompt", base_prompt)
                    logger.info(f"Optimized Prompt: {final_prompt}")
                except Exception:
                    final_prompt = base_prompt

                output_path, generation_time = offline_provider.generate_image(
                    image_path,
                    room_type, # Changed from final_prompt to room_type based on instruction
                    style,
                    strength=strength # Added strength based on instruction
                )
                
            elif provider == "replicate":
                output_path, generation_time = replicate_provider.generate_image(
                    image_path, room_type, style
                )
                
            elif provider == "hf":
                output_path, generation_time = hf_provider.generate_image(
                    image_path, room_type, style
                )
        
        except RuntimeError as e:
            # Provider configuration error
            error_message = str(e)
            logger.error(f"Provider error: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
        
        except Exception as e:
            # Generation error
            logger.error(f"Generation failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate image: {str(e)}"
            )
        
        # Build response
        total_time = time.time() - start_time
        # Use relative path - frontend adds BACKEND_URL
        image_url = f"/generated/{output_path.name}"
        
        response = {
            "image_url": image_url,
            "provider_used": provider,
            "estimated_cost": estimated_cost,
            "budget": budget,
            "status": budget_status,
            "time_taken_sec": round(generation_time, 2),
            "total_time_sec": round(total_time, 2),
        }
        
        logger.info(f"✓ Generation complete in {total_time:.1f}s")
        logger.info(f"=== Request complete ===\n")
        
        return JSONResponse(content=response, status_code=200)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
