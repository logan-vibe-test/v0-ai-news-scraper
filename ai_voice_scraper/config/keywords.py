"""
Enhanced keyword configuration for AI Voice News Scraper
"""

# Core voice AI keywords - articles MUST contain at least one
PRIMARY_VOICE_AI_KEYWORDS = [
    # Direct voice AI terms
    'voice ai', 'ai voice', 'voice artificial intelligence',
    'text-to-speech', 'tts', 'speech synthesis', 'voice synthesis',
    'voice generation', 'voice model', 'neural voice',
    'voice cloning', 'voice clone', 'synthetic voice',
    
    # Voice assistant terms
    'voice assistant', 'voice bot', 'conversational ai',
    'voice interface', 'voice api', 'voice sdk',
    
    # Audio generation
    'audio generation', 'speech generation', 'voice streaming',
    'real-time voice', 'voice conversion', 'voice transformer'
]

# Company-specific voice AI keywords
COMPANY_VOICE_KEYWORDS = [
    'elevenlabs', 'eleven labs', 'openai voice', 'openai whisper',
    'google voice', 'google speech', 'amazon polly', 'azure speech',
    'microsoft speech', 'anthropic voice', 'meta voice',
    'nvidia voice', 'adobe voice', 'murf', 'speechify',
    'resemble ai', 'descript', 'wellsaid', 'lovo'
]

# Technical voice AI terms
TECHNICAL_VOICE_KEYWORDS = [
    'vocoder', 'neural vocoder', 'wavenet', 'tacotron',
    'fastspeech', 'melgan', 'hifigan', 'voice encoder',
    'speaker embedding', 'voice embedding', 'prosody',
    'phoneme', 'mel-spectrogram', 'voice dataset',
    'voice training', 'voice fine-tuning', 'voice model training'
]

# Voice AI applications
APPLICATION_VOICE_KEYWORDS = [
    'voice over', 'voiceover', 'audiobook', 'podcast generation',
    'voice dubbing', 'voice translation', 'multilingual voice',
    'voice accessibility', 'voice commerce', 'voice search',
    'voice control', 'voice narration', 'voice acting',
    'voice personalization', 'custom voice', 'brand voice'
]

# Combine all voice-specific keywords
ALL_VOICE_AI_KEYWORDS = (
    PRIMARY_VOICE_AI_KEYWORDS + 
    COMPANY_VOICE_KEYWORDS + 
    TECHNICAL_VOICE_KEYWORDS + 
    APPLICATION_VOICE_KEYWORDS
)

# Context keywords that help determine relevance
CONTEXT_KEYWORDS = [
    'ai', 'artificial intelligence', 'machine learning', 'deep learning',
    'neural network', 'model', 'algorithm', 'training', 'dataset',
    'api', 'sdk', 'platform', 'technology', 'innovation',
    'startup', 'funding', 'release', 'launch', 'announcement'
]

# Negative keywords to filter out irrelevant content
NEGATIVE_KEYWORDS = [
    'voice actor', 'voice actress', 'singing voice', 'music voice',
    'voice coach', 'voice lesson', 'voice therapy', 'voice disorder',
    'voice of america', 'voice of america', 'voice vote', 'voice mail', 'voicemail'
]

### **🔧 Key Fixes Applied:**

#### **1. Enhanced News Scraper**
- ✅ Added SSL verification bypass for problematic sources
- ✅ Improved error handling with detailed logging
- ✅ Added fallback RSS feeds for more reliable content
- ✅ Increased timeout and retry logic

#### **2. Less Restrictive Content Processing**
- ✅ Lowered relevance threshold from 0.7 to 0.4
- ✅ Added more flexible keyword matching
- ✅ Improved content extraction from various formats
- ✅ Better handling of partial matches

#### **3. Expanded Keywords**
- ✅ Added more voice AI related terms
- ✅ Included company names and product names
- ✅ Added technical terms and acronyms
- ✅ More inclusive matching patterns

#### **4. Debug Tools**
- ✅ Added comprehensive debug script
- ✅ Step-by-step pipeline testing
- ✅ Detailed logging at each stage

### **🚀 Quick Debug Steps:**

\`\`\`bash
# Run the debug script to see what's happening
python debug.py

# Check logs for specific errors
tail -f logs/scraper.log

# Test individual components
python -c "from ai_voice_scraper.scrapers.news_scraper import NewsScraper; scraper = NewsScraper(); print(len(scraper.scrape_news()))"
