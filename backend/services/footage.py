"""
Visual Footage Retriever: Google Veo AI, Pexels Stock, and Procedural Generator.
"""
import os
import subprocess
import requests
import imageio_ffmpeg
from backend.services.veo_ai import generate_veo_clip

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()


def generate_procedural_broll(output_path: str, duration: float, mood: str = "cinematic"):
    duration = max(5.0, duration)
    
    if mood == "dark":
        filter_complex = (
            f"testsrc=duration={duration}:size=1080x1920:rate=30,format=yuv420p,"
            f"drawbox=x=0:y=0:w=1080:h=1920:color=black@1.0:t=fill,"
            f"geq=r='15+10*sin(X/120+T)+25*sin(Y/180-T)':"
            f"g='10+5*sin(X/90-T)+15*sin(Y/140+T)':"
            f"b='40+30*sin(X/80+T*1.2)+35*sin(Y/110-T*0.8)',"
            f"boxblur=8:1"
        )
    elif mood == "energetic":
        filter_complex = (
            f"testsrc=duration={duration}:size=1080x1920:rate=30,format=yuv420p,"
            f"drawbox=x=0:y=0:w=1080:h=1920:color=black@1.0:t=fill,"
            f"geq=r='60+50*sin(X/100+T*2)':"
            f"g='20+20*sin(Y/120+T*1.5)':"
            f"b='90+60*cos(X/90-T*2.2)',"
            f"boxblur=10:1"
        )
    else:
        filter_complex = (
            f"testsrc=duration={duration}:size=1080x1920:rate=30,format=yuv420p,"
            f"drawbox=x=0:y=0:w=1080:h=1920:color=black@1.0:t=fill,"
            f"geq=r='18+15*sin(X/140+T*0.7)':"
            f"g='24+20*cos(Y/160-T*0.9)':"
            f"b='55+35*sin((X+Y)/200+T*1.1)',"
            f"boxblur=12:1"
        )

    cmd = [
        FFMPEG_EXE,
        "-y",
        "-f", "lavfi",
        "-i", filter_complex,
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path


def fetch_or_create_footage(
    keywords: list,
    total_duration: float,
    output_dir: str,
    mood: str = "cinematic",
    pexels_api_key: str = "",
    veo_prompt: str = "",
    veo_api_key: str = ""
) -> list:
    os.makedirs(output_dir, exist_ok=True)
    video_files = []

    # 1. Check if Google Veo AI mode is requested
    if veo_prompt and (veo_api_key or os.environ.get("GEMINI_API_KEY")):
        try:
            veo_output = os.path.join(output_dir, "veo_scene.mp4")
            generate_veo_clip(
                prompt=veo_prompt,
                output_path=veo_output,
                api_key=veo_api_key,
                duration_seconds=int(total_duration)
            )
            if os.path.exists(veo_output) and os.path.getsize(veo_output) > 1000:
                video_files.append(veo_output)
        except Exception as e:
            print(f"[Footage] Veo generation error fallback: {e}")

    # 2. Check if Pexels API key is present
    if not video_files and pexels_api_key:
        headers = {"Authorization": pexels_api_key}
        for idx, kw in enumerate(keywords[:3]):
            try:
                url = f"https://api.pexels.com/videos/search?query={kw}&orientation=portrait&per_page=1"
                resp = requests.get(url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("videos"):
                        video_files_data = data["videos"][0]["video_files"]
                        best_link = None
                        for vf in video_files_data:
                            if vf.get("height", 0) >= 1080 and vf.get("width", 0) <= 1080:
                                best_link = vf["link"]
                                break
                        if not best_link and video_files_data:
                            best_link = video_files_data[0]["link"]
                            
                        if best_link:
                            vid_path = os.path.join(output_dir, f"pexels_clip_{idx}.mp4")
                            r = requests.get(best_link, stream=True, timeout=15)
                            with open(vid_path, "wb") as f:
                                for chunk in r.iter_content(chunk_size=1024*1024):
                                    if chunk:
                                        f.write(chunk)
                            video_files.append(vid_path)
            except Exception as e:
                print(f"[Footage] Pexels fallback: {e}")

    # 3. Procedural generator fallback
    if not video_files:
        clip_path = os.path.join(output_dir, "procedural_backdrop.mp4")
        generate_procedural_broll(clip_path, total_duration + 2.0, mood=mood)
        video_files.append(clip_path)

    return video_files
