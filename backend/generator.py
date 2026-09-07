"""
Master Pipeline Orchestrator for 1-Click YouTube Short Creation
Supports Google Veo AI, Edge-TTS, and dynamic cloud/serverless storage.
"""
import os
import time
import uuid
import tempfile
import threading
from backend.services.script_ai import generate_script
from backend.services.voice_tts import generate_voiceover
from backend.services.footage import fetch_or_create_footage
from backend.services.music_synth import generate_background_music
from backend.services.video_engine import render_short_video
from backend.services.youtube_upload import upload_video_to_youtube

# Determine writable output directory (handles Vercel / AWS Lambda / Local)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    test_out = os.path.join(BASE_DIR, "output")
    os.makedirs(test_out, exist_ok=True)
    # Test write permission
    test_file = os.path.join(test_out, ".perm_test")
    with open(test_file, "w") as f:
        f.write("1")
    os.remove(test_file)
    OUTPUT_DIR = test_out
    TEMP_DIR = os.path.join(BASE_DIR, "temp")
except Exception:
    # Serverless / Read-only environment fallback to /tmp
    OUTPUT_DIR = os.path.join(tempfile.gettempdir(), "yt_output")
    TEMP_DIR = os.path.join(tempfile.gettempdir(), "yt_temp")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

# In-memory status tracker for jobs
JOBS = {}


def process_video_job(
    job_id: str,
    topic: str,
    tone: str,
    voice: str,
    publish_mode: str,
    pexels_key: str = "",
    veo_key: str = "",
    use_veo: bool = False
):
    try:
        JOBS[job_id] = {
            "status": "running",
            "progress": 10,
            "step": "🧠 Crafting viral hook and script with Google Veo prompts...",
            "topic": topic,
            "error": None,
            "result": None
        }
        
        job_temp = os.path.join(TEMP_DIR, job_id)
        os.makedirs(job_temp, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # 1. Script Generation
        script_data = generate_script(topic=topic, tone=tone)
        JOBS[job_id]["script"] = script_data
        JOBS[job_id]["progress"] = 30
        JOBS[job_id]["step"] = f"🎙️ Generating realistic AI voiceover ({voice})..."
        
        # 2. Voiceover & Dynamic Subtitles
        audio_path = os.path.join(job_temp, "voiceover.mp3")
        ass_path = os.path.join(job_temp, "subtitles.ass")
        generate_voiceover(
            text=script_data["full_text"],
            voice_key=voice,
            output_audio_path=audio_path,
            output_ass_path=ass_path
        )
        
        JOBS[job_id]["progress"] = 55
        if use_veo or veo_key:
            JOBS[job_id]["step"] = "🎬 Generating cinematic AI scenes with Google Veo..."
        else:
            JOBS[job_id]["step"] = "🎬 Sourcing vertical HD visual footage & background music..."
        
        # 3. Footage (Google Veo / Pexels / Procedural) & Music
        footage_paths = fetch_or_create_footage(
            keywords=script_data["keywords"],
            total_duration=45.0,
            output_dir=job_temp,
            mood=script_data.get("music_mood", "cinematic"),
            pexels_api_key=pexels_key,
            veo_prompt=script_data.get("veo_prompt", ""),
            veo_api_key=veo_key
        )
        
        music_path = os.path.join(job_temp, "bg_music.aac")
        generate_background_music(
            output_path=music_path,
            duration=60.0,
            mood=script_data.get("music_mood", "cinematic")
        )
        
        JOBS[job_id]["progress"] = 75
        JOBS[job_id]["step"] = "⚡ Rendering 1080x1920 Short with animated captions..."
        
        # 4. FFmpeg Video Assembly
        safe_title = "".join([c if c.isalnum() else "_" for c in script_data["title"][:30]])
        final_filename = f"Short_{safe_title}_{job_id[:6]}.mp4"
        final_mp4_path = os.path.join(OUTPUT_DIR, final_filename)
        
        render_short_video(
            audio_path=audio_path,
            subtitles_ass_path=ass_path,
            footage_paths=footage_paths,
            music_path=music_path,
            output_mp4_path=final_mp4_path
        )
        
        JOBS[job_id]["progress"] = 90
        JOBS[job_id]["step"] = "🚀 Finalizing video and metadata..."
        
        # 5. YouTube Upload if requested
        upload_result = None
        if publish_mode == "youtube":
            JOBS[job_id]["step"] = "📤 Uploading directly to YouTube..."
            upload_result = upload_video_to_youtube(
                video_path=final_mp4_path,
                title=script_data["title"],
                description=script_data["description"]
            )
            
        JOBS[job_id]["progress"] = 100
        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["step"] = "🎉 Video created successfully!"
        JOBS[job_id]["result"] = {
            "filename": final_filename,
            "video_url": f"/api/video/{final_filename}",
            "title": script_data["title"],
            "description": script_data["description"],
            "upload_info": upload_result
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)
        JOBS[job_id]["step"] = f"❌ Error: {str(e)}"


def start_generation_job(
    topic: str,
    tone: str,
    voice: str,
    publish_mode: str,
    pexels_key: str = "",
    veo_key: str = "",
    use_veo: bool = False
) -> str:
    job_id = str(uuid.uuid4())
    thread = threading.Thread(
        target=process_video_job,
        args=(job_id, topic, tone, voice, publish_mode, pexels_key, veo_key, use_veo),
        daemon=True
    )
    thread.start()
    return job_id
