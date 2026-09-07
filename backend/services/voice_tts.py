"""
Voiceover and Subtitle Generator using Edge-TTS (100% Free, Zero API Keys)
Produces crystal-clear neural voiceovers and word-timed subtitles.
"""
import asyncio
import os
import re
import uuid
import edge_tts
import tempfile

VOICE_MAP = {
    "christopher": "en-US-ChristopherNeural",  # Deep, Authoritative Male
    "guy": "en-US-GuyNeural",                  # Energetic, Viral Male
    "jenny": "en-US-JennyNeural",              # Smooth, Engaging Female
    "aria": "en-US-AriaNeural",                # Dynamic, Clear Female
    "ryan": "en-GB-RyanNeural",                # British Male Narrator
    "sonia": "en-GB-SoniaNeural"               # British Female Narrator
}


def format_ass_time(seconds: float) -> str:
    """Formats seconds into ASS timestamp format H:MM:SS.cs"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{cs:02d}"


async def _generate_voice_and_subtitles_async(text: str, voice_key: str, output_audio_path: str, output_ass_path: str, rate: str = "+5%"):
    voice_name = VOICE_MAP.get(voice_key.lower(), "en-US-ChristopherNeural")
    communicate = edge_tts.Communicate(text, voice_name, rate=rate)
    
    audio_data = bytearray()
    word_boundaries = []
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            word_boundaries.append({
                "text": chunk["text"],
                "offset": chunk["offset"] / 10_000_000,
                "duration": chunk["duration"] / 10_000_000
            })
            
    with open(output_audio_path, "wb") as f:
        f.write(audio_data)
        
    ass_dialogues = []
    chunk_size = 3
    
    if word_boundaries:
        for i in range(0, len(word_boundaries), chunk_size):
            group = word_boundaries[i:i + chunk_size]
            phrase_start = group[0]["offset"]
            phrase_end = group[-1]["offset"] + group[-1]["duration"] + 0.1
            words_text = " ".join([w["text"] for w in group]).upper()
            formatted_text = f"{{\\c&H0000FFFF&}}{words_text}{{\\c&H00FFFFFF&}}"
            start_str = format_ass_time(phrase_start)
            end_str = format_ass_time(phrase_end)
            ass_dialogues.append(f"Dialogue: 0,{start_str},{end_str},ShortsStyle,,0,0,0,,{formatted_text}")
    else:
        duration_est = max(5.0, len(text.split()) * 0.4)
        ass_dialogues.append(
            f"Dialogue: 0,0:00:00.00,{format_ass_time(duration_est)},ShortsStyle,,0,0,0,,{{\\c&H0000FFFF&}}{text[:40].upper()}"
        )
        
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ShortsStyle,Arial Black,75,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,10,6,2,60,60,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass_content = ass_header + "\n".join(ass_dialogues)
    
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)
        
    return output_audio_path, output_ass_path


def generate_voiceover(text: str, voice_key: str, output_audio_path: str, output_ass_path: str):
    """Synchronous caller for voiceover and subtitle generation."""
    return asyncio.run(_generate_voice_and_subtitles_async(text, voice_key, output_audio_path, output_ass_path))


async def _synthesize_preview_async(text: str, voice_key: str, output_path: str, speed_pct: int = 0):
    voice_name = VOICE_MAP.get(voice_key.lower(), "en-US-ChristopherNeural")
    rate_str = f"+{speed_pct}%" if speed_pct >= 0 else f"{speed_pct}%"
    communicate = edge_tts.Communicate(text, voice_name, rate=rate_str)
    await communicate.save(output_path)
    return output_path


def synthesize_preview_audio(text: str, voice_key: str = "christopher", speed_pct: int = 0, output_dir: str = "") -> str:
    """Synthesizes preview audio file on-demand."""
    if not output_dir:
        output_dir = tempfile.gettempdir()
    os.makedirs(output_dir, exist_ok=True)
    filename = f"preview_{uuid.uuid4().hex[:8]}.mp3"
    filepath = os.path.join(output_dir, filename)
    asyncio.run(_synthesize_preview_async(text, voice_key, filepath, speed_pct))
    return filepath, filename
