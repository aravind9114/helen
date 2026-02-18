# COMPLETE CODEBASE EXPLANATION - VOLUME 6
## Project Configuration & Build System

**Context**: This volume covers the essential "glue" code that makes the project run: The Build System, Configuration Files, and Dependencies.

---

## 31. Frontend Entry Point: `frontend/src/main.jsx`

**Purpose**: The absolute starting point of the React application.

```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
```
*   **`createRoot`**: React 18's new way to mount the app into the `index.html`'s `<div id="root">`.
*   **`BrowserRouter`**: Wraps the entire app to enable routing (URL navigation).
*   **`StrictMode`**: A development tool that highlights potential problems (like side effects in render) by running components twice.

---

## 32. Build Configuration: `frontend/vite.config.js`

**Purpose**: Configures Vite, the ultra-fast build tool used for this project.

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
```
*   **Simplicity**: Unlike Webpack (which needs 500 lines), Vite works almost zero-config.
*   **`plugins: [react()]`**: Enables Fast Refresh (HMR). When you save a file, the browser updates instantly without a full reload.

---

## 33. Global Styles: `frontend/src/index.css`

**Purpose**: Sets up the Design System variables and utility classes.

### CSS Variables
```css
:root {
  --primary: #4f46e5;     /* Indigo */
  --bg-color: #f9fafb;    /* Light Gray */
  --text-main: #111827;   /* Dark Text */
}
```
*   **Effect**: Changing `--primary` here updates the color of *every button and link* in the entire app instantly.

### Utility Classes
```css
.btn-primary {
  background-color: var(--primary);
  color: white;
}
.card {
  background: var(--card-bg);
  box-shadow: 0 1px 3px ...;
}
```
*   **"Mini-Tailwind"**: Defines reusable classes used in `CreateProject.jsx` and other files.

---

## 34. Dependencies: `frontend/package.json`

**Purpose**: Lists all the libraries powering the UI.

*   **`react` / `react-dom`**: The core framework.
*   **`react-router-dom`**: Navigation.
*   **`konva` / `react-konva`**: The Canvas engine for dragging furniture.
*   **`axios`**: HTTP Client (talks to backend).
*   **`lucide-react`**: The icon set (Home, Save, Upload icons).

---

## 35. Backend Dependencies: `backend/requirements.txt`

**Purpose**: Lists Python libraries required for the server.

*   **`fastapi` / `uvicorn`**: The Web Server.
*   **`sqlalchemy`**: Database ORM.
*   **`Pillow`**: Image processing logic (used in `generate_assets.py`).

---

## 36. Placeholder AI Folders: `backend/ai/`

You will notice folders like `backend/ai/diffusion` and `backend/ai/vision` containing only `__init__.py`.

*   **Status**: These are architectural placeholders.
*   **Purpose**: In the "Modern Stack" (`dark-universe`), the complex AI logic (Volumes 1-3) has not yet been ported over. These folders are reserved for when you merge the Legacy AI code into this modern React architecture.

---

## 🏁 Final Verification

Comparing your file system against these 6 Volumes:

| Directory | Files | Covered In |
| :--- | :--- | :--- |
| `backend/` | `main.py`, `models.py`, `schemas.py`, `seed.py`, `database.py` | **Vol 4** |
| `backend/` | `generate_assets.py` | **Vol 5** |
| `backend/` | `requirements.txt` | **Vol 6** |
| `backend/ai` | Placeholder folders | **Vol 6** |
| `frontend/src/pages` | `EditorPage`, `UploadPage`, `SummaryPage`, `CreateProject` | **Vol 4 & 5** |
| `frontend/src/components` | `BudgetPanel`, `Layout`, `FurnitureLibrary` | **Vol 4 & 5** |
| `frontend/src` | `App.jsx`, `api.js` | **Vol 4** |
| `frontend/src` | `main.jsx`, `index.css` | **Vol 6** |
| `frontend/` | `vite.config.js`, `package.json` | **Vol 6** |
| `legacy_code/` | `offline_diffusers.py`, `memory.py`, etc. | **Vol 1-3** |

**Status**: 100% Coverage. Every file has been explained.
