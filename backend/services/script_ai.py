"""
AI Script Generator for YouTube Shorts
Generates high-retention, viral short scripts with Google Veo visual scene prompts.
"""
import random
import os
import json

PRESET_SCRIPTS = {
    "psychology": [
        {
            "title": "3 Dark Psychology Tricks You Experience Everyday 🧠 #shorts",
            "hook": "Here are 3 psychological tricks people use on you without you realizing.",
            "body": "First, the illusion of choice. When someone gives you two options, your brain forgets that 'no' is also an option. Second, the door in the face technique. They ask for something huge, get rejected, and then ask for what they actually wanted all along. Third, silent pressure. If someone pauses after you speak, your instinct is to keep talking and reveal your secrets. Which one have you fallen for?",
            "keywords": ["brain psychology", "mysterious person thinking", "neon city night", "dark portrait"],
            "veo_prompt": "Cinematic 8K close up of a human brain with glowing electric blue and gold synapses, dark atmospheric background, photorealistic 9:16",
            "music_mood": "dark"
        },
        {
            "title": "Why Your Brain Loves Being Lazy (The Science) ⚡ #shorts",
            "hook": "Stop blaming yourself for being lazy. Your brain was designed for it.",
            "body": "Thousands of years ago, conserving energy was the only way our ancestors survived harsh winters and famines. Every time you hesitate to start a task, your brain is actively trying to save dopamine for emergencies. The secret hack? The 5-second rule. Count down five, four, three, two, one, and physically move before your brain hits the emergency brake.",
            "keywords": ["human brain glowing", "clock ticking fast", "running athlete focus", "modern city hyperlapse"],
            "veo_prompt": "Futuristic digital clock ticking in high speed with glowing neon particles exploding in slow motion, cinematic 9:16",
            "music_mood": "energetic"
        }
    ],
    "motivation": [
        {
            "title": "The Rule That Changes Everything in 6 Months 🚀 #shorts",
            "hook": "If you feel stuck in life right now, listen to this for 30 seconds.",
            "body": "Most people overestimate what they can do in a day, but brutally underestimate what they can do in six months of relentless focus. The world doesn't reward perfection. It rewards momentum. Stop waiting for the perfect day, the perfect mood, or the perfect time. Wake up, put in the work quietly, and let your results make the noise.",
            "keywords": ["luxury penthouse sunrise", "hard workout gym", "city skyline drone", "supercar driving night"],
            "veo_prompt": "Cinematic aerial drone flight over a futuristic glowing metropolis skyline at golden hour sunset, 8k resolution, 9:16",
            "music_mood": "energetic"
        },
        {
            "title": "Never Tell People Your Plans (Do This Instead) 🤫 #shorts",
            "hook": "The biggest mistake ambitious people make is talking too soon.",
            "body": "When you announce your goals to people, your brain releases premature dopamine, tricking you into feeling like you've already accomplished it. Move in silence. Don't announce your moves before you make them. Shock them with your execution, not your intentions.",
            "keywords": ["chess player thinking", "dark luxury room", "foggy mountain road", "silhouette walking"],
            "veo_prompt": "Moody cinematic shot of a grandmaster moving a crystal chess piece on a dark marble table with dramatic rim light, 9:16",
            "music_mood": "cinematic"
        }
    ],
    "space": [
        {
            "title": "The Scariest Sound Recorded in Deep Space 🌌 #shorts",
            "hook": "NASA pointed their sensors at a massive black hole, and recorded this.",
            "body": "Two hundred and forty million light years away in the Perseus galaxy cluster, acoustic waves ripple through superheated gas. Sound cannot travel through empty vacuum, but space gas is dense enough to carry soundwaves fifty-seven octaves below middle C. It is the sound of an cosmic titan devouring entire stars in absolute darkness.",
            "keywords": ["black hole galaxy space", "nebula deep cosmos", "telescope stars rotating", "planet earth atmosphere"],
            "veo_prompt": "Hyper-realistic simulation of an enormous gravitational black hole warping starlight in a cosmic purple nebula, 8k 9:16",
            "music_mood": "dark"
        }
    ]
}


def generate_script(topic: str, tone: str = "energetic", custom_prompt: str = "") -> dict:
    topic_clean = topic.strip().lower()

    matched_category = None
    if any(k in topic_clean for k in ["psychology", "mind", "brain", "human", "behavior"]):
        matched_category = "psychology"
    elif any(k in topic_clean for k in ["motivation", "discipline", "mindset", "success", "grind"]):
        matched_category = "motivation"
    elif any(k in topic_clean for k in ["space", "universe", "planet", "galaxy", "nasa", "earth"]):
        matched_category = "space"

    if matched_category and matched_category in PRESET_SCRIPTS:
        sample = random.choice(PRESET_SCRIPTS[matched_category])
        full_text = f"{sample['hook']} {sample['body']}"
        return {
            "title": sample["title"],
            "hook": sample["hook"],
            "body": sample["body"],
            "full_text": full_text,
            "keywords": sample["keywords"],
            "veo_prompt": sample.get("veo_prompt", f"Cinematic photorealistic 8k video of {topic}, dramatic lighting, 9:16 vertical"),
            "music_mood": sample.get("music_mood", "cinematic"),
            "description": f"{sample['title']}\n\nSubscribe for daily mind-blowing facts & insights! #shorts #viral #facts"
        }

    capitalized_topic = topic.strip().title()
    hook = f"Here is the shocking truth about {capitalized_topic} that almost nobody talks about."
    body = (
        f"When you dive deep into {topic.strip()}, everything you thought you knew gets turned upside down. "
        f"First, key patterns emerge when you look at the underlying science. "
        f"Second, the greatest breakthrough came from questioning standard assumptions. "
        f"If you want to master {topic.strip()}, remember this: consistency beats intensity every single time. "
        f"Hit subscribe if this opened your eyes."
    )
    full_text = f"{hook} {body}"
    keywords = [f"{topic} close up", "dramatic cinematic light", "abstract digital motion", "epic landscape horizon"]

    return {
        "title": f"The Shocking Truth About {capitalized_topic} 🤯 #shorts",
        "hook": hook,
        "body": body,
        "full_text": full_text,
        "keywords": keywords,
        "veo_prompt": f"Epic cinematic shot representing {capitalized_topic} with dramatic volumetric lighting and particle motion, 8K, 9:16 vertical",
        "music_mood": "energetic" if "energetic" in tone.lower() else "cinematic",
        "description": f"Learn the truth about {capitalized_topic}! Subscribe for more viral shorts. #shorts #{topic.replace(' ', '')}"
    }
