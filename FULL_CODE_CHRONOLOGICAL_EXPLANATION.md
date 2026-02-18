# FULL CODE CHRONOLOGICAL EXPLANATION
## Project: Interior Design AI Architect

This document provides a line-by-line technical deep dive into the project's execution flow, verifying every file, function, and logical connection.

---

## 1️⃣ ENTRY POINT: `backend/main.py`

The execution begins here. This file bootstraps the FastAPI server and ties the application components together.

### Imports & Setup
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.core.config import settings
from backend.api.routes import router as api_router
from backend.services.logging import logger
import uvicorn
import torch
```
*   **`from backend.core.config import settings`**: **CRITICAL EXECUTION STEP.** Importing `settings` initializes the `Settings` class in `config.py`. This immediately triggers the hardware verification logic (See Section 2), determining if the app runs in Low VRAM or Normal mode before the server even starts.
*   **`import torch`**: Used later to check CUDA status for the health check.

### App Initialization
```python
app = FastAPI(
    title="Budget-Constrained Interior Design AI",
    description="AI-powered interior design with offline and online providers",
    version="2.0.0"
)
```
*   **`FastAPI(...)`**: Instantiates the ASGI application. This object `app` is the registry for all routes and middleware.

### Middleware (CORS)
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
*   **`CORSMiddleware`**: Cross-Origin Resource Sharing.
*   **Why?** The frontend runs in a browser (e.g., `file://` or `localhost:3000`), while the backend runs on `localhost:8000`. By default, browsers block this cross-port communication for security.
*   **`allow_origins=["*"]`**: A permissive setting for development, allowing any domain to access the API.

### Static File Mounting
```python
app.mount("/generated", StaticFiles(directory=str(settings.generated_dir)), name="generated")
app.mount("/uploads", StaticFiles(directory=str(settings.uploads_dir)), name="uploads")
app.mount("/masks", StaticFiles(directory=str(settings.storage_dir / "masks")), name="masks")
```
*   **`app.mount`**: Binds a specific URL path (e.g., `/generated`) to a directory on the disk.
*   **`StaticFiles`**: A standard ASGI app that streams files.
*   **Execution Flow**: When the frontend requests `<img src="http://localhost:8000/generated/result.png">`, FastAPI bypasses all Python logic and serves the file directly from the disk. This is crucial for performance.

### Router & Endpoints
```python
app.include_router(api_router)
```
*   **`app.include_router(api_router)`**: Registers all the API logic defined in `backend/api/routes.py`. Without this, the server would run but report `404 Not Found` for all API calls.

```python
@app.get("/health")
async def health_check():
    cuda_available = torch.cuda.is_available()
    # ... returns status dict
```
*   **Health Check**: A simple diagnostic endpoint. The frontend polls this to verify the backend is online (`System Online` badge).

### Runtime Execution (Script Mode)
```python
if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
```
*   **`uvicorn.run(...)`**: Starts the actual server process.
*   **`reload=True`**: Watches for file changes and restarts the server. This is why you see "Application startup complete" in the terminal.

---

## 2️⃣ CONFIG INITIALIZATION: `backend/core/config.py`

This file is executed immediately when `backend.main` imports it. It acts as the "Hardware Profiler" and "Global State Container".

### Imports
```python
import os
from pathlib import Path
from pydantic_settings import BaseSettings
```
*   **`pydantic_settings.BaseSettings`**: A powerful class that automatically reads environment variables (e.g., `OLLAMA_URL`) and maps them to class attributes.

### Settings Class
```python
class Settings(BaseSettings):
    # Storage paths
    base_dir: Path = Path(__file__).resolve().parent.parent
    storage_dir: Path = base_dir / "storage"
    uploads_dir: Path = storage_dir / "uploads"
    # ...
```
*   **Path Intelligence**:
    *   `Path(__file__)`: The location of `config.py`.
    *   `.parent.parent`: Moves up to `backend/`.
    *   **Why?** Ensures the app works on *any* computer without hardcoded paths like `C:\Users\Aravind...`.

### Hardware Optimization Defaults
```python
    # HARDWARE OPTIMIZATION
    low_vram: bool = True  # Enable 4GB Optimization Mode
```
*   **Defensive Default**: `low_vram` defaults to `True`. If detection fails, the system safely assumes the worst-case scenario (4GB VRAM) to prevent crashing high-end models on low-end hardware.

### Generation Parameters
```python
    diffusers_model: str = "runwayml/stable-diffusion-v1-5"
    image_width: int = 512
    # ...
    num_inference_steps: int = 35      # Normal mode
    # ...
    # Default Generation Params (Overridden if low_vram is True)
    num_inference_steps: int = 20      # Optimized for speed/memory
```
*   **Model Choice**: Hardcoded to `stable-diffusion-v1-5`. Larger models (SDXL) are strictly avoided due to the 4GB VRAM constraint.
*   **Step Strategy**: Defines two sets of defaults. 35 steps for quality (Normal), 20 steps for speed/safety (Low VRAM).

### The Hardware Detection Logic (Execution Time)
```python
# Auto-detect Hardware Profile (STRICT OVERRIDE)
settings = Settings()

try:
    import torch
    if torch.cuda.is_available():
        vram_bytes = torch.cuda.get_device_properties(0).total_memory
        vram_gb = vram_bytes / (1024**3)
        if vram_gb <= 4.5:
            settings.low_vram = True
            print(f"[MemoryProfile] LOW_VRAM activated ({vram_gb:.2f}GB)")
        else:
            settings.low_vram = False
            print(f"[MemoryProfile] NORMAL mode activated ({vram_gb:.2f}GB)")
```
*   **Runtime Logic**: This block runs *outside* any class, so it executes on import.
*   **`vram_gb <= 4.5`**: The critical decision boundary.
    *   **If True**: Sets the global `settings.low_vram` flag. This flag is the "Master Switch" used by `MemoryManager` and `OfflineProvider` later.
    *   **Why 4.5?** 4GB cards often report slightly scattered numbers depending on OS overhead. 4.5GB safely captures all 4GB cards while detecting 6GB/8GB cards as Normal.

### Directory Creation
```python
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.generated_dir.mkdir(parents=True, exist_ok=True)
(settings.storage_dir / "masks").mkdir(parents=True, exist_ok=True)
```
*   **Self-Healing Filesystem**: Ensures that the `storage/` folder structure exists. If deleted, the app rebuilds it on the next run.

---

## 3️⃣ MEMORY MANAGER: `backend/utils/memory.py`

This module implements the **Singleton VRAM Governor**. It is responsible for the unique "Single Slot Policy" that allows this app to run on 4GB VRAM.

### Class Structure
```python
class MemoryManager:
    _current_model: Optional[str] = None
    _loaded_models: dict = {}
```
*   **State Tracking**:
    *   `_loaded_models`: A dictionary mapping model names (e.g., "sd_img2img", "yolov8") to their initializing objects.
    *   `_current_model`: Tracks which specific model is currently allowed to reside on the GPU.

### Model Registration
```python
    @classmethod
    def register_model(cls, name: str, model_instance: Any):
        cls._loaded_models[name] = model_instance
        cls._current_model = name
```
*   **Role**: When `OfflineDiffusersProvider` or `YOLODetector` successfully loads a model, they call this to tell the manager "I am now holding the VRAM".

### The "Bouncer": `ensure_gpu`
```python
    @classmethod
    def ensure_gpu(cls, name: str):
        if cls._current_model == name:
            return

        if cls._current_model is not None:
            # LOW_VRAM: Enforce strict switching (Offload previous)
            if settings.low_vram:
                cls.offload_all()
            else:
                pass # Normal mode
        
        cls._current_model = name
```
*   **Logic**:
    *   Called *before* any model attempts to load weights.
    *   **Low VRAM Mode**: If *Model A* is in VRAM and *Model B* calls `ensure_gpu`, the manager **Forcibly Evicts** Model A (calls `offload_all`). This guarantees the GPU is empty before B tries to load.
    *   **Normal Mode**: It does nothing, allowing A and B to coexist for faster performance.

### The Cleanup Crew: `offload_all`
```python
    @classmethod
    def offload_all(cls, force: bool = False):
        # ... check settings.low_vram ...
        
        for name, model in cls._loaded_models.items():
            if hasattr(model, "to"):
                model.to("cpu")
            elif hasattr(model, "cpu"):
                model.cpu()
                
        cls.force_cleanup()
```
*   **`model.to("cpu")`**: This is the core trick. It moves the model's tensors from VRAM (Video RAM) to System RAM.
    *   **Why implementation matters**: We don't `del model` (delete). We keep the python object in RAM. Moving it back to GPU later (`.to("cuda")`) is much faster than reloading files from the disk.

### Force Cleanup
```python
    @classmethod
    def force_cleanup(cls):
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
```
*   **`gc.collect()`**: Python's garbage collector. Removes unused variables.
*   **`torch.cuda.empty_cache()`**: Tells the CUDA driver to release memory pages that are checked out but empty. PyTorch caches memory aggressively; this forces it to release it back to the operating system logic.

---

## 4️⃣ DIFFUSION PROVIDER: `backend/providers/offline_diffusers.py`

This file contains the heavy lifting for Image Generation. It wraps the Hugging Face `diffusers` library and applies the specific optimizations needed for consumer hardware.

### Imports
```python
from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
from backend.utils.memory import memory_manager
```
*   **`StableDiffusionImg2ImgPipeline`**: The specific pipeline used. It takes an input image + prompt and produces a new image. It is *not* the standard text-to-image pipeline.
*   **`DPMSolverMultistepScheduler`**: A "Scheduler" controls the denoising process. DPM++ is chosen because it produces high-quality images in fewer steps (20-25) compared to the default Euler (50).

### Initialization & Hardware Logic
```python
class OfflineDiffusersProvider:
    def __init__(self):
        if torch.cuda.is_available():
            self.device = "cuda"
            self.dtype = torch.float16
        else:
            self.device = "cpu"
            self.dtype = torch.float32
```
*   **Precision (dtype)**:
    *   **`float16`**: Uses "Half Precision" floating point numbers (16-bit). This halves the VRAM usage (from ~8GB to ~4GB for SD 1.5) with negligible quality loss. **Crucial for this project.**
    *   **`float32`**: CPU operations generally require 32-bit float consistency.

### Pipeline Loading (`initialize`)
```python
    def initialize(self):
        if not settings.low_vram and self.pipeline is not None:
             return # Skip if already loaded in Normal Mode

        memory_manager.ensure_gpu("sd_img2img")
```
*   **Handshake**: Calls `memory_manager.ensure_gpu`. In Low VRAM mode, this triggers the eviction of YOLO or any other resident model.

```python
        self.pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
            settings.diffusers_model,
            torch_dtype=self.dtype,
            use_safetensors=True
        )
```
*   **`use_safetensors=True`**: Uses the SafeTensors format. It maps directly to memory (mmap) and loads significantly faster than standard PyTorch `.bin` files.

### Optimizations (The "Secret Sauce")
```python
        if self.device == "cuda":
            self.pipeline.to("cuda")
            self.pipeline.enable_attention_slicing()
            self.pipeline.enable_vae_slicing()
            
            if hasattr(self.pipeline, "enable_xformers_memory_efficient_attention"):
                 self.pipeline.enable_xformers_memory_efficient_attention()
```
*   **`enable_attention_slicing()`**: Splits the massive "Attention Matrix" calculation into smaller chunks.
    *   *Trade-off*: Slightly slower (milliseconds).
    *   *Gain*: Massive VRAM savings. Prevents OOM on 4GB cards.
*   **`enable_vae_slicing()`**: The VAE (Variational Autoencoder) converts the latent (compressed) image back to pixels. This is often the step that crashes the GPU at 99%. Slicing decodes the image in strips rather than all at once.
*   **`enable_xformers...`**: Uses optimized CUDA kernels provided by the `xformers` library. If installed, it speeds up generation and reduces memory footprint further.

### Image Generation (`generate_image`)
```python
    def generate_image(self, image_path, ...):
        # ... logic ...
        target_size = (512, 512)
        input_image = input_image.resize(target_size)
```
*   **Resolution Cap**: 
    *   Stable Diffusion v1.5 was trained on 512x512 images.
    *   While Normal mode *could* handle 640x640, the code caps it at 512x512 to ensure 100% stability.
    *   Generating non-square aspect ratios or higher resolutions on v1.5 often results in "duplication artifacts" (two heads, stacked rooms).

### Step Capping Logic
```python
        if settings.low_vram:
            strength = settings.img2img_strength
            num_steps = min(settings.num_inference_steps, 20)
        else:
            num_steps = min(30, settings.num_inference_steps)
```
*   **Runtime Config**: This block explicitly overrides global settings based on the runtime hardware profile.
    *   **Low VRAM**: Capped at 20 steps. Users cannot force higher steps via API to prevent timeouts or OOMs.

### Inference Call
```python
        with torch.inference_mode():
            output = self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=input_image,
                strength=strength,
                guidance_scale=settings.guidance_scale,
                num_inference_steps=num_steps
            ).images[0]
```
*   **`torch.inference_mode()`**: Disables PyTorch's gradient calculation engine (Autograd). Even though we aren't training, PyTorch tracks history by default. Disabling this saves significant RAM.
*   **`guidance_scale`**: Controls how strictly the AI follows the prompt (7.0-7.5 is standard).
*   **`strength`**: Controls how much pixel data is preserved from the original. Lower strength = more structure preservation.

### Immediate Cleanup (Low VRAM)
```python
        if settings.low_vram:
            torch.cuda.empty_cache()
```
*   **Purpose**: Immediately after the heavy lifting, it attempts to free VRAM for the next task (like UI updates or thumbnail generation), keeping the system snappy.

---

## 5️⃣ YOLO DETECTOR: `backend/ai/vision/detector.py`

Responsible for detecting furniture items (`Bed`, `Sofa`, `Table`) in the room to inform the Planning Agent.

### Model Loading (Lazy)
```python
    def _load_model(self):
        memory_manager.ensure_gpu("yolov8")
        if self._model is None:
            self._model = YOLO("yolov8n.pt")
            self._model.to("cuda")
```
*   **`YOLO("yolov8n.pt")`**: Loads the "Nano" version of YOLOv8. It is the smallest and fastest variant, suitable for real-time applications.
*   **`ensure_gpu("yolov8")`**: Guarantees that Stable Diffusion is offloaded before YOLO loads, preventing OOM.

### Detection Pipeline
```python
    def detect_furniture(self, image_path, ...):
        results = self._model(str(image_path), conf=0.35)
```
*   **Inference**: Runs the image through the YOLO network.
*   **`conf=0.35`**: Filters out weak detections (less than 35% confidence).

### Immediate Offloading
```python
        if settings.low_vram:
            if self._model:
                self._model.to("cpu")
            torch.cuda.empty_cache()
```
*   **Why?** Detection is usually a one-off event at the start of a session. There is no need to keep YOLO in VRAM while the user is prompting or generating. We move it to CPU immediately to clear the stage for the main star (Stable Diffusion).

---

## 6️⃣ SAM SEGMENTATION: `backend/ai/segmentation/sam_service.py`

Handles precise object masking (e.g., "Select the sofa").

### Strict CPU Enforcement
```python
class SamSegmenter:
    def __init__(self):
        # STRICT RULE: SAM must ALWAYS run on CPU for both profiles
        self.device = "cpu"
```
*   **Design Decision**: SAM (Segment Anything Model) is computationally lighter than SD but memory-intensive.
*   **Why CPU?** By forcing SAM to CPU, we allow the user to mask objects *without* unloading Stable Diffusion from the GPU (in Normal mode). In Low VRAM mode, it avoids the costly "Swap IN/Swap OUT" dance if the user just wants to select a few pixels.

### Mask Generation
```python
    def generate_mask(self, image_path, x, y, box):
        # ...
        results = self.model(source=image_path, device="cpu", points=[[x, y]], labels=[1])
```
*   **Point Prompting**: Converts the user's click (x, y) into a prompt for the SAM model.
*   **Output**: Returns a binary mask (black & white image) where the selected object is white.

