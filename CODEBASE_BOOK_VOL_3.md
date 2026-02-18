# COMPLETE CODEBASE EXPLANATION - VOLUME 3
## API Layer & Frontend

This volume covers the Interface Layer: How the outside world talks to the AI, and how the User Interface works.

---

## 19. API Endpoints: `backend/api/endpoints/`

The API acts as the bridge between the Frontend and the Backend Services.

### A. Upload (`upload.py`)
```python
@router.post("/api/upload")
async def upload_image(...):
     # 1. Save Image
     # 2. Run Room Classifier (detect_room logic)
     return { "image_path": ..., "detected_room_type": ... }
```
*   **Smart Upload**: It doesn't just save the file; it immediately triggers a classification to guess if it's a "Living Room" or "Bedroom", saving the user a click.

### B. Detect (`detect.py`)
```python
@router.post("/vision/detect")
async def detect_furniture(...):
    # 1. Run YOLO
    detections = yolo_detector.detect_furniture(image)
    # 2. Get Replacement Suggestions
    # 3. Get Online Vendor Links
    return complex_json_response
```
*   **Orchestrator**: Moves data from Vision -> Logic -> Web Search -> Frontend.

### C. Plan (`plan.py`)
```python
@router.post("/api/plan")
async def create_plan(request):
     # 1. Planner Agent (Create Steps)
     plan = await planner_agent.create_plan(...)
     # 2. Web Suggester (Find Products for Steps)
     # 3. Budget Agent (Verify Cost)
     return final_plan
```
*   **Agent Chain**: Chains three different services (LLM Planner -> Web Search -> LLM Critic) into a single synchronous API call.

### D. Generate (`generate.py`)
```python
@router.post("/api/generate")
async def generate_design(...):
     # Check Provider
     if provider == "offline":
          # Use Local Stable Diffusion
          offline_provider.generate_image(...)
     elif provider == "replicate":
          # Call Cloud API
          replicate_provider.generate_image(...)
```
*   **Abstraction**: The frontend doesn't care *how* it's generated. This endpoint handles the complexity of dispatching to the right engine.

### E. Inpaint (`inpaint.py`) & Segment (`segment.py`)
*   **Inpaint**: Wraps the Stable Diffusion Inpainting pipeline.
*   **Segment**: Wraps the SAM `generate_mask` function.
*   **Recolor**: Wraps the `recolor.py` logic (OpenCV-based wall tinting).

### F. History (`history.py`)
*   Simple CRUD (Create/Read) endpoints to fetch and save the JSON session history.

---

## 20. Frontend: `frontend/index.html`

**Structure**:
1.  **Sidebar**: Tabs for Create / Edit / Plan.
2.  **Main Canvas**: Displays the User Image + Mask Layer.
3.  **Scripts**: Imports `script.js`.
4.  **CSS**: Uses `styles.css` (Dark Mode UI).

---

## 21. Frontend: `frontend/script.js`

**The Controller**.

### Initialization
```javascript
function init() {
    setupTabs();
    setupUpload();
    // ...
}
```

### Upload Flow
```javascript
  async function uploadToServer(file) {
      // POST /api/upload
      // Receive response
      if (data.detected_room_type) {
           // Update Dropdown
           // Update Badge
      }
  }
```
*   **Reactivity**: Updates the UI immediately based on the backend's "Smart Upload" analysis.

### Planning Logic
```javascript
  planBtn.addEventListener('click', async () => {
      // POST /api/plan
      // Render Response as HTML
      addChatMessage("ai", planText);
      return; // Stop execution (Ghost Error Fix)
  });
```

### Canvas Interaction (Masking)
```javascript
  maskCanvas.addEventListener('mouseup', (e) => {
      // 1. Calculate relative coordinates
      // 2. Determine if Click or Drag
      // 3. Call /edit/segment API
      // 4. Draw resulting mask on canvas
  });
```
*   **Coordinate mapping**: The most complex part. Translates `e.clientX` (Screen Pixel) -> `canvas coordinates` -> `image resolution coordinates` for the backend.

---

## 🏁 Final System Summary

1.  **User Opens App**: `main.py` starts. `config.py` detects Hardware.
2.  **User Uploads**: `upload.py` saves file.
3.  **User Clicks "Scan"**: `detect.py` runs YOLO, finds furniture, finds links.
4.  **User Asks "Remove Bed"**: `plan.py` calls Llama 3 -> Returns steps.
5.  **User Clicks "Generate"**: `generate.py` loads Stable Diffusion (swapping out YOLO if needed) -> Generates Design.

This codebase is a tightly integrated system designed to bring **Cloud-Grade AI** to **Local Consumer Hardware** through aggressive memory management (`memory.py`) and optimized usage of state-of-the-art models (SD 1.5, YOLOv8, SAM).
