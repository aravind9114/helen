# COMPLETE CODEBASE EXPLANATION - VOLUME 5
## Auxiliary Components & Tools

**Context**: This final volume covers the remaining utility scripts and UI components in the `dark-universe` workspace that support the main application flow.

---

## 27. Asset Generation: `backend/generate_assets.py`

 **Purpose**: A developer utility script used to create "Placeholder" images for the catalog when real images aren't available.

```python
def create_placeholder_image(path, text, size, color):
    img = Image.new('RGB', size, color=color)
    d = ImageDraw.Draw(img)
    d.text((x, y), text, ...)
    img.save(path)
```
*   **Logic**: Uses the `Pillow` library to draw simple colored rectangles with text (e.g., a brown square labeled "Sofa").
*   **Usage**: Run `python generate_assets.py` once to populate `static/catalog/` with dummy files so the frontend `FurnitureLibrary` has something to show.

---

## 28. Upload Page: `frontend/src/pages/UploadPage.jsx`

**Purpose**: Handles image ingestion and initial AI processing (mocked).

### File Selection
```jsx
<input type="file" onChange={handleFileChange} />
// Previews image immediately using URL.createObjectURL()
```

### The "Generate" Flow
```jsx
const handleGenerate = async () => {
    // 1. Upload Original
    await api.post(`/projects/${id}/upload`, formData);
    // 2. Request Variations (Mocked)
    const response = await api.post(`/projects/${id}/generate`, ...);
    setVariations(response.data.variations);
}
```
*   **Variations Grid**: displays the 3 "Mock Variations" returned by the backend. Clicking one sets it as the `selectedImage` passed to the Editor.

---

## 29. Summary Page: `frontend/src/pages/SummaryPage.jsx`

**Purpose**: The final "Invoice" or "Manifest".

### Fetching Data
```jsx
const fetchSummary = async () => {
   const res = await api.get(`/projects/${id}/summary`);
   setSummary(res.data);
}
```
*   **Endpoint**: Calls `backend/main.py:get_summary`.

### Features
*   **Budget Status**: Calculates if `total_cost > budget_cap` and shows a Red (Over Budget) or Green (Within Budget) badge.
*   **Export JSON**: `handleDownloadJson()` creates a dynamic `data:text/json` link to download the project data.
*   **Export Image**: `handleDownloadImage()` downloads the screenshot captured in the Editor phase.

---

## 30. UI Components

### `BudgetPanel.jsx`
**Purpose**: A live sidebar widget in the Editor.
```jsx
const percentage = Math.min((totalCost / budgetCap) * 100, 100);
// Renders a progress bar
<div style={{ width: `${percentage}%` }} />
```
*   **Reactivity**: Updates instantly as items are added/removed from the canvas.
*   **Visual feedback**: Bar turns Yellow at 75% and Red at 100%.

### `Layout.jsx`
**Purpose**: The common page wrapper.
```jsx
<header> ... </header>
<main> <Outlet /> </main>
<footer> ... </footer>
```
*   **React Router Outlet**: This is where individual pages (`EditorPage`, `UploadPage`) are rendered within the common shell.

---

## 🏁 Final Conclusion

You now have a complete set of documentation covering **every single file** across your project's history and current state:

*   **Vol 1-3**: The Deep Python AI backend (Logic, Agents, ML).
*   **Vol 4-5**: The Modern Full-Stack App (React Interface, SQL DB, Tools).

This concludes the chronological explanation of the entire codebase.
