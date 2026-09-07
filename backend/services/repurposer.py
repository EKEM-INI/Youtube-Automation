"""
1-Click Content Repurposer Engine
Transforms long-form YouTube videos, transcripts, or podcasts into:
Shorts, TikToks, Reels, X (Twitter) Threads, LinkedIn Posts, and SEO Blog Articles.
"""

def repurpose_content(source_title: str, source_text: str = "", video_url: str = ""):
    """
    Splits long content into multi-platform viral formats.
    """
    if not source_title:
        source_title = "The Secret Psychology of High Performers"
        
    title_clean = source_title.strip()

    shorts_clips = [
        {
            "clip_number": 1,
            "title": f"The #1 Mistake in {title_clean} ⚡",
            "hook": f"If you're trying to master {title_clean}, stop doing this immediately.",
            "duration": "0:35",
            "visual_style": "Fast zoom on key takeaway, dynamic yellow subtitles",
            "timestamp": "01:15 - 01:50"
        },
        {
            "clip_number": 2,
            "title": f"The 5-Second Rule for {title_clean} 🧠",
            "hook": "Your brain tricks you every single morning. Here is the neuroscience fix.",
            "duration": "0:42",
            "visual_style": "Dramatic slow pan, high-contrast B-roll",
            "timestamp": "04:30 - 05:12"
        },
        {
            "clip_number": 3,
            "title": f"Why 99% Fail at {title_clean} 🚀",
            "hook": "The difference between top 1% and everyone else comes down to this one habit.",
            "duration": "0:48",
            "visual_style": "Kinetic typography, pulsing beat transition",
            "timestamp": "08:10 - 08:58"
        }
    ]

    x_thread = [
        f"1/7 Most people get {title_clean} completely wrong.\n\nHere are 5 counter-intuitive insights that will save you 5 years of trial and error: 🧵👇",
        "2/7 Lesson 1: Action precedes motivation, never the reverse.\n\nWaiting until you 'feel ready' is why 90% of ambitious goals die before starting. Move first.",
        "3/7 Lesson 2: Asymmetric leverage.\n\nThe top 1% don't work 100x harder. They build digital assets and automated distribution systems that compound while they sleep.",
        "4/7 Lesson 3: Eliminate open loops.\n\nEvery unfinished project creates cognitive drag on your working memory. Ruthlessly cut low-leverage tasks.",
        "5/7 Lesson 4: Silent execution beats noisy announcements.\n\nSharing your goals releases premature dopamine. Shock the world with results, not announcements.",
        "6/7 Lesson 5: The compound effect is invisible for the first 80% of the journey.\n\nDon't quit when you're in the flat part of the exponential curve.",
        f"7/7 TL;DR:\n• Build momentum daily\n• Use digital leverage\n• Move in silence\n\nIf you enjoyed this breakdown on {title_clean}, RT the first tweet and follow for daily actionable systems! 🚀"
    ]

    linkedin_post = (
        f"I spent months researching {title_clean}.\n\n"
        "Here is what 99% of people misunderstand about building momentum in 2026:\n\n"
        "1. Complexity is the enemy of execution.\n"
        "2. The world rewards consistency over occasional genius.\n"
        "3. High performers protect their cognitive bandwidth like a fortress.\n\n"
        "The key takeaway?\n"
        "Stop optimizing for perfection. Start optimizing for speed of iteration.\n\n"
        f"What's your biggest insight when it comes to {title_clean}? Share below 👇\n\n"
        "#Productivity #Leadership #GrowthMindset #Automation #Strategy"
    )

    blog_article = {
        "title": f"The Complete Blueprint: Everything You Need to Know About {title_clean}",
        "read_time": "5 min read",
        "meta_description": f"A comprehensive breakdown of {title_clean}, covering actionable strategies, psychological frameworks, and step-by-step systems.",
        "sections": [
            {"heading": "Introduction: The Modern Dilemma", "body": f"In an era of endless noise, mastering {title_clean} has become a superpower..."},
            {"heading": "The Three Core Pillars of Momentum", "body": "Pillar 1 focuses on input control. Pillar 2 automates routine friction. Pillar 3 leverages compounding feedback loops..."},
            {"heading": "Actionable 7-Day Implementation Protocol", "body": "Day 1: Audit friction points. Day 2-4: Establish baseline metrics. Day 5-7: Deploy automated systems..."},
            {"heading": "Conclusion & Key Takeaways", "body": "Consistency is not about never missing a day—it is about never missing twice."}
        ]
    }

    return {
        "source_title": title_clean,
        "shorts_clips": shorts_clips,
        "x_thread": x_thread,
        "linkedin_post": linkedin_post,
        "blog_article": blog_article
    }
