"""
Core Video Rendering Engine using FFmpeg
Combines voiceover, background music, video clips, and dynamic subtitles into a vertical 1080x1920 Short.
"""
import os
import subprocess
import json
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()


def get_media_duration(file_path: str) -> float:
    """Gets exact duration of audio/video file using ffprobe/ffmpeg."""
    cmd = [
        FFMPEG_EXE,
        "-i", file_path,
        "-f", "null",
        "-"
    ]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    # Parse Duration: 00:00:15.34 from stderr
    import re
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", result.stderr)
    if match:
        hrs, mins, secs = match.groups()
        return int(hrs) * 3600 + int(mins) * 60 + float(secs)
    return 15.0


def render_short_video(
    audio_path: str,
    subtitles_ass_path: str,
    footage_paths: list,
    music_path: str,
    output_mp4_path: str
) -> str:
    """
    Renders the complete 9:16 vertical Short video.
    """
    os.makedirs(os.path.dirname(output_mp4_path), exist_ok=True)
    duration = get_media_duration(audio_path)
    
    # Base directory for subtitles to avoid Windows path colon escaping issues
    work_dir = os.path.dirname(os.path.abspath(subtitles_ass_path))
    ass_filename = os.path.basename(subtitles_ass_path)
    
    primary_video = footage_paths[0]
    
    # Filter graph:
    # 1. Scale and crop video to 1080x1920 (9:16)
    # 2. Burn in ASS dynamic animated subtitles
    # 3. Mix voiceover (1.0) and background music (0.12)
    
    video_filter = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,"
        f"ass={ass_filename}[v]"
    )
    
    audio_filter = (
        f"[1:a]volume=1.0[voice];"
        f"[2:a]volume=0.12,aloop=loop=-1:size=2e+09[bgm];"
        f"[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]"
    )

    cmd = [
        FFMPEG_EXE,
        "-y",
        "-stream_loop", "-1", "-i", os.path.abspath(primary_video),
        "-i", os.path.abspath(audio_path),
        "-i", os.path.abspath(music_path),
        "-filter_complex", f"{video_filter};{audio_filter}",
        "-map", "[v]",
        "-map", "[a]",
        "-t", str(duration + 0.3),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        os.path.abspath(output_mp4_path)
    ]
    
    # Run in work_dir so ffmpeg finds ass file locally
    subprocess.run(cmd, cwd=work_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return output_mp4_path
