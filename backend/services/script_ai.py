"""
AI Script Generator for YouTube Shorts
Generates high-retention, viral short scripts with hooks, visual keywords, and metadata.
"""
import random
import os
import json
import requests

PRESET_SCRIPTS = {
    "psychology": [
        {
            "title": "3 Dark Psychology Tricks You Experience Everyday 🧠 #shorts",
            "hook": "Here are 3 psychological tricks people use on you without you realizing.",
            "body": "First, the illusion of choice. When someone gives you two options, your brain forgets that 'no' is also an option. Second, the door in the face technique. They ask for something huge, get rejected, and then ask for what they actually wanted all along. Third, silent pressure. If someone pauses after you speak, your instinct is to keep talking and reveal your secrets. Which one have you fallen for?",
            "keywords": ["brain psychology", "mysterious person thinking", "neon city night", "dark portrait"],
            "music_mood": "dark"
        },
        {
            "title": "Why Your Brain Loves Being Lazy (The Science) ⚡ #shorts",
            "hook": "Stop blaming yourself for being lazy. Your brain was designed for it.",
            "body": "Thousands of years ago, conserving energy was the only way our ancestors survived harsh winters and famines. Every time you hesitate to start a task, your brain is actively trying to save dopamine for emergencies. The secret hack? The 5-second rule. Count down five, four, three, two, one, and physically move before your brain hits the emergency brake.",
            "keywords": ["human brain glowing", "clock ticking fast", "running athlete focus", "modern city hyperlapse"],
            "music_mood": "energetic"
        }
    ],
    "motivation": [
        {
            "title": "The Rule That Changes Everything in 6 Months 🚀 #shorts",
            "hook": "If you feel stuck in life right now, listen to this for 30 seconds.",
            "body": "Most people overestimate what they can do in a day, but brutally underestimate what they can do in six months of relentless focus. The world doesn't reward perfection. It rewards momentum. Stop waiting for the perfect day, the perfect mood, or the perfect time. Wake up, put in the work quietly, and let your results make the noise.",
            "keywords": ["luxury penthouse sunrise", "hard workout gym", "city skyline drone", "supercar driving night"],
            "music_mood": "energetic"
        },
        {
            "title": "Never Tell People Your Plans (Do This Instead) 🤫 #shorts",
            "hook": "The biggest mistake ambitious people make is talking too soon.",
            "body": "When you announce your goals to people, your brain releases premature dopamine, tricking you into feeling like you've already accomplished it. Move in silence. Don't announce your moves before you make them. Shock them with your execution, not your intentions.",
            "keywords": ["chess player thinking", "dark luxury room", "foggy mountain road", "silhouette walking"],
            "music_mood": "cinematic"
        }
    ],
    "space": [
        {
            "title": "The Scariest Sound Recorded in Deep Space 🌌 #shorts",
            "hook": "NASA pointed their sensors at a massive black hole, and recorded this.",
            "body": "Two hundred and forty million light years away in the Perseus galaxy cluster, acoustic waves ripple through superheated gas. Sound cannot travel through empty vacuum, but space gas is dense enough to carry soundwaves fifty-seven octaves below middle C. It is the sound of an cosmic titan devouring entire stars in absolute darkness.",
            "keywords": ["black hole galaxy space", "nebula deep cosmos", "telescope stars rotating", "planet earth atmosphere"],
            "music_mood": "dark"
        },
        {
            "title": "What If Earth Stopped Spinning for 1 Second? 🌍 #shorts",
            "hook": "If the Earth stopped spinning for just one single second, here is what happens.",
            "body": "At the equator, the Earth rotates at roughly one thousand miles per hour. If it stopped abruptly, everything not bolted down to bedrock would instantly fly eastward at supersonic speed. Giant tidal waves hundreds of feet high would sweep across continents in minutes. Luckily, our planet's momentum is locked for billions of years.",
            "keywords": ["planet earth spinning", "ocean waves crashing", "storm clouds time lapse", "cosmic galaxy view"],
            "music_mood": "cinematic"
        }
    ],
    "wealth": [
        {
            "title": "The Money Rule The Rich Never Teach You 💰 #shorts",
            "hook": "Rich people don't work for money. They make money work for them.",
            "body": "The middle class trades hours for dollars. The wealthy build assets that generate cashflow while they sleep. If you have only one income stream, you are exactly one step away from zero. Start building digital leverage, invest in compounding assets, and buy your freedom.",
            "keywords": ["gold bullion coins", "modern architecture mansion", "stock market chart green", "city skyline sunset"],
            "music_mood": "energetic"
        }
    ],
    "mystery": [
        {
            "title": "The Unsolved Mystery of the Siberian Crater 🕳️ #shorts",
            "hook": "In 2014, helicopter pilots discovered a massive bottomless hole in Siberia.",
            "body": "Deep in the remote Russian tundra, a crater over one hundred and sixty feet wide suddenly opened up out of nowhere. Trees were thrown hundreds of feet outwards, indicating an enormous underground explosion. Scientists believe ancient methane gas trapped beneath permafrost for thousands of years suddenly burst through the crust.",
            "keywords": ["deep mysterious cave", "arctic snow blizzard", "underground glowing cave", "drone mountain exploration"],
            "music_mood": "dark"
        }
    ]
}


def generate_script(topic: str, tone: str = "energetic", custom_prompt: str = "") -> dict:
    """
    Generates a high-retention viral YouTube Short script.
    """
    topic_clean = topic.strip().lower()

    # Check for matched preset
    matched_category = None
    if any(k in topic_clean for k in ["psychology", "mind", "brain", "human", "behavior"]):
        matched_category = "psychology"
    elif any(k in topic_clean for k in ["motivation", "discipline", "mindset", "success", "grind"]):
        matched_category = "motivation"
    elif any(k in topic_clean for k in ["space", "universe", "planet", "galaxy", "nasa", "earth"]):
        matched_category = "space"
    elif any(k in topic_clean for k in ["money", "wealth", "rich", "finance", "crypto", "business"]):
        matched_category = "wealth"
    elif any(k in topic_clean for k in ["mystery", "unsolved", "creepy", "dark", "secret", "strange"]):
        matched_category = "mystery"

    if matched_category and matched_category in PRESET_SCRIPTS:
        sample = random.choice(PRESET_SCRIPTS[matched_category])
        full_text = f"{sample['hook']} {sample['body']}"
        return {
            "title": sample["title"],
            "hook": sample["hook"],
            "body": sample["body"],
            "full_text": full_text,
            "keywords": sample["keywords"],
            "music_mood": sample.get("music_mood", "cinematic"),
            "description": f"{sample['title']}\n\nSubscribe for daily mind-blowing facts & insights! #shorts #viral #facts"
        }

    # Generate smart contextual script for custom topics
    capitalized_topic = topic.strip().title()
    hook = f"Here is the shocking truth about {capitalized_topic} that almost nobody talks about."
    body = (
        f"When you dive deep into {topic.strip()}, everything you thought you knew gets turned upside down. "
        f"First, experts discovered that key patterns emerge when you look at the underlying science. "
        f"Second, the greatest breakthrough came from questioning standard assumptions. "
        f"If you want to master {topic.strip()} and stay ahead of the curve, remember this: consistency beats intensity every single time. "
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
        "music_mood": "energetic" if "energetic" in tone.lower() else "cinematic",
        "description": f"Learn the truth about {capitalized_topic}! Subscribe for more viral shorts. #shorts #{topic.replace(' ', '')}"
    }
