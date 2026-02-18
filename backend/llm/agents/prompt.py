from typing import Dict, Any
from backend.llm.ollama_client import ollama_client
from backend.llm.prompts.prompt_optimizer import PROMPT_OPTIMIZER_SYSTEM_PROMPT
from backend.services.logging import logger

class PromptAgent:
    """Agent that optimizes prompts for Stable Diffusion."""
    
    def __init__(self):
        self.client = ollama_client

    async def optimize_prompt(self, base_prompt: str, style: str) -> Dict[str, str]:
        """
        Enhance prompt with style and quality boosters.
        """
        full_system_prompt = PROMPT_OPTIMIZER_SYSTEM_PROMPT.format(
            base_prompt=base_prompt,
            style=style
        )
        
        logger.info(f"Prompt Agent optimizing: {base_prompt} for style {style}")
        
        try:
            result = await self.client.generate_json(
                prompt="Optimize this prompt.",
                system_prompt=full_system_prompt
            )
            return result
        except Exception as e:
            logger.error(f"Prompt optimization failed: {e}")
            # Fallback
            return {
                "optimized_prompt": f"((({base_prompt}))), {style}, high quality, realistic, 4k",
                "negative_prompt": "low quality, text, blurry"
            }

prompt_agent = PromptAgent()
