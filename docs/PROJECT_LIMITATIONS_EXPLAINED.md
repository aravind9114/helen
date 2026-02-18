# Project Limitations and Justification for Design Decisions

This section outlines technical constraints encountered during development and justifies the exclusion of specific features originally proposed. These decisions were made to prioritize system stability, performance, and the integrity of the core Generative AI features on the target hardware (NVIDIA GTX 1650, 4GB VRAM).

## 1. Exclusion of Drag-and-Drop Image Editing
The initial proposal included a feature to drag-and-drop furniture items into the scene. This feature was evaluated but ultimately excluded for the following technical reasons:

### A. Hardware Constraints (VRAM Bottleneck)
State-of-the-art (SOTA) models capable of realistic "object insertion" (such as **Flux**, **SDXL Inpainting**, or **ControlNet Reference-Only**) require significant GPU memory.
*   **Minimum Requirement:** 12GB - 16GB VRAM for stable inference.
*   **Available Hardware:** 4GB VRAM (GTX 1650).
Attempting to load these models resulted in immediate `CUDA Out of Memory` errors. Using strictly CPU offloading for these large models would result in inference times exceeding 5-10 minutes per edit, violating the "Real-Time" requirement of the project.

### B. Limitations of Lightweight Models (Stable Diffusion v1.5)
While lightweight models like Stable Diffusion v1.5 can run on 4GB VRAM, they lack the spatial coherence required for realistic object insertion. During testing, these models frequently:
*   Failed to blend the new object's lighting with the scene.
*   "Hallucinated" distorted objects when given a specific furniture mask.
*   Struggled to maintain the scale of inserted objects relative to the room.

**Conclusion:** To maintain a high standard of visual quality, the system focuses on **Global Style Transfer** (redesigning the entire room style) rather than local object insertion, which requires hardware beyond the scope of this project.

## 2. Exclusion of 3D Volumetric Visualization
The proposal to convert 2D images into interactive 3D environments was deprecated in favor of high-fidelity 2D Generative AI for the following reasons:

### A. Monocular Depth Estimation Accuracy
Extracting a 3D mesh from a single 2D image (Monocular Depth Estimation) using tools like MiDaS or ZoeDepth typically produces "2.5D" representations, not true 3D.
*   **Issue:** Furniture items act as "billboards" rather than true 3D objects.
*   **Result:** Users cannot truly rotate "behind" objects, leading to visual artifacts and a poor user experience.

### B. Shift to Generative AI Paradigm
The interior design industry is shifting from manual 3D modeling (CAD) to **Generative AI Visualization**.
*   **Justification:** Modern AI models (like the one implemented) can generate photorealistic lighting, textures, and reflections that would take hours to render in a traditional 3D engine.
*   **Decision:** The project prioritizes **photorealism and style transfer** over low-fidelity 3D geometry.

## 3. Lighting Simulation
Interactive lighting controls (e.g., toggling "Day/Night") were implemented implicitly via **Prompt Engineering** rather than a physics-based physics engine.
*   **Reason:** Physics-based ray tracing requires complex 3D geometry which (as noted above) was not generated.
*   **Solution:** The AI model was fine-tuned to understand prompts like *"cinematic lighting"*, *"warm atmosphere"*, and *"natural sunlight"*, allowing users to achieve the desired lighting effects via the style selection interface.

---

### **Summary Table for Defense/Viva**

| Feature | Status | Justification for Deviation |
| :--- | :--- | :--- |
| **Generative AI Design** | ✅ **Completed** | Core feature; successfully implemented using Stable Diffusion + CUDA. |
| **Object Detection** | ✅ **Completed** | Implemented using YOLOv8 for accurate furniture recognition. |
| **Drag & Drop Editing** | ❌ **Excluded** | **Hardware Limitation:** Requires 12GB+ VRAM for realistic results; target hardware has 4GB. |
| **3D Visualization** | ❌ **Excluded** | **Technology Shift:** Prioritized photorealistic AI generation over low-fidelity 3D mesh approximation. |
| **Real-Time Costing** | ✅ **Completed** | Integrated logic for budget estimation and vendor price lookups. |
