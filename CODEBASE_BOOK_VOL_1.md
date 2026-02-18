# COMPLETE CODEBASE EXPLANATION - VOLUME 1
## Core Architecture & Foundation

This volume covers the initialization, configuration, and foundational services that power the Interior Design AI.

---

## 1. Entry Point: `backend/main.py`

**Purpose**: The bootstrapper. It initializes the FastAPI application, mounts static directories, and starts the server.

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
*   **Imports**: Standard FastAPI imports.
*   **`import backend.core.config.settings`**: **Executes Config Logic**. This import triggers the entire hardware verification process defined in `config.py`. The app decides if it's "Low VRAM" or "Normal" right here, before `app = FastAPI()` runs.

```python
app = FastAPI(...)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # ...
)
```
*   **CORS**: Configures Cross-Origin Resource Sharing to allow the frontend (running on a different port/protocol) to communicate with the backend.

```python
app.mount("/generated", StaticFiles(directory=str(settings.generated_dir)), name="generated")
app.mount("/uploads", StaticFiles(directory=str(settings.uploads_dir)), name="uploads")
app.mount("/masks", StaticFiles(directory=str(settings.storage_dir / "masks")), name="masks")
```
*   **Static Serving**:
    *   Maps URL paths (e.g., `/generated`) directly to filesystem paths.
    *   **Crucial**: This bypasses Python execution for image serving, ensuring high performance when the frontend loads generated limits.

```python
app.include_router(api_router)
```
*   **Routing**: Registers all endpoint logic from `backend/api/routes.py`.

```python
@app.get("/health")
async def health_check():
    # ... checks CUDA status ...
```
*   **Health Check**: Used by the frontend `Script.js` to show the "System Online" badge.

---

## 2. Core Configuration: `backend/core/config.py`

**Purpose**: The Single Source of Truth for settings and Hardware Profiling.

### Hardware Detection Logic
```python
# Auto-detect Hardware Profile (STRICT OVERRIDE)
settings = Settings()

try:
    if torch.cuda.is_available():
        vram_bytes = torch.cuda.get_device_properties(0).total_memory
        vram_gb = vram_bytes / (1024**3)
        if vram_gb <= 4.5:
            settings.low_vram = True
```
*   **Execution Time**: This block runs on *import*.
*   **Logic**: Query the GPU driver. If VRAM <= 4.5GB, set `settings.low_vram = True`.
*   **Effect**: This flag is the global switch. It tells `OfflineDiffusersProvider` to use aggressive caching and `MemoryManager` to evict models aggressively.

### Directory Setup
```python
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.generated_dir.mkdir(parents=True, exist_ok=True)
# ...
```
*   **Self-Healing**: Ensures `storage/` folders exist. If you delete them, the app recreates them on restart.

---

## 3. Data Models: `backend/core/schemas.py`

**Purpose**: Defines the expected structure (Schema) of JSON requests using Pydantic.

```python
class SegmentRequest(BaseModel):
    image_path: str
    mode: str = "point"
    points: Optional[List[List[int]]] = None
    box: Optional[List[int]] = None
```
*   **Validation**: FastAPI uses this to validate input. If a user sends "box": "banana", FastAPI returns a 422 Error automatically.
*   **Flexibility**: `Optional` fields allow the same endpoint to handle Click (Points) and Drag (Box) interactions.

```python
class GenerateRequest(BaseModel):
    image_path: str
    room_type: str
    style: str
    budget: int
    provider: str = "offline"
```
*   **Provider**: Defaults to "offline" (Local GPU). Can be switched to "replicate" via frontend dropdown.

---

## 4. Utilities: `backend/core/utils.py`

**Purpose**: Helper functions, primarily for file path resolution.

```python
def resolve_path(path_str: str) -> Path:
    candidates = [
        settings.uploads_dir / clean_name,
        Path("storage/generated") / clean_name,
        # ...
    ]
```
*   **Robustness**: The frontend might send `/uploads/image.png` or just `image.png` or `C:/.../image.png`.
*   **Logic**: This function checks multiple known directories to find the *actual* file on disk, preventing `FileNotFoundError` crashes in the pipeline.

---

## 5. Budget Engine: `backend/core/budget_engine.py`

**Purpose**: Calculates cost estimates for renovations.

```python
    def calculate_item_cost(self, item_name):
        if item_lower in self.estimates:
            return self.estimates[...]
```
*   **Logic**: Checks a static lookup table (`BUDGET_ESTIMATES` in config) for base prices.
*   **Fallback**: Returns 500 (generic cost) if item not found, ensuring the math never breaks.

```python
    def calculate_plan_cost(self, plan_steps):
        # Iterates steps, sums up costs
```
*   Used by the API to show the "Total Estimated Cost" on the frontend.

---

## 6. Services: Logging (`backend/services/logging.py`)

**Purpose**: Configures the console output format.

```python
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
```
*   **Format**: `[2026-02-18 10:00:00] [INFO] Model loaded`.
*   **Importance**: Helps debug race conditions and async flows by giving exact timestamps.

---

## 7. Services: Storage (`backend/services/storage.py`)

**Purpose**: Low-level file Input/Output operations.

```python
def save_uploaded_image(image_data, filename):
    unique_name = f"{uuid.uuid4()}{ext}"
    filepath = settings.uploads_dir / unique_name
```
*   **Sanitization**: Never trusts the user's filename (which could contain viruses or path traversal attacks). It generates a random UUID for the file saved on disk.

```python
def save_generated_image(image, prefix="generated"):
    unique_name = f"{prefix}_{uuid.uuid4()}.png"
    image.save(filepath, format="PNG", quality=95)
```
*   **Format**: Always saves as PNG to preserve quality (lossless) for future edits (Inpainting).

---

## 8. Services: History (`backend/services/history_service.py`)

**Purpose**: Persists session data to `storage/history.json`.

```python
    def _ensure_file(self):
        if not HISTORY_FILE.exists():
            with open(HISTORY_FILE, "w") as f: json.dump([], f)
```
*   **Persistence**: Creates a JSON file to store past sessions.
*   **Logic**: Each `add_session` call reads the file, appends the new session object, and overwrites the file. Simple, flat-file database suitable for single-user local apps.

---

## 9. Memory Manager: `backend/utils/memory.py`

**Purpose**: **CRITICAL**. The Traffic Controller for GPU VRAM.

```python
class MemoryManager:
    _current_model: Optional[str] = None
    _loaded_models: dict = {}
```
*   **Singleton**: One instance controls the entire backend.

```python
    @classmethod
    def ensure_gpu(cls, name: str):
        if cls._current_model is not None:
            # LOW_VRAM: Enforce strict switching
            if settings.low_vram:
                cls.offload_all()
```
*   **The "One at a Time" Rule**: If Low VRAM mode is active, this function **evicts** any currently loaded model (moving it to CPU) before allowing a new model to take the stage.
*   **Normal Mode**: Skips eviction, allowing models to coexist.

```python
    @classmethod
    def offload_all(cls):
        for name, model in cls._loaded_models.items():
            model.to("cpu")
        cls.force_cleanup()
```
*   **Offloading**: Moves weights to system RAM.
*   **`force_cleanup`**: Calls `gc.collect()` and `torch.cuda.empty_cache()` to flush the GPU memory buffers immediately.

---

**End of Volume 1.**
*Next Volume: AI Providers, Vision Services, and Agents.*
