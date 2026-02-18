# How to Run the Project

This guide provides step-by-step instructions to set up and run the Budget-Constrained AI Interior Design System.

---

## Prerequisites

### Required Software

- **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** - Python package installer (comes with Python)
- **Web Browser** - Chrome, Firefox, or Edge (modern versions)

### Optional (for GPU acceleration)

- **NVIDIA GPU** with 4GB+ VRAM
- **CUDA Toolkit 12.1+** - [Download CUDA](https://developer.nvidia.com/cuda-downloads)

---

## Installation

### Step 1: Download the Project

Clone or download the project to your computer:

```bash
cd C:\Users\[YourName]\Desktop
# If you have the zip file, extract it
# Or if using git: git clone [repository-url]
```

### Step 2: Set Up Backend

#### 2.1 Navigate to Backend Directory

```bash
cd interior-designer-ai\backend
```

#### 2.2 Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

#### 2.3 Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

**Note**: This will download ~3GB of files including PyTorch and Stable Diffusion models.

#### 2.4 (Optional) Install GPU Support

If you have an NVIDIA GPU with CUDA:

```bash
# Uninstall CPU-only PyTorch
pip uninstall torch torchvision

# Install CUDA-enabled PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

#### 2.5 (Optional) Configure Online Providers

If you want to use Replicate or HuggingFace:

1. Create a `.env` file in the `backend/` directory
2. Add your API tokens:
   ```
   REPLICATE_API_TOKEN=r8_your_token_here
   HF_API_TOKEN=hf_your_token_here
   ```

**Note**: Offline mode works without any API tokens!

### Step 3: Verify Installation

Test that everything is installed correctly:

```bash
python test_setup.py
```

You should see:

- ✓ All required packages installed
- ✓ CUDA available (if you have GPU) or CPU mode
- ✓ Directories created successfully

---

## Running the Application

You need **TWO terminals** - one for backend, one for frontend.

### Terminal 1: Start Backend

```bash
# Navigate to the PROJECT ROOT (NOT backend!)
cd C:\Users\[YourName]\Desktop\helentest\interior-designer-ai

# Activate virtual environment
venv\Scripts\activate

# Start the backend server (as a module)
python -m backend.main
```

**Expected output:**

```
[INFO] Starting Budget-Constrained AI Interior Design Backend
[INFO] ✓ CUDA detected: NVIDIA GeForce RTX 4060
[INFO] Provider: offline (Diffusers img2img)
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✅ Backend is now running at `http://localhost:8000`**

**Keep this terminal open!**

---

### Terminal 2: Start Frontend

Open a **NEW terminal** window:

```bash
# Navigate to frontend
cd C:\Users\[YourName]\Desktop\interior-designer-ai\frontend

# Start simple HTTP server
python -m http.server 8080
```

**Expected output:**

```
Serving HTTP on :: port 8080 (http://[::]:8080/) ...
```

**✅ Frontend is now running at `http://localhost:8080`**

**Keep this terminal open too!**

---

### Step 3: Open in Browser

1. Open your web browser
2. Go to: **http://localhost:8080**
3. You should see the Interior Design AI interface

---

## Using the Application

### Feature 1: AI Design Generation

#### 1. Upload an Image

- Drag and drop a room photo, or
- Click the upload zone to browse files
- Supported formats: JPG, PNG, WEBP
- Max size: 10MB

#### 2. Configure Settings

- **Room Type**: Select the type of room (Living Room, Bedroom, etc.)
- **Design Style**: Choose aesthetic (Minimalist, Modern, Vintage, Professional)
- **AI Provider**:
  - **Offline (Local GPU)** - Fast, free, works without internet (recommended)
  - **Replicate** - Online, requires API token
  - **HuggingFace** - Online, requires API token
- **Budget**: Enter your budget in Rupees (₹)

#### 3. Generate Design

- Click the **"Generate Design"** button
- Wait forgeneration (8-10 seconds with GPU, 2-5 minutes with CPU)
- View the results!

#### 4. Review Results

- **AI Design**: See the redesigned room
- **Budget Status**: Check if design is within budget
- **Generation Info**: View provider used and time taken
- **Download**: Click the download button to save the image

---

### Feature 2: Furniture Detection & Shopping

#### 1. Upload Furnished Room Image

- Use the same upload zone
- Image should contain visible furniture

#### 2. Click "🔍 Re-Design (Detect Furniture)"

- Wait ~1-2 seconds (GPU) or ~5-10 seconds (CPU)

#### 3. View Detected Furniture

- See detected items with confidence scores
- Example: "couch - 90% confident"

#### 4. Explore Suggestions (Tabs)

**📦 Local Replacements Tab:**

- View 6-8 catalog items per detected category
- Prices range from ₹6.5k to ₹2.25L
- Sorted by price (budget to premium)
- Example: Compact 2-Seater Sofa - ₹18,000 (Pepperfry)

**🌐 Online Suggestions Tab:**

- View 5 vendor links per detected category
- Direct links to shopping websites
- Vendors: Pepperfry, Urban Ladder, IKEA, Amazon, WoodenStreet
- Approximate prices shown in snippets
- Click any link to open vendor website

#### 5. Check Remaining Budget

- System calculates cheapest replacement cost
- Shows remaining budget after purchases

---

## Troubleshooting

### Backend won't start

**Error: `ModuleNotFoundError`**

- Solution: Make sure virtual environment is activated and run `pip install -r requirements.txt`

**Error: `CUDA out of memory`**

- Solution: Close other GPU-intensive programs, or use CPU mode

**Error: `Port 8000 already in use`**

- Solution: Stop other programs using port 8000, or change port in `main.py`

### Frontend won't load

**Error: `Address already in use`**

- Solution: Use a different port: `python -m http.server 8081`

**Can't access http://localhost:8080**

- Solution: Check that the HTTP server is running in the frontend directory

### Image not displaying

**CORS error in browser console**

- Solution: Make sure you're accessing via `http://localhost:8080`, not opening `file://` directly
- Solution: Check that backend is running and accessible

**Image generates but doesn't show**

- Solution: Hard refresh the browser (Ctrl+Shift+R)
- Solution: Check browser console (F12) for errors

### Slow generation

**Taking 5+ minutes**

- This is normal for CPU mode
- Solution: Install CUDA-enabled PyTorch for GPU acceleration

**GPU not being used**

- Check: Run `test_setup.py` to verify CUDA is detected
- Solution: Reinstall PyTorch with CUDA support

---

## Stopping the Application

### To stop the servers:

1. Go to each terminal
2. Press `Ctrl+C`
3. Type `deactivate` in the backend terminal to deactivate virtual environment

### To restart:

Follow the "Running the Application" steps again

---

## System Requirements

### Minimum (CPU Mode)

- Windows 10/11, Linux, or macOS
- Python 3.10+
- 8GB RAM
- 15GB free disk space
- Any modern web browser

### Recommended (GPU Mode)

- NVIDIA GPU with 4GB+ VRAM (RTX 2060, RTX 3060, RTX 4060, etc.)
- CUDA 12.1+
- 16GB RAM
- 20GB free disk space
- Windows 10/11 or Linux

---

## Performance Guide

### AI Design Generation

| Hardware       | Generation Time | Quality |
| -------------- | --------------- | ------- |
| RTX 4060 (GPU) | 8-10 seconds    | High    |
| RTX 3060 (GPU) | 15-20 seconds   | High    |
| CPU (8-core)   | 2-3 minutes     | High    |
| CPU (4-core)   | 4-5 minutes     | High    |

### Furniture Detection

| Hardware       | Detection Time |
| -------------- | -------------- |
| RTX 4060 (GPU) | 1-2 seconds    |
| RTX 3060 (GPU) | 2-3 seconds    |
| CPU (8-core)   | 5-10 seconds   |
| CPU (4-core)   | 10-15 seconds  |

### Vendor Suggestions

| Feature        | Response Time |
| -------------- | ------------- |
| Local Catalog  | Instant (0ms) |
| Online Vendors | Instant (0ms) |

**Note**: Both CPU and GPU produce identical quality results - GPU is just faster!

---

## Next Steps

**Core Documentation:**

- Read `PROJECT_SUMMARY.md` for complete project overview
- Read `ARCHITECTURE.md` to understand how the system works
- Read `BACKEND_CODE_EXPLAINED.md` to understand backend implementation
- Read `FRONTEND_CODE_EXPLAINED.md` to understand frontend implementation

**Feature Documentation:**

- Read `YOLO_FEATURE_EXPLAINED.md` for in-depth detection explanation (600+ lines)
- Read `ONLINE_VENDOR_SUGGESTIONS.md` for vendor directory feature
- Read `SEARCH_CATALOG_IMPROVEMENTS.md` for latest updates

**Experimentation:**

- Try different design styles and room types
- Test furniture detection with various room photos
- Explore both local and online suggestions tabs
- Experiment with budget constraints
- (Optional) Set up online providers for comparison

---

## Support

If you encounter issues:

1. Check the terminal output for error messages
2. Review the troubleshooting section above
3. Verify all prerequisites are installed
4. Check that both backend and frontend are running
5. Try restarting both servers

---

**Congratulations! Your AI Interior Design System is now running!** 🎉
