"""
FastAPI Backend Server for YouTube Automation & AI Channel Studio SaaS
Powers Google Plugins: YouTube Data API v3 OAuth, Google Veo, Google Trends, Edge-TTS, and all 20 modules.
"""
import os
import glob
import uuid
import random
import tempfile
from fastapi import FastAPI, HTTPException, Body, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional, List

from backend.generator import start_generation_job, process_video_job, JOBS, OUTPUT_DIR, TEMP_DIR
from backend.services.script_ai import generate_script
from backend.services.voice_tts import synthesize_preview_audio
from backend.services.research_engine import get_all_niches, analyze_niche_opportunity, get_google_trends_keywords
from backend.services.agents import run_autonomous_agent_pipeline, AGENTS_CONFIG
from backend.services.repurposer import repurpose_content
from backend.services.thumbnail_ai import generate_thumbnail_concepts
from backend.services.seo_optimizer import analyze_and_optimize_seo
from backend.services.youtube_upload import upload_video_to_youtube
from backend.services.youtube_oauth import (
    get_oauth_auth_url,
    handle_oauth_callback,
    get_current_channel_info,
    disconnect_channel
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = FastAPI(title="AutoShorts AI — YouTube Automation Studio", version="2.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# In-memory calendar database
CALENDAR_EVENTS = [
    {"id": "ev_1", "date": "2026-09-08", "time": "15:00", "title": "3 Dark Psychology Secrets Everyday", "format": "Shorts", "channel": "Apex Tech", "status": "Ready to Publish"},
    {"id": "ev_2", "date": "2026-09-10", "time": "16:30", "title": "Google Veo 2 vs OpenAI Sora Full Deep Dive", "format": "Long-form", "channel": "Apex Tech", "status": "Script Drafted"},
    {"id": "ev_3", "date": "2026-09-12", "time": "14:00", "title": "The 5-Second Silence Trick in Business", "format": "Shorts", "channel": "Dark Psychology", "status": "Rendering (Veo)"},
    {"id": "ev_4", "date": "2026-09-15", "time": "15:00", "title": "The Scariest Sound Recorded in Deep Space", "format": "Shorts", "channel": "Apex Tech", "status": "Scheduled"}
]


# Pydantic Request Models
class GenerateRequest(BaseModel):
    topic: str
    tone: str = "energetic"
    voice: str = "christopher"
    publish_mode: str = "download"
    pexels_key: str = ""
    veo_key: str = ""
    use_veo: bool = False


class ScriptFullRequest(BaseModel):
    topic: str
    format_type: str = "shorts"
    tone: str = "energetic"
    style: str = "documentary"


class VoicePreviewRequest(BaseModel):
    text: str
    voice: str = "christopher"
    speed_pct: int = 0


class RepurposeRequest(BaseModel):
    title: str
    text: Optional[str] = ""
    video_url: Optional[str] = ""


class SEORequest(BaseModel):
    title: str
    topic: Optional[str] = ""
    niche: Optional[str] = "general"


class ThumbnailRequest(BaseModel):
    topic: str
    tone: Optional[str] = "viral"


class AgentPipelineRequest(BaseModel):
    topic: str
    niche: Optional[str] = "psychology"
    voice: Optional[str] = "christopher"
    channel: Optional[str] = "Apex Tech"


class CalendarAddRequest(BaseModel):
    title: str
    date: str
    time: str
    format: str = "Shorts"
    channel: str = "Apex Tech"


class UploadRequest(BaseModel):
    filename: str
    title: str
    description: str


# -------------------------------------------------------------
# 1. CORE & YOUTUBE OAUTH ENDPOINTS (GOOGLE PLUGIN)
# -------------------------------------------------------------
@app.get("/")
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AutoShorts AI Suite 2.5 API Running."}


@app.get("/api/youtube/auth-url")
def get_youtube_auth_url(client_id: str = "", redirect_uri: str = "http://localhost:8000/api/youtube/callback"):
    """
    Returns Google OAuth2 authorization URL for connecting a YouTube channel.
    """
    url = get_oauth_auth_url(client_id=client_id, redirect_uri=redirect_uri)
    return {"auth_url": url}


@app.get("/api/youtube/callback")
def handle_youtube_oauth_callback(code: str = "", error: str = ""):
    """
    Handles redirect from Google OAuth consent screen.
    """
    if error:
        return RedirectResponse(url="/?oauth_error=" + error)
    handle_oauth_callback(code=code)
    return RedirectResponse(url="/?oauth_success=true")


@app.get("/api/youtube/channel-info")
def get_connected_channel():
    """
    Returns live connected YouTube channel statistics.
    """
    return get_current_channel_info()


@app.post("/api/youtube/disconnect")
def disconnect_youtube_channel():
    return disconnect_channel()


# -------------------------------------------------------------
# 2. DASHBOARD & AI BRAIN
# -------------------------------------------------------------
@app.get("/api/dashboard/stats")
def get_dashboard_stats(channel: str = "Apex Tech"):
    ch_info = get_current_channel_info()
    if ch_info.get("connected"):
        subs = ch_info["subscribers"]
        views = ch_info["total_views"]
        title = ch_info["title"]
    else:
        subs = "142,850" if channel == "Apex Tech" else "328,100"
        views = "1,840,290" if channel == "Apex Tech" else "4,120,800"
        title = channel

    return {
        "channel_title": title,
        "subscribers": subs,
        "subs_change": "+8,420 (this mo)",
        "views_28d": views,
        "views_change": "+24.8%",
        "watch_time_hrs": "48,200",
        "est_revenue": "$6,420.50",
        "revenue_change": "+18.2%",
        "avg_ctr": "11.4%",
        "avg_view_duration": "82%",
        "niche": "🤖 AI & Future Tech",
        "ai_brain_recommendations": [
            {
                "type": "opportunity",
                "title": "Viral Spike Detected: Google Veo 2 Topics",
                "detail": "Your last Veo Short outperformed channel average by +142%. Create 3 more follow-ups this week.",
                "urgency": "High Impact",
                "action_topic": "Google Veo 2 vs OpenAI Sora 2026 Comparison"
            },
            {
                "type": "retention",
                "title": "Hook Retention Optimization",
                "detail": "Adding a 1-second countdown visual in 0-3s increased your Average Percentage Viewed by +12%.",
                "urgency": "Pro Tip",
                "action_topic": "The 5-Second Silence Rule in Negotiations"
            }
        ]
    }


# -------------------------------------------------------------
# 3. RESEARCH & GOOGLE TRENDS PLUGIN
# -------------------------------------------------------------
@app.get("/api/research/niches")
def get_niches():
    return {"niches": get_all_niches()}


@app.get("/api/research/opportunity")
def get_niche_opportunity(niche_id: str = "dark_psychology"):
    return analyze_niche_opportunity(niche_id)


@app.get("/api/research/trends")
def get_trends(query: str = "ai automation"):
    return get_google_trends_keywords(query)


# -------------------------------------------------------------
# 4. AI SCRIPT & VOICE STUDIO
# -------------------------------------------------------------
@app.post("/api/scripts/generate-full")
def create_full_script(req: ScriptFullRequest):
    if req.format_type == "longform":
        return {
            "title": f"The Complete Documentary: The Rise of {req.topic.title()}",
            "format": "Long-form (8-12 Mins)",
            "estimated_read_time": "9 mins 30 secs",
            "word_count": 1420,
            "chapters": [
                {"timestamp": "0:00", "title": "The Hook: The Hidden Catalyst", "content": f"What if everything you knew about {req.topic} was engineered to keep you looking in the wrong direction? Today, we uncover the verified truth..."},
                {"timestamp": "1:45", "title": "Chapter 1: The Initial Discovery", "content": "To understand where we are going, we have to look back at how the underlying pattern was first discovered..."},
                {"timestamp": "4:30", "title": "Chapter 2: The Critical Turning Point", "content": "When researchers first measured the feedback loop, the results shocked the entire scientific community..."},
                {"timestamp": "7:15", "title": "Chapter 3: The Future Implication", "content": "Over the next decade, those who adapt to this protocol will hold an asymmetric advantage..."},
                {"timestamp": "8:50", "title": "Conclusion & Action Protocol", "content": "Before you leave, remember this golden rule. Hit subscribe and leave your thoughts below."}
            ]
        }
    else:
        script_data = generate_script(topic=req.topic, tone=req.tone)
        return {
            "title": script_data["title"],
            "format": "Vertical Short (30-50s)",
            "hook": script_data["hook"],
            "body": script_data["body"],
            "full_text": script_data["full_text"],
            "word_count": len(script_data["full_text"].split()),
            "estimated_read_time": "36 secs",
            "veo_prompt": script_data.get("veo_prompt", "8K 9:16 vertical"),
            "music_mood": script_data.get("music_mood", "energetic")
        }


@app.post("/api/voice/synthesize")
def synthesize_voice(req: VoicePreviewRequest):
    """
    On-demand voiceover synthesizer for Voiceover Studio.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    filepath, filename = synthesize_preview_audio(
        text=req.text,
        voice_key=req.voice,
        speed_pct=req.speed_pct,
        output_dir=TEMP_DIR
    )
    return {
        "status": "success",
        "audio_url": f"/api/audio/{filename}",
        "voice": req.voice,
        "filename": filename
    }


@app.get("/api/audio/{filename}")
def stream_preview_audio(filename: str):
    path = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return FileResponse(path, media_type="audio/mpeg", filename=filename)


# -------------------------------------------------------------
# 5. THUMBNAILS, SEO & REPURPOSING
# -------------------------------------------------------------
@app.post("/api/thumbnails/generate")
def create_thumbnails(req: ThumbnailRequest):
    return generate_thumbnail_concepts(topic=req.topic, tone=req.tone or "viral")


@app.post("/api/seo/analyze")
def optimize_seo(req: SEORequest):
    return analyze_and_optimize_seo(title=req.title, topic=req.topic or req.title, niche=req.niche or "general")


@app.post("/api/repurpose")
def run_repurpose(req: RepurposeRequest):
    return repurpose_content(source_title=req.title, source_text=req.text or "", video_url=req.video_url or "")


@app.post("/api/agents/run-pipeline")
def execute_agent_pipeline(req: AgentPipelineRequest):
    return run_autonomous_agent_pipeline(
        topic=req.topic,
        niche=req.niche or "psychology",
        voice=req.voice or "christopher",
        channel=req.channel or "Apex Tech"
    )


# -------------------------------------------------------------
# 6. CALENDAR & MONETIZATION
# -------------------------------------------------------------
@app.get("/api/calendar/events")
def get_calendar_events():
    return {"events": CALENDAR_EVENTS}


@app.post("/api/calendar/add")
def add_calendar_event(req: CalendarAddRequest):
    new_ev = {
        "id": f"ev_{uuid.uuid4().hex[:6]}",
        "title": req.title,
        "date": req.date,
        "time": req.time,
        "format": req.format,
        "channel": req.channel,
        "status": "Scheduled"
    }
    CALENDAR_EVENTS.insert(0, new_ev)
    return {"status": "added", "event": new_ev}


@app.post("/api/calendar/delete")
def delete_calendar_event(event_id: str = Body(..., embed=True)):
    global CALENDAR_EVENTS
    CALENDAR_EVENTS = [ev for ev in CALENDAR_EVENTS if ev.get("id") != event_id]
    return {"status": "deleted"}


@app.get("/api/monetization/stats")
def get_monetization_stats():
    return {
        "monthly_totals": {
            "total_earnings": "$18,450.00",
            "adsense_revenue": "$11,250.00",
            "sponsorship_revenue": "$5,800.00",
            "affiliate_revenue": "$1,400.00",
            "projected_annual": "$221,400.00"
        },
        "sponsorship_calculator": {
            "avg_views_per_video": "85,000",
            "niche_cpm_rate": "$30.00 - $45.00 CPM",
            "recommended_integration_rate": "$2,500 - $3,800 / video",
            "recommended_dedicated_rate": "$6,000 - $8,500 / video"
        },
        "active_brand_deals": [
            {"brand": "NordPass / NordVPN", "stage": "Contract Signed", "deal_value": "$3,200", "deliverable": "60s Midroll Integration", "due_date": "Sept 15, 2026"},
            {"brand": "Cursor / AI IDE", "stage": "Proposal Sent", "deal_value": "$4,500", "deliverable": "Dedicated AI Review", "due_date": "Sept 22, 2026"},
            {"brand": "Hostinger", "stage": "Paid & Completed", "deal_value": "$2,800", "deliverable": "Shorts Pinned Link", "due_date": "Sept 01, 2026"}
        ]
    }


# -------------------------------------------------------------
# 7. VIDEO RENDERING & STREAMING
# -------------------------------------------------------------
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
