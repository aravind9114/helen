import httpx
from typing import List, Dict, Any, Optional
from backend.core.config import settings
from backend.services.logging import logger

class OllamaClient:
    """Async client for local Ollama instance."""
    
    def __init__(self, base_url: str = settings.ollama_url, model: str = settings.ollama_model):
        self.base_url = base_url
        self.model = model
        
    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate JSON response ensuring valid JSON structure.
        Uses format="json" if supported by model/Ollama version.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "format": "json",  # Force JSON mode
            "options": {
                "temperature": 0.2, # Low temperature for deterministic planning
                "num_ctx": 4096
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/chat", 
                    json=payload, 
                    timeout=60.0 # 60s timeout for complex plans
                )
                response.raise_for_status()
                
                result = response.json()
                content = result.get("message", {}).get("content", "{}")
                
                # Verify JSON structure manually if needed (Ollama 'format': 'json' usually handles this)
                import json
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    logger.error(f"Ollama returned invalid JSON: {content}")
                    # Robust fallback using regex to find matching braces
                    import re
                    json_match = re.search(r"\{.*\}", content, re.DOTALL)
                    if json_match:
                        try: 
                            return json.loads(json_match.group(0))
                        except:
                            pass
                            
                    # Fallback for ```json blocks if regex failed
                    if "```" in content:
                        parts = content.split("```")
                        for part in parts:
                            if "{" in part:
                                try:
                                    return json.loads(part.replace("json", "").strip())
                                except:
                                    continue
                                    
                    raise ValueError("Failed to parse JSON response from LLM")
                    
            except httpx.RequestError as e:
                logger.error(f"Ollama connection error: {e}")
                # Fallback mocking if offline? No, user wants it purely offline but operational.
                # If Ollama is down, we should gracefully fail or suggest starting it.
                raise RuntimeError(f"Could not connect to Ollama at {self.base_url}. Is it running?")
            except Exception as e:
                logger.error(f"LLM Generation failed: {e}")
                raise

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Standard text generation."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/chat", 
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json().get("message", {}).get("content", "")
            except Exception as e:
                logger.error(f"LLM Text Generation failed: {e}")
                raise

# Global Instance
ollama_client = OllamaClient()
