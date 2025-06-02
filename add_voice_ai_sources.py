"""
Script to add more voice AI specific news sources
"""
import json
import os

# Define new voice AI specific RSS feeds
NEW_VOICE_AI_SOURCES = [
    {
        "name": "Voicebot.ai",
        "url": "https://voicebot.ai/feed/",
        "category": "voice_ai"
    },
    {
        "name": "Speech Technology Magazine",
        "url": "https://www.speechtechmag.com/rss.aspx",
        "category": "voice_ai"
    },
    {
        "name": "Elevenlabs Blog",
        "url": "https://elevenlabs.io/blog/rss/",
        "category": "voice_ai"
    },
    {
        "name": "Resemble AI Blog",
        "url": "https://www.resemble.ai/blog/rss/",
        "category": "voice_ai"
    },
    {
        "name": "Voice Tech Podcast",
        "url": "https://voicetechpodcast.com/feed/",
        "category": "voice_ai"
    },
    {
        "name": "Project Voice",
        "url": "https://www.projectvoice.ai/blog?format=rss",
        "category": "voice_ai"
    }
]

def add_sources_to_config():
    """Add new sources to the news sources configuration"""
    config_path = "ai_voice_scraper/config/news_sources.json"
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # Load existing config or create new one
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            try:
                sources = json.load(f)
            except json.JSONDecodeError:
                sources = []
    else:
        sources = []
    
    # Add new sources if they don't already exist
    added_count = 0
    for new_source in NEW_VOICE_AI_SOURCES:
        if not any(s.get('url') == new_source['url'] for s in sources):
            sources.append(new_source)
            added_count += 1
    
    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(sources, f, indent=2)
    
    print(f"Added {added_count} new voice AI specific news sources")
    print(f"Total news sources: {len(sources)}")

if __name__ == "__main__":
    add_sources_to_config()
