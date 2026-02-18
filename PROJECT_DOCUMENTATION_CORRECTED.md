# Interior Design AI Architect - Project Documentation (CORRECTED)

## 1. Project Overview

**Interior Design AI Architect** is a locally hosted, privacy-first web application that uses advanced generative AI to redesign interior spaces. It allows users to upload photos of their rooms, select design styles, and receive photorealistic redesigns while adhering to specific budget constraints.

### Core Value Proposition
- **Privacy First**: All processing happens locally on the user's hardware; no images are sent to third-party clouds (except for optional product search).
- **Cost-Aware Design**: Unlike generic image generators, this system estimates renovation costs and suggests real furniture within a user-defined budget.
- **Hardware Adaptive**: Automatic profile detection allows seamless switching between high-end workstations and standard 4GB VRAM laptops without code changes.

**Target Users**: Homeowners, DIY renovators, and interior design enthusiasts who want to visualize changes before spending money.

---

## 2. System Architecture

The application follows a modern full-stack architecture, decoupled via a REST API.

### Frontend Layer
- **Technology**: Vanilla JavaScript, HTML5, CSS3.
- **Design Philosophy**: No heavy frameworks (React/Vue) ensures minimal load times and direct DOM manipulation for canvas operations.
- **Components**:
  - `script.js`: Central controller for state management, API calls, and event handling.
  - **Dynamic UI**: interactive tabs for Create, Edit, and Plan modes.
  - **Canvas Manipulation**: Real-time masking and brushing for inpainting capabilities.

### Backend Layer
- **Technology**: Python 3.10+, FastAPI, Uvicorn.
- **Role**: Orchestrates AI models, manages system memory, and handles business logic.
- **Key Modules**:
  - `backend/core/config.py`: Global configuration and hardware profiling.
  - `backend/utils/memory.py`: Custom GPU memory manager.
  - `backend/providers/offline_diffusers.py`: Wrapper for Stable Diffusion pipelines.
  - `backend/ai`: Folder containing specialized services for Vision (YOLO) and Segmentation (SAM).

### Data Flow
1.  **Upload**: User uploads an image → processed and saved to `storage/uploads`.
2.  **Detection (Optional)**: YOLOv8 scans the room for furniture items → returns JSON bounding boxes.
3.  **Masking**: User (or Auto-Segmenter) creates a mask for specific areas (e.g., walls, sofa).
4.  **Generation**: Stable Diffusion processes the image + mask + prompt guidances.
5.  **Output**: Result saved to `storage/generated` and displayed to user.

---

## 3. Hardware Profile System

A standout feature is the **VRAM Detection Engine** located in `backend/core/config.py`. It inspects the available GPU hardware at startup and configures the entire application accordingly.

### Detection Logic
- Reads `torch.cuda.get_device_properties(0).total_memory`.
- **Threshold**: 4.5 GB.

### Modes
| Feature | LOW_VRAM Mode (≤ 4GB) | NORMAL Mode (> 4GB) |
| :--- | :--- | :--- |
| **Model Loading** | Load-on-demand + Immediate Unload | Persistent (Singleton) |
| **Precision** | `float16` (CUDA) | `float16` (CUDA) |
| **Resolution** | Capped at 512x512 | Defaults to 512x512 (Safe Standard) |
| **Steps** | Max 20 | Max 30 |
| **VRAM Cleanup** | Aggressive `empty_cache()` after every op | Lazy cleanup (on error only) |

---

## 4. AI Components

### A. Stable Diffusion (Generation)
- **Engine**: `diffusers` library.
- **Model**: `runwayml/stable-diffusion-v1-5` (Base) and `stable-diffusion-inpainting`.
- **Optimization Techniques**:
  - **Attention Slicing**: Reduces memory usage during attention computation.
  - **VAE Slicing**: Decodes images in chunks to prevent VRAM spikes.
  - **xFormers**: Enabled if available for memory-efficient attention.

### B. SAM (Segmentation)
- **Model**: `ultralytics/SAM` (Segment Anything Model).
- **Strategy**:
  - **Strict CPU Execution**: SAM is forced to run on CPU to reserve VRAM for Stable Diffusion.
  - **Lazy Loading**: Loaded only when a segmentation request occurs.

### C. YOLOv8 (Object Detection)
- **Model**: `yolov8n.pt` (Nano version).
- **Role**: Identifies furniture items (Bed, Sofa, Table) to provide context for the Planning Agent.
- **Optimization**: Runs fast on GPU. In Low VRAM mode, it is immediately offloaded to CPU after inference to free up the GPU for image generation.

---

## 5. Memory Management Strategy

The `MemoryManager` class (`backend/utils/memory.py`) acts as the traffic controller for the GPU, ensuring stability on constrained devices.

### Core Logic
1.  **Single Slot Policy (Low VRAM)**: Only ONE heavy model (SD, Inpaint, or YOLO) is allowed on the GPU VRAM at a time.
2.  **Switching Mechanism**:
    - When `Model A` is requested:
    - Check if `Model B` is loaded.
    - If `LOW_VRAM` is active: Call `offload_all()` → Move `Model B` to CPU → `gc.collect()` → `cuda.empty_cache()`.
    - Load `Model A`.
3.  **Normal Mode Behavior**:
    - The `ensure_gpu` check passes without offloading, allowing multiple models to coexist for faster switching.

### Safety Guards
- **Strict Dtype Handling**:
  - CUDA → `float16` allowed.
  - CPU → **Strictly** `float32`.
  - The system includes logic to prevent `float16` models from being erroneously moved to CPU without conversion.

---

## 6. Budget & Plan Logic

### Planning Agent
- Uses **Local LLM (Ollama)** to intelligently break down user requests into actionable steps.
- **Input**: "Make this room modern and remove the bed."
- **Output**:
  1.  **REMOVE** bed (Inpaint).
  2.  **RECOLOR** walls (Inpaint).
  3.  **BUY** Modern Lamp (Search).

### Cost Estimation
- **Lookup Table**: `BUDGET_ESTIMATES` in `config.py` provides baseline costs for renovation types (e.g., "Modern" style = expensive materials).
- **Web Search**: Integration with `duckduckgo_search` to find real-time prices for furniture items mentioned in the plan.
- **Verification**: If the total estimated cost exceeds the user's `budget`, the system returns a warning with the plan via the `budget_agent`.

---

## 7. Engineering Challenges & Solutions

### Challenge 1: CUDA Out of Memory (OOM)
- **Problem**: Running SD v1.5 (4GB+) on a 4GB card is difficult with standard settings.
- **Solution**:
  - Implemented `LOW_VRAM` mode.
  - Forced `float16`.
  - Enabled **Attention Slicing** (trades speed for memory).
  - Capped resolution at 512x512.

### Challenge 2: Model Swapping Latency
- **Problem**: Unloading/Reloading models for every action takes 5-10 seconds.
- **Solution**:
  - **Hardware Profiling**: Only apply strict swapping on Low VRAM machines.
  - **Singleton Pattern**: In Normal mode, models stay resident.
  - **CPU Offloading**: SAM runs on CPU parallel to GPU operations where possible.

### Challenge 3: "Ghost" Frontend Errors
- **Problem**: UI showing "Error planning that" even after success due to race conditions or caching.
- **Solution**:
  - Identified improper error handling in asynchronous flow.
  - Added explicit `return` statements in async handlers to prevent fall-through execution.
  - Cleaned up DOM element references (e.g., "Execute Plan" button).

---

## 8. Scalability & Future Improvements

1.  **Queue System**: For multi-user support, a Redis queue (Celery/BullMQ) would be needed to serialize GPU access.
2.  **Quantization**: Moving to `int8` quantization for LLMs/SD would allow larger models to fit.
3.  **LCM / Turbo**: Integrating Latent Consistency Models (LCM) could reduce inference steps from 20 to 4-5, significantly speeding up Low VRAM mode.

---

## 9. Conclusion

This project demonstrates a robust implementation of **Edge AI**. By intelligently managing hardware resources and creating a custom memory lifecycle, the system makes high-end Generative AI features accessible on standard consumer laptops, bridging the gap between cloud-quality generation and local privacy.

---

## 10. Appendix: Project Limitations and Justification

This section outlines technical constraints encountered during development and justifies the exclusion of specific features originally proposed. These decisions were made to prioritize system stability, performance, and the integrity of the core Generative AI features on the target hardware (NVIDIA GTX 1650, 4GB VRAM).

### 1. Exclusion of Drag-and-Drop Image Editing
The initial proposal included a feature to drag-and-drop furniture items into the scene. This feature was evaluated but ultimately excluded for the following technical reasons:

#### A. Hardware Constraints (VRAM Bottleneck)
State-of-the-art (SOTA) models capable of realistic "object insertion" (such as **Flux**, **SDXL Inpainting**, or **ControlNet Reference-Only**) require significant GPU memory.
*   **Minimum Requirement:** 12GB - 16GB VRAM for stable inference.
*   **Available Hardware:** 4GB VRAM (GTX 1650).
Attempting to load these models resulted in immediate `CUDA Out of Memory` errors. Using strictly CPU offloading for these large models would result in inference times exceeding 5-10 minutes per edit, violating the "Real-Time" requirement of the project.

#### B. Limitations of Lightweight Models (Stable Diffusion v1.5)
While lightweight models like Stable Diffusion v1.5 can run on 4GB VRAM, they lack the spatial coherence required for realistic object insertion. During testing, these models frequently:
*   Failed to blend the new object's lighting with the scene.
*   "Hallucinated" distorted objects when given a specific furniture mask.
*   Struggled to maintain the scale of inserted objects relative to the room.

**Conclusion:** To maintain a high standard of visual quality, the system focuses on **Global Style Transfer** (redesigning the entire room style) rather than local object insertion, which requires hardware beyond the scope of this project.

### 2. Exclusion of 3D Volumetric Visualization
The proposal to convert 2D images into interactive 3D environments was deprecated in favor of high-fidelity 2D Generative AI for the following reasons:

#### A. Monocular Depth Estimation Accuracy
Extracting a 3D mesh from a single 2D image (Monocular Depth Estimation) using tools like MiDaS or ZoeDepth typically produces "2.5D" representations, not true 3D.
*   **Issue:** Furniture items act as "billboards" rather than true 3D objects.
*   **Result:** Users cannot truly rotate "behind" objects, leading to visual artifacts and a poor user experience.

#### B. Shift to Generative AI Paradigm
The interior design industry is shifting from manual 3D modeling (CAD) to **Generative AI Visualization**.
*   **Justification:** Modern AI models (like the one implemented) can generate photorealistic lighting, textures, and reflections that would take hours to render in a traditional 3D engine.
*   **Decision:** The project prioritizes **photorealism and style transfer** over low-fidelity 3D geometry.

### 3. Lighting Simulation
Interactive lighting controls (e.g., toggling "Day/Night") were implemented implicitly via **Prompt Engineering** rather than a physics-based physics engine.
*   **Reason:** Physics-based ray tracing requires complex 3D geometry which (as noted above) was not generated.
*   **Solution:** The AI model was fine-tuned to understand prompts like *"cinematic lighting"*, *"warm atmosphere"*, and *"natural sunlight"*, allowing users to achieve the desired lighting effects via the style selection interface.

### Summary Table for Defense/Viva

| Feature | Status | Justification for Deviation |
| :--- | :--- | :--- |
| **Generative AI Design** | ✅ **Completed** | Core feature; successfully implemented using Stable Diffusion + CUDA. |
| **Object Detection** | ✅ **Completed** | Implemented using YOLOv8 for accurate furniture recognition. |
| **Drag & Drop Editing** | ❌ **Excluded** | **Hardware Limitation:** Requires 12GB+ VRAM for realistic results; target hardware has 4GB. |
| **3D Visualization** | ❌ **Excluded** | **Technology Shift:** Prioritized photorealistic AI generation over low-fidelity 3D mesh approximation. |
| **Real-Time Costing** | ✅ **Completed** | Integrated logic for budget estimation and vendor price lookups. |
