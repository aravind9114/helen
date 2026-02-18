# FULL CODE EXPLANATION (PART 2)

---

## 7️⃣ LLM CLIENT: `backend/llm/ollama_client.py`

Operates as the brain of the "Planning Agent", communicating with a local Ollama instance (Llama 3).

### Asynchronous HTTP
```python
    async def generate_json(self, prompt, ...):
        payload = {
            "model": "llama3",
            "format": "json",
            "stream": False,
            "options": { "temperature": 0.2 }
        }
```
*   **`format: "json"`**: Forces the LLM to output strictly valid JSON. This is critical because the backend parses this response programmatically.
*   **`temperature: 0.2`**: Low randomness. We want the planner to be logical and deterministic, not creative.

```python
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:11434/api/chat", json=payload)
```
*   **`httpx`**: An async HTTP library. It allows the Python backend to wait for the LLM (which might take 10s) without blocking other requests (like health checks or image uploads).
*   **Error Handling**: If `localhost:11434` (Ollama) is unreachable, it raises a `RuntimeError` which the API layer catches.

---

## 8️⃣ WEB SUGGEST: `backend/services/web_suggest.py`

Finds real-world furniture links.

### DuckDuckGo Integration
```python
    def search_suggestions(self, category, budget):
         with DDGS() as ddgs:
             results = ddgs.text(f"buy {category} online india", ...)
```
*   **`DDGS`**: An unofficial library for DuckDuckGo.
*   **Why?** It requires no API key and respects privacy (no tracking), aligning with the project's "Offline/Private" ethos.

### Caching
```python
    if cache_key in cache and self._is_cache_valid(...):
        return cache[cache_key]
```
*   **Latency Optimization**: Web searching is slow (1-2s). Detected items (e.g., "Sofa") are often repeated. Caching results for 24 hours makes the UI feel instant on repeat scans.

---

## 9️⃣ API ROUTES

The brain stem. These files map HTTP URLs to the Python functions explained above.

### A. Upload (`endpoints/upload.py`)
```python
@router.post("/api/upload")
async def upload_image(image: UploadFile):
    # Save file
    # Run YOLO detection immediately (optional auto-detect logic)
    return { "image_path": path, "detected_items": [...] }
```
*   **Flow**: Frontend sends file -> Saved to disk -> Returns local path. This path is then sent back by the frontend in subsequent `generate` calls.

### B. Generate (`endpoints/generate.py`)
```python
@router.post("/api/generate")
async def generate_design(provider: str, ...):
    if provider == "offline":
        output, time = offline_provider.generate_image(...)
```
*   **Provider Switching**: Accepts a `provider` string. This allows seamless toggling between local GPU (Offline) and Cloud APIs (Replicate) if the user's hardware is too weak.

### C. Plan (`endpoints/plan.py`)
```python
@router.post("/api/plan")
async def create_plan(request: PlanRequest):
    # 1. Ask Planner Agent (LLM)
    plan = await planner_agent.create_plan(...)
    
    # 2. Enrich with Web Suggestions
    for step in plan["steps"]:
        suggestions = web_suggester.search(...)
        step["suggestions"] = suggestions
        
    return plan
```
*   **Orchestration**: This endpoint acts as a "Supervisor". It calls the LLM, parses the plan, and then calls the Web Search service to populate "buy links" for any furniture mentioned in the plan.

---

## 🔟 FRONTEND: `script.js` & `index.html`

The Control Center. It manages state, canvas drawing, and API communication.

### Initialization & State
```javascript
const state = {
    file: null,
    serverPath: null,
    mode: 'create',
    currentTab: 'create'
};
```
*   **State Management**: Simple JavaScript object to track what the user is doing. No React/Redux complexity needed for this scope.

### Canvas Masking (`setupEditing`)
```javascript
    maskCanvas.addEventListener('mousedown', (e) => {
        isDragging = true;
        // Calculate coordinates relative to canvas
    });
    
    maskCanvas.addEventListener('mouseup', (e) => {
        // ... Detect if Click or Drag ...
        if (isClick) {
             // Send (x,y) to SAM API
             fetch('/edit/segment', { x, y }) 
        }
    });
```
*   **Interaction**: Handles both "Point and Click" (for SAM segmentation) and "Box Dragging".
*   **Coordinate mapping**: Translates screen pixels to image pixels so the backend knows exactly where to segment.

### The Planning Loop (`setupPlanning`)
```javascript
    const res = await fetch(`${BACKEND_URL}/api/plan`, ...);
    const data = await res.json();
    
    // Render the plan HTML
    addChatMessage("ai", planText);
    return; // STOP EXECUTION
```
*   **Ghost Error Fix**: The `return` statement is the specific fix mentioned in the technical defense. It ensures that once the plan is rendered, the function exits. Previously, it might have fell through to error handlers or other logic, causing "Error" popups even on success.

### Room Detection Badge
```javascript
      if (data.detected_room_type) {
        // Update UI Badge
        badge.textContent = `Detected: ${data.detected_room_type}`;
        
        // Auto-set Dropdown
        document.getElementById('room-type').value = data.detected_room_type;
      }
```
*   **UX Intelligence**: When an image is uploaded, the backend (via YOLO or a Classifier) guesses the room type. The frontend automatically updates the UI dropdown, saving the user a click.

---

## 🏁 CONCLUSION: SYSTEM LIFECYCLE

1.  **Boot**: `config.py` detects 4GB VRAM -> Sets `Low VRAM Mode`.
2.  **Idle**: API waits. No models loaded in VRAM.
3.  **User Uploads**: `upload.py` saves file. `detect.py` (YOLO) runs -> Loads -> Detects -> Unloads to CPU.
4.  **User Plans**: `plan.py` calls Ollama (RAM) to get instructions.
5.  **User Generates**:
    *   `OfflineProvider` requested.
    *   `MemoryManager` ensures VRAM is empty.
    *   `Stable Diffusion` loads (Float16, Sliced Attention).
    *   Image generates (20 steps).
    *   `cleanup()` runs -> VRAM freed.
6.  **Result**: Image sent to frontend canvas.

This architecture treats VRAM as a scarce resource that must be acquired and released transactionally, enabling modern AI on budget hardware.
