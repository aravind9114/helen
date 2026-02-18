import sys
import os
from pathlib import Path

# Add project root to Python path to allow running directly
# This fixes "ModuleNotFoundError: No module named 'backend'" when running 'python main.py'
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.append(str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.core.config import settings
from backend.api.routes import router as api_router
from backend.services.logging import logger
import uvicorn
import torch

# Create FastAPI app
app = FastAPI(
    title="Budget-Constrained Interior Design AI",
    description="AI-powered interior design with offline and online providers",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static file serving
app.mount(
    "/generated",
    StaticFiles(directory=str(settings.generated_dir)),
    name="generated"
)

app.mount(
    "/uploads",
    StaticFiles(directory=str(settings.uploads_dir)),
    name="uploads"
)

app.mount(
    "/masks",
    StaticFiles(directory=str(settings.storage_dir / "masks")),
    name="masks"
)

# Include API Router
app.include_router(api_router)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "message": "Budget-Constrained Interior Design AI Backend V2",
        "version": "2.0.0"
    }

@app.get("/health")
async def health_check():
    """Extended health check with system information."""
    cuda_available = torch.cuda.is_available()
    cuda_device = torch.cuda.get_device_name(0) if cuda_available else "N/A"
    
    return {
        "status": "healthy",
        "cuda_available": cuda_available,
        "cuda_device": cuda_device,
        "mode": "offline-first"
    }

if __name__ == "__main__":
    logger.info("Starting Backend V2")
    uvicorn.run(
        "backend.main:app",  # Adjusted import path for new structure
        host=settings.host,
        port=settings.port,
        reload=True
    )
