# ⚡ AutoShorts AI — 1-Click YouTube Shorts Automation

A complete, 100% free **YouTube Automation Web Application** designed to generate high-retention vertical YouTube Shorts (1080x1920) in 30 seconds from a 3-question prompt.

---

## 🌟 Key Features

- **⚡ 3-Question Instant Wizard:**
  1. Pick or enter any topic/niche.
  2. Select tone & pace (Viral Energy, Dark & Mystery, Cinematic, Inspiring).
  3. Choose human-like neural AI voiceover.
- **🎙️ 100% Free Neural Voiceovers:** Powered by Microsoft Edge-TTS with crystal-clear voices (Christopher, Guy, Jenny, Ryan, Sonia, Aria).
- **📝 Automated Dynamic Animated Subtitles:** Word-level synchronized yellow & white high-impact captions burned directly onto the video.
- **🎬 Procedural & Stock Visual Footage:** Sourcing HD vertical video clips or generating high-speed 1080x1920 motion backdrops offline.
- **🎵 Auto Background Music & Ducking:** Dynamic ambient/synth audio mixing that automatically ducks beneath voiceover speech.
- **🚀 1-Click Publishing & Download:** In-browser MP4 video preview, instant download, or direct upload via YouTube Data API v3.

---

## 📂 Project Structure

```
website automation/
├── backend/
│   ├── app.py                     # FastAPI REST API & static web server
│   ├── generator.py               # Master asynchronous video pipeline coordinator
│   ├── services/
│   │   ├── script_ai.py           # Retention-engineered script generator
│   │   ├── voice_tts.py           # Edge-TTS voice synthesis & ASS subtitle maker
│   │   ├── footage.py             # Pexels API fetcher & procedural video generator
│   │   ├── music_synth.py         # Royalty-free procedural background music
│   │   ├── video_engine.py        # FFmpeg 9:16 vertical video assembler
│   │   └── youtube_upload.py      # YouTube Data API v3 OAuth2 uploader
│   └── requirements.txt           # Python dependencies
├── frontend/
│   ├── index.html                 # Glassmorphic dark-mode web dashboard
│   └── app.js                     # Wizard state, progress tracker & video gallery
├── output/                        # Rendered Full HD 1080x1920 .mp4 videos
└── run.bat                        # 1-Click Windows batch launcher
```

---

## 🚀 Quick Start Guide

### 1. Install Requirements
```bash
pip install -r backend/requirements.txt
```

### 2. Launch the Application
Double-click `run.bat` or run:
```bash
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Open in Browser
Visit **[http://localhost:8000](http://localhost:8000)** to start generating Shorts!

---

## ⚙️ Optional Settings & API Keys

The application works completely offline and free out-of-the-box. Adding optional keys unlocks extra features:
- **Pexels API Key:** Enter in the Settings tab to fetch live stock footage.
- **YouTube OAuth (`client_secrets.json`):** Place in the root directory to enable direct channel publishing.

---

## 📄 License
MIT License. Built for YouTube creators and automation enthusiasts.
