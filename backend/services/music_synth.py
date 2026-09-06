"""
Procedural Background Music Generator using FFmpeg audio synthesis.
Generates calming, cinematic, or upbeat royalty-free backing music tracks.
"""
import os
import subprocess
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()


def generate_background_music(output_path: str, duration: float = 60.0, mood: str = "cinematic"):
    """
    Generates a royalty-free ambient backing track matching the mood using FFmpeg audio synthesis.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    duration = max(10.0, duration)
    
    if mood == "dark":
        # Deep drone bass with sub-harmonics
        audio_filter = (
            f"aevalsrc=exprs='0.08*sin(2*PI*55*t)+0.04*sin(2*PI*110*t)+0.02*sin(2*PI*165*t)':"
            f"s=44100:d={duration},lowpass=f=200,volume=0.8"
        )
    elif mood == "energetic":
        # Pulsing synth bass rhythm
        audio_filter = (
            f"aevalsrc=exprs='0.06*sin(2*PI*130*t)*mod(t*2,1)+0.04*sin(2*PI*260*t)*mod(t*4,1)':"
            f"s=44100:d={duration},lowpass=f=500,volume=0.8"
        )
    else:
        # Warm ambient cinematic chord pad (F-maj / C-maj intervals)
        audio_filter = (
            f"aevalsrc=exprs='0.05*sin(2*PI*220*t)+0.04*sin(2*PI*277.18*t)+0.03*sin(2*PI*329.63*t)+0.02*sin(2*PI*440*t)':"
            f"s=44100:d={duration},lowpass=f=450,volume=0.7"
        )

    cmd = [
        FFMPEG_EXE,
        "-y",
        "-f", "lavfi",
        "-i", audio_filter,
        "-t", str(duration),
        "-c:a", "aac",
        "-b:a", "192k",
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path
