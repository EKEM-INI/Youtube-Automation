"""
FastAPI Backend Server for YouTube Automation Dashboard
Supports both synchronous cloud generation and asynchronous local rendering.
"""
import os
import glob
import uuid
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from backend.generator import start_generation_job, process_video_job, JOBS, OUTPUT_DIR
from backend.services.youtube_upload import upload_video_to_youtube

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = FastAPI(title="1-Click YouTube Shorts Automation", version="1.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class GenerateRequest(BaseModel):
    topic: str
    tone: str = "energetic"
    voice: str = "christopher"
    publish_mode: str = "download"
    pexels_key: str = ""
    veo_key: str = ""
    use_veo: bool = False


class UploadRequest(BaseModel):
    filename: str
    title: str
    description: str


@app.get("/")
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "YouTube Automation API running."}


@app.post("/api/generate")
def create_video_async(req: GenerateRequest):
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
        
    job_id = start_generation_job(
        topic=req.topic,
        tone=req.tone,
        voice=req.voice,
        publish_mode=req.publish_mode,
        pexels_key=req.pexels_key,
        veo_key=req.veo_key,
        use_veo=req.use_veo
    )
    return {"job_id": job_id, "status": "started"}


@app.post("/api/generate-sync")
def create_video_sync(req: GenerateRequest):
    """
    Synchronous generation for Serverless platforms (Vercel, Lambda) where background threads are frozen.
    """
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
        
    job_id = str(uuid.uuid4())
    process_video_job(
        job_id=job_id,
        topic=req.topic,
        tone=req.tone,
        voice=req.voice,
        publish_mode=req.publish_mode,
        pexels_key=req.pexels_key,
        veo_key=req.veo_key,
        use_veo=req.use_veo
    )
    
    job_info = JOBS.get(job_id)
    if not job_info or job_info.get("status") == "failed":
        err_msg = job_info.get("error", "Unknown error during rendering") if job_info else "Failed to start"
        raise HTTPException(status_code=500, detail=err_msg)
        
    return job_info


@app.get("/api/job/{job_id}")
def get_job_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found or expired on serverless instance.")
    return JOBS[job_id]


@app.get("/api/video/{filename}")
def get_video_file(filename: str):
    video_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video not found.")
    return FileResponse(video_path, media_type="video/mp4", filename=filename)


@app.get("/api/videos")
def list_videos():
    videos = []
    pattern = os.path.join(OUTPUT_DIR, "*.mp4")
    for file_path in glob.glob(pattern):
        stat = os.stat(file_path)
        filename = os.path.basename(file_path)
        videos.append({
            "filename": filename,
            "url": f"/api/video/{filename}",
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
