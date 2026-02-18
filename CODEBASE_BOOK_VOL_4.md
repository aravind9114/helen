# COMPLETE CODEBASE EXPLANATION - VOLUME 4
## The Modern Stack (React + SQL)

**Context**: This volume explains the architecture found in your active `dark-universe` workspace. This represents the **Next-Generation** version of the project, replacing the file-based/Vanilla JS approach (Volumes 1-3) with a robust Database and Component-based Frontend.

---

## 22. Modern Backend: `backend/main.py` (FastAPI + SQL)

Unlike the Volume 1 backend which used JSON files (`history.json`), this version interacts with a real SQL database.

### Database Session Management
```python
def get_db():
    db = database.SessionLocal()
    try: yield db
    finally: db.close()
```
*   **Dependency Injection**: Every API endpoint uses `Depends(get_db)`. This ensures that a fresh database connection is opened for the request and securely closed afterwards, preventing connection leaks.

### Project Creation (SQL Transaction)
```python
@app.post("/projects")
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
```
*   **ORM (Object-Relational Mapping)**: Instead of manually writing `INSERT INTO projects...`, we create a python object `models.Project`. SQLAlchemy translates this to SQL.
*   **Safety**: `schemas.ProjectCreate` validates the input (name, budget) before it ever touches the DB.

### Layout Persistence
```python
@app.post("/projects/{project_id}/layout")
def save_layout(...):
    # 1. Clear old layout
    db.query(models.LayoutItem).filter(...).delete()
    # 2. Insert new items
    for item in layout.items:
        db.add(models.LayoutItem(...))
    db.commit()
```
*   **State Saving**: Saves the exact X/Y coordinates, rotation, and scale of every furniture piece so the user can resume editing later.

---

## 23. Database Layer: `backend/models.py` & `seed.py`

### Schema Definition (`models.py`)
*   **`Project`**: Stores high-level metadata (Budget Cap, Room Type).
*   **`Item`**: The Furniture Catalog (Price, Image URL, Vendor).
*   **`LayoutItem`**: junction table linking `Project` + `Item` + `Position (x,y)`.

### Catalog Seeding (`seed.py`)
```python
def seed_data():
    items = [ { "name": "Modern Grey Sofa", "price": 899.99 ... } ]
    for item in items: db.add(models.Item(**item))
```
*   **Purpose**: Pre-populates the SQLite database with demo furniture assets so the `FurnitureLibrary` isn't empty on first run.

---

## 24. React Frontend: `frontend/src/App.jsx`

**The Router**.
```jsx
<Routes>
  <Route path="/create" element={<CreateProject />} />
  <Route path="/project/:id/editor" element={<EditorPage />} />
</Routes>
```
*   **Navigation Flow**: Create -> Upload -> Editor -> Summary.

---

## 25. The Core Editor: `frontend/src/pages/EditorPage.jsx`

This is the most complex file in the modern stack. It uses `react-konva` to render an HTML5 Canvas that supports complex drag-and-drop interactions.

### Canvas Layering
```jsx
<Stage>
    <Layer> <BackgroundImage /> </Layer>
    <Layer> 
        {layoutItems.map(item => <URLImage />)} 
    </Layer>
</Stage>
```
*   **Layer 1 (Background)**: The user's uploaded room photo.
*   **Layer 2 (Furniture)**: Draggable images overlaying the room.

### Drag & Drop Logic
```jsx
const handleDrop = (e) => {
    // 1. Get Mouse Position relative to Stage
    const pointerPosition = stage.getPointerPosition();
    // 2. Add Item to State
    setLayoutItems([...layoutItems, { x: pointerPosition.x, ... }]);
}
```
*   **Interaction**: Handles the event when a user drags a sofa from the sidebar and drops it onto the canvas. It calculates exactly where to place it.

### Transformer (The Blue Box)
```jsx
{isSelected && (
    <Transformer
        boundBoxFunc={(oldBox, newBox) => { ... }}
    />
)}
```
*   **UX**: Renders the resize handles (corners) around the selected furniture, allowing the user to rotate and scale items to fit the perspective.

---

## 26. Component Library

### `FurnitureLibrary.jsx`
*   Fetches the catalog (`/catalog`) from FastAPI.
*   Renders the sidebar grid.
*   Uses HTML5 `draggable="true"` and `e.dataTransfer` to pass furniture data to the Canvas.

### `CreateProject.jsx`
*   A form that collects Name, Room Type, and Budget.
*   POSTs to `/projects` to initialize the database entry.

---

## 🏁 Summary of Differences

| Feature | Legacy Version (Vol 1-3) | Modern Version (Vol 4) |
| :--- | :--- | :--- |
| **Backend** | File-based (`json`) | SQL Database (`sqlite`) |
| **Frontend** | Vanilla JS + HTML | React + Vite + Tailwind |
| **Canvas** | Basic Drawing | `react-konva` (Advanced Drag/Drop) |
| **State** | Global Object | React State Hooks |
| **AI** | **Real (SD/YOLO)** | **Mocked** (Currently) |

**Important Note**: Your `dark-universe` workspace currently uses **Mock AI** (`backend/main.py` lines 72-80). It returns fake image URLs. The "Real AI" logic explained in Volumes 1-3 resides in your other codebase. Merging these (Real AI backend + React Frontend) would be the ultimate goal.
