"""
FastAPI Backend Server for YouTube Automation & AI Channel Studio SaaS
Powers all 20 modules: Dashboard, Niche Research, AI Ideas, Script Studio, Voiceover,
Google Veo Video Engine, Thumbnails, SEO, Calendar, Multi-Agent Pipeline, Repurposer, Analytics, and Monetization CRM.
"""
import os
import glob
import uuid
import random
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from backend.generator import start_generation_job, process_video_job, JOBS, OUTPUT_DIR
from backend.services.script_ai import generate_script
from backend.services.research_engine import get_all_niches, analyze_niche_opportunity
from backend.services.agents import run_autonomous_agent_pipeline, AGENTS_CONFIG
from backend.services.repurposer import repurpose_content
from backend.services.thumbnail_ai import generate_thumbnail_concepts
from backend.services.seo_optimizer import analyze_and_optimize_seo
from backend.services.youtube_upload import upload_video_to_youtube

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = FastAPI(title="AutoShorts AI — YouTube Automation Studio", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# Pydantic Schemas
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
    format_type: str = "shorts"  # "shorts" or "longform"
    tone: str = "energetic"
    style: str = "documentary"


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


class UploadRequest(BaseModel):
    filename: str
    title: str
    description: str


# -------------------------------------------------------------
# 1. CORE & DASHBOARD ENDPOINTS
# -------------------------------------------------------------
@app.get("/")
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AutoShorts AI Suite 2.0 API Running."}


@app.get("/api/dashboard/stats")
def get_dashboard_stats(channel: str = "Apex Tech"):
    """
    Returns executive metrics, AI Channel Brain advice, recent uploads, and channel status.
    """
    channels_data = {
        "Apex Tech": {
            "subscribers": "142,850",
            "subs_change": "+8,420 (this mo)",
            "views_28d": "1,840,290",
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
                    "action_topic": "Use Dynamic Highlighted Subtitles"
                }
            ]
        },
        "Dark Psychology": {
            "subscribers": "328,100",
            "subs_change": "+19,400 (this mo)",
            "views_28d": "4,120,800",
            "views_change": "+38.4%",
            "watch_time_hrs": "98,400",
            "est_revenue": "$12,850.00",
            "revenue_change": "+28.1%",
            "avg_ctr": "13.2%",
            "avg_view_duration": "88%",
            "niche": "🧠 Human Behavior & Psychology",
            "ai_brain_recommendations": [
                {
                    "type": "opportunity",
                    "title": "High-RPM Gap: Negotiation Micro-Expressions",
                    "detail": "Competitor query 'how to read silence in deals' has high search volume and low competition.",
                    "urgency": "High Impact",
                    "action_topic": "The 5-Second Silence Rule in Negotiations"
                }
            ]
        }
    }
    return channels_data.get(channel, channels_data["Apex Tech"])


# -------------------------------------------------------------
# 2. NICHE & COMPETITOR RESEARCH
# -------------------------------------------------------------
@app.get("/api/research/niches")
def get_niches():
    return {"niches": get_all_niches()}


@app.get("/api/research/opportunity")
def get_niche_opportunity(niche_id: str = "dark_psychology"):
    return analyze_niche_opportunity(niche_id)


# -------------------------------------------------------------
# 3. AI VIDEO IDEAS & VIRAL SCANNER
# -------------------------------------------------------------
@app.get("/api/ideas/generate")
def generate_ideas(niche: str = "AI Tech", count: int = 6):
    ideas = [
        {"title": f"The Secret {niche} Protocol That 99% Of People Miss", "viral_score": 96, "angle": "Controversial / Pattern Interrupt", "est_views": "150K - 400K", "rpm_potential": "High ($18+)"},
        {"title": f"Why Everything You Were Told About {niche} Is A Lie", "viral_score": 94, "angle": "Debunking / Mythbuster", "est_views": "120K - 350K", "rpm_potential": "Medium-High"},
        {"title": f"How To Master {niche} In 6 Months (Step-by-Step Blueprint)", "viral_score": 91, "angle": "Actionable Roadmap", "est_views": "80K - 220K", "rpm_potential": "Very High ($24+)"},
        {"title": f"3 Shocking Facts About {niche} That Will Keep You Up At Night", "viral_score": 98, "angle": "Curiosity Gap / Mystery", "est_views": "250K - 600K", "rpm_potential": "High ($15+)"},
        {"title": f"The Real Reason The Top 1% Are Investing In {niche}", "viral_score": 89, "angle": "Authority / Insider Secrets", "est_views": "90K - 280K", "rpm_potential": "Maximum ($32+)"}
    ]
    return {"niche": niche, "ideas": ideas}


# -------------------------------------------------------------
# 4. AI SCRIPT STUDIO (SHORTS & LONG-FORM)
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
            ],
            "visual_prompts": [
                "Cinematic 4K establishing shot with dramatic volumetric lighting, 16:9",
                "Macro slow-motion shot of digital data stream particles, 16:9",
                "Dramatic portrait with dark vignette and neon rim light, 16:9"
            ]
        }
    else:
        # Shorts format
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


# -------------------------------------------------------------
# 5. AI THUMBNAIL STUDIO & A/B TESTER
# -------------------------------------------------------------
@app.post("/api/thumbnails/generate")
def create_thumbnails(req: ThumbnailRequest):
    return generate_thumbnail_concepts(topic=req.topic, tone=req.tone or "viral")


# -------------------------------------------------------------
# 6. YOUTUBE SEO OPTIMIZER
# -------------------------------------------------------------
@app.post("/api/seo/analyze")
def optimize_seo(req: SEORequest):
    return analyze_and_optimize_seo(title=req.title, topic=req.topic or req.title, niche=req.niche or "general")


# -------------------------------------------------------------
# 7. CONTENT REPURPOSER
# -------------------------------------------------------------
@app.post("/api/repurpose")
def run_repurpose(req: RepurposeRequest):
    return repurpose_content(source_title=req.title, source_text=req.text or "", video_url=req.video_url or "")


# -------------------------------------------------------------
# 8. AUTONOMOUS MULTI-AGENT PIPELINE
# -------------------------------------------------------------
@app.post("/api/agents/run-pipeline")
def execute_agent_pipeline(req: AgentPipelineRequest):
    return run_autonomous_agent_pipeline(
        topic=req.topic,
        niche=req.niche or "psychology",
        voice=req.voice or "christopher",
        channel=req.channel or "Apex Tech"
    )


# -------------------------------------------------------------
# 9. MONETIZATION & SPONSORSHIP CRM
# -------------------------------------------------------------
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
# 10. CONTENT CALENDAR EVENTS
# -------------------------------------------------------------
@app.get("/api/calendar/events")
def get_calendar_events():
    return {
        "events": [
            {"date": "2026-09-08", "time": "15:00", "title": "3 Dark Psychology Secrets Everyday", "format": "Shorts", "channel": "Apex Tech", "status": "Ready to Publish"},
            {"date": "2026-09-10", "time": "16:30", "title": "Google Veo 2 vs OpenAI Sora Full Deep Dive", "format": "Long-form", "channel": "Apex Tech", "status": "Script Drafted"},
            {"date": "2026-09-12", "time": "14:00", "title": "The 5-Second Silence Trick in Business", "format": "Shorts", "channel": "Dark Psychology", "status": "Rendering (Veo)"},
            {"date": "2026-09-15", "time": "15:00", "title": "The Scariest Sound Recorded in Deep Space", "format": "Shorts", "channel": "Apex Tech", "status": "Scheduled"}
        ]
    }


# -------------------------------------------------------------
# 11. VIDEO RENDERING ENDPOINTS
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
