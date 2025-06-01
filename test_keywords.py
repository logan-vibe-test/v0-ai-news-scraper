"""
Test script to see what keywords are being used and test relevance filtering
"""
import re
from config.keywords import ALL_VOICE_AI_KEYWORDS, PRIMARY_VOICE_AI_KEYWORDS, CONTEXT_KEYWORDS

def test_article_relevance(title, content=""):
    """Test if an article would be considered relevant"""
    text = f"{title} {content}".lower()
    
    # Check for primary keyword matches
    primary_matches = [kw for kw in PRIMARY_VOICE_AI_KEYWORDS if kw in text]
    all_matches = [kw for kw in ALL_VOICE_AI_KEYWORDS if kw in text]
    context_matches = [kw for kw in CONTEXT_KEYWORDS if kw in text]
    
    print(f"Title: {title}")
    print(f"Primary matches: {primary_matches}")
    print(f"All matches: {all_matches}")
    print(f"Context matches: {context_matches}")
    
    # Apply the same logic as the scraper
    if len(primary_matches) == 0:
        print("❌ REJECTED: No primary voice AI keywords")
        return False
    
    if len(all_matches) >= 2 or (len(primary_matches) >= 1 and len(context_matches) >= 1):
        print("✅ ACCEPTED: Strong relevance")
        return True
    
    print("⚠️  MAYBE: Weak relevance - would need sentence-level analysis")
    return False

if __name__ == "__main__":
    print("=== Current Keywords ===")
    print(f"Primary keywords ({len(PRIMARY_VOICE_AI_KEYWORDS)}): {PRIMARY_VOICE_AI_KEYWORDS}")
    print(f"Total keywords ({len(ALL_VOICE_AI_KEYWORDS)}): {len(ALL_VOICE_AI_KEYWORDS)} keywords")
    
    print("\n=== Testing Sample Articles ===")
    
    # Test some sample article titles
    test_articles = [
        "OpenAI Launches New Voice Model for Realistic Speech Generation",
        "ElevenLabs Raises $80M for AI Voice Cloning Technology", 
        "Google Announces Improved Text-to-Speech API",
        "Meta's New AI Can Generate Realistic Voices in Real-Time",
        "Apple Updates Siri with Better Voice Recognition",
        "Tesla Announces New Autopilot Features",  # Should be rejected
        "Microsoft Azure Gets New Machine Learning Tools",  # Should be rejected
        "Anthropic Releases Claude with Voice Capabilities"
    ]
    
    for title in test_articles:
        print(f"\n{'-'*50}")
        test_article_relevance(title)
