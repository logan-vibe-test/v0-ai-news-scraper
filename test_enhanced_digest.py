"""
Test the enhanced email digest with executive summary
"""
import asyncio
import logging
from datetime import datetime
from notifiers.email_notifier import send_email_digest, generate_executive_summary

logging.basicConfig(level=logging.INFO)

async def test_enhanced_digest():
    print("🧪 Testing enhanced email digest...")
    
    # Create sample data
    sample_digest = {
        'date': datetime.now().strftime("%Y-%m-%d"),
        'news_items': [
            {
                'title': 'ElevenLabs Launches New Voice Cloning API',
                'url': 'https://example.com/elevenlabs-api',
                'source': 'TechCrunch',
                'published_date': '2024-01-15T10:00:00',
                'summary': 'ElevenLabs has announced a new voice cloning API that allows developers to create custom voices with just 30 seconds of audio. The technology uses advanced neural networks to capture voice characteristics and speaking patterns.'
            },
            {
                'title': 'OpenAI Improves Whisper Speech Recognition',
                'url': 'https://example.com/openai-whisper',
                'source': 'OpenAI Blog',
                'published_date': '2024-01-15T09:00:00',
                'summary': 'OpenAI has released Whisper v3, featuring improved accuracy for multiple languages and better handling of background noise. The update includes support for real-time transcription and enhanced punctuation.'
            },
            {
                'title': 'Voice AI Market Reaches $15 Billion',
                'url': 'https://example.com/voice-ai-market',
                'source': 'AI News',
                'published_date': '2024-01-15T08:00:00',
                'summary': 'The global voice AI market has reached $15 billion in 2024, driven by increased adoption in customer service, content creation, and accessibility applications. Growth is expected to continue at 25% annually.'
            }
        ],
        'reactions': [
            {
                'platform': 'reddit',
                'subreddit': 'MachineLearning',
                'title': 'ElevenLabs API is game-changing for content creators',
                'url': 'https://reddit.com/r/MachineLearning/comments/test1',
                'score': 156,
                'num_comments': 23
            },
            {
                'platform': 'reddit',
                'subreddit': 'OpenAI',
                'title': 'Whisper v3 accuracy improvements are impressive',
                'url': 'https://reddit.com/r/OpenAI/comments/test2',
                'score': 89,
                'num_comments': 12
            }
        ]
    }
    
    # Test executive summary generation
    print("📊 Generating executive summary...")
    summary = await generate_executive_summary(
        sample_digest['news_items'], 
        sample_digest['reactions']
    )
    print(f"Summary: {summary[:200]}...")
    
    # Test sending digest
    print("📧 Testing email digest...")
    result = await send_email_digest(sample_digest)
    
    if result:
        print("✅ Enhanced email digest sent successfully!")
        print("Check your email for the new format with:")
        print("  • Executive summary at the top")
        print("  • Statistics dashboard")
        print("  • Top 5 most relevant articles")
        print("  • Enhanced visual design")
    else:
        print("❌ Email sending failed. Check your email configuration.")

if __name__ == "__main__":
    asyncio.run(test_enhanced_digest())
