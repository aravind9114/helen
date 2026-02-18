# COMPLETE CODEBASE EXPLANATION - VOLUME 2
## AI Models & Intelligent Agents

This volume covers the "Brain" of the system: The Generative AI models, Vision systems, and LLM Agents.

---

## 10. Diffusion Provider: `backend/providers/offline_diffusers.py`

**Purpose**: Wraps Stable Diffusion (v1.5) for image generation. Handles the heavy GPU lifting.

### Hardware-Specific Loading
```python
    def __init__(self):
        if torch.cuda.is_available():
            self.device = "cuda"
            self.dtype = torch.float16 # Half precision (saves 50% VRAM)
```
*   **Optimization**: Forces `float16` on CUDA. This is non-negotiable for 4GB usage.

### Pipeline Initialization
```python
    def initialize(self):
        memory_manager.ensure_gpu("sd_img2img") # Ask permission
        
        self.pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(...)
        
        if self.device == "cuda":
            self.pipeline.enable_attention_slicing()
            self.pipeline.enable_vae_slicing()
```
*   **VRAM Safeguards**:
    *   **Attention Slicing**: Computes attention in small chunks.
    *   **VAE Slicing**: Decodes images in strips. Prevents the "Final Step Crash".

### Inference Logic
```python
    def generate_image(self, ...):
        target_size = (512, 512)
        # ...
        if settings.low_vram:
            num_steps = min(settings.num_inference_steps, 20)
```
*   **Constraints**:
    *   **Resolution**: Capped at 512x512 to ensure stability.
    *   **Steps**: Capped at 20 for Low VRAM mode to prevent timeouts and overheating on laptops.

```python
        with torch.inference_mode():
             output = self.pipeline(...)
             
        if settings.low_vram:
             torch.cuda.empty_cache()
```
*   **Cleanup**: Immediately attempts to free VRAM after generation, keeping the system responsive.

---

## 11. Vision: `backend/ai/vision/detector.py` (YOLO)

**Purpose**: Detects furniture items locally.

```python
    def _load_model(self):
        memory_manager.ensure_gpu("yolov8")
        self._model = YOLO("yolov8n.pt") # Nano model (Smallest)
```
*   **Interaction**: Calls `ensure_gpu`, which might kick Stable Diffusion out of VRAM.

```python
    def detect_furniture(self, ...):
        # ... inference ...
        if settings.low_vram:
             self._model.to("cpu")
```
*   **Immediate Eviction**: YOLO is only needed for 1 second. It immediately moves itself to CPU after running, voluntarily freeing the GPU for the next task.

---

## 12. Vision: `backend/ai/segmentation/sam_service.py` (SAM)

**Purpose**: High-precision object masking.

```python
class SamSegmenter:
    def __init__(self):
        # STRICT RULE: SAM must ALWAYS run on CPU
        self.device = "cpu"
```
*   **Design Decision**: SAM runs on CPU.
*   **Why?** It prevents competition with Stable Diffusion. Users can mask (CPU) and Generate (GPU) without constant swapping.

---

## 13. LLM Client: `backend/llm/ollama_client.py`

**Purpose**: Communicates with the local Llama 3 instance.

```python
    async def generate_json(self, prompt, ...):
        payload = { "format": "json", ... }
        # ... http post ...
```
*   **Structured Output**: Forces the LLM to reply in JSON, which is critical for the Planning Agent's reliability.

---

## 14. Agents: Planner (`backend/llm/agents/planner.py`)

**Purpose**: Converts user text ("Remove bed") into a structured JSON plan.

```python
    async def create_plan(self, user_request, detected_items):
        full_system_prompt = PLANNER_SYSTEM_PROMPT.format(
            detected_items=formatted_list
        )
        return await self.client.generate_json(...)
```
*   **Context Injection**: IT feeds the YOLO detections (`detected_items`) into the prompt.
*   **Logic**: The LLM "sees" the room inventory and the user request, then decides the steps.

---

## 15. Agents: Budget (`backend/llm/agents/budget.py`)

**Purpose**: Reviews plans for financial feasibility.

```python
    async def verify_plan(self, plan, budget):
         prompt = f"Check this plan against {budget}..."
```
*   **Role**: A "Critic" agent. It doesn't generate content; it acts as a guardrail, warning the user if their plan implies expensive construction.

---

## 16. Services: Web Suggest (`backend/services/web_suggest.py`)

**Purpose**: Finds real items on the web.

```python
    def search_suggestions(self, category):
        with DDGS() as ddgs:
            results = ddgs.text(...)
```
*   **Privacy**: Uses DuckDuckGo to search for furniture without tracking generated queries.

---

## 17. Services: Vendor Links (`backend/services/vendor_links.py`)

**Purpose**: Provides hardcoded, reliable links for common items.

```python
    VENDOR_DIRECTORY = {
        "sofa": [ { "link": "pepperfry.com/...", "vendor": "Pepperfry" }, ... ]
    }
```
*   **Reliability**: Web search can be flaky or return blogs. This directory guarantees at least 5-10 valid shopping links for major categories (`Bed`, `Sofa`, `Table`), ensuring the "Shop" feature always works in the demo.

---

## 18. Services: Replacement Engine (`backend/services/replacement_engine.py`)

**Purpose**: Logic for suggesting cheaper alternatives.

```python
    def suggest_replacements(self, detections, budget):
        # Groups items by price
        # Suggests items cheaper than current estimate
```
*   **Logic**: Uses a local `catalog.json` (or internal dict) to find items that fit within the remaining budget.

---

**End of Volume 2.**
*Next Volume: API Endpoints and Frontend Implementation.*
