"""
FastAPI Backend Server for YouTube Automation Dashboard
"""
import os
import glob
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from backend.generator import start_generation_job, JOBS
from backend.services.youtube_upload import upload_video_to_youtube

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

app = FastAPI(title="1-Click YouTube Shorts Automation", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FRONTEND_DIR, exist_ok=True)

# Mount generated videos
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")
# Mount frontend files
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class GenerateRequest(BaseModel):
    topic: str
    tone: str = "energetic"
    voice: str = "christopher"
    publish_mode: str = "download"  # "download" or "youtube"
    pexels_key: str = ""


class UploadRequest(BaseModel):
    filename: str
    title: str
    description: str


@app.get("/")
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "YouTube Automation API running. Build frontend/index.html."}


@app.post("/api/generate")
def create_video(req: GenerateRequest):
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
        
    job_id = start_generation_job(
        topic=req.topic,
        tone=req.tone,
        voice=req.voice,
        publish_mode=req.publish_mode,
        pexels_key=req.pexels_key
    )
    return {"job_id": job_id, "status": "started"}


@app.get("/api/job/{job_id}")
def get_job_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found.")
    return JOBS[job_id]


@app.get("/api/videos")
def list_videos():
    videos = []
    pattern = os.path.join(OUTPUT_DIR, "*.mp4")
    for file_path in glob.glob(pattern):
        stat = os.stat(file_path)
        filename = os.path.basename(file_path)
        videos.append({
            "filename": filename,
            "url": f"/output/{filename}",
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created_at": stat.st_mtime
        })
    videos.sort(key=lambda x: x["created_at"], reverse=True)
    return {"videos": videos}


@app.post("/api/upload-youtube")
def manual_youtube_upload(req: UploadRequest):
    video_path = os.path.join(OUTPUT_DIR, req.filename)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found.")
        
    result = upload_video_to_youtube(
        video_path=video_path,
        title=req.title,
        description=req.description
    )
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
