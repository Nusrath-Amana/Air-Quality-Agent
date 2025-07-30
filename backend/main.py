from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agent_loader import agent
from typing import Optional, Dict, Any
import os
import time
from pathlib import Path

# Create FastAPI app
app = FastAPI()

# Create directories
os.makedirs("generated_images", exist_ok=True)

# Mount static files 
app.mount("/generated_images", StaticFiles(directory="generated_images"), name="generated_images")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    error: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Clean up old images on startup"""
    now = time.time()
    for f in Path("generated_images").glob("*.png"):
        if f.stat().st_mtime < now - 3600:  # 1 hour old
            try:
                f.unlink()
            except:
                pass


@app.post("/ask", response_model=QueryResponse)
async def ask_query(request: QueryRequest) -> Dict[str, Any]:
    # Delete old images
    for f in Path("generated_images").glob("*.png"):
        try:
            f.unlink()
        except:
            pass

    try:
        result = agent.query(request.query) # your existing function

        image_path = None
        image_files = list(Path("generated_images").glob("*.png"))
        if image_files:
            image_path = f"/generated_images/{os.path.basename(image_files[0])}"

        return {
            "success": True,
            "result": str(result),
            "image_url": image_path,
        }

    except Exception as e:
        return {
            "success": False,
            "result": "Error occurred.",
            "image_url": None,
            "error": str(e),
        }