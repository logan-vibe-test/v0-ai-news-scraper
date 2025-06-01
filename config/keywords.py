"""
Keyword configuration for AI Voice News Scraper
"""

# Primary keywords - articles MUST contain at least one of these
PRIMARY_VOICE_AI_KEYWORDS = [
    'voice ai', 'text-to-speech', 'tts', 'speech synthesis',
    'voice synthesis', 'voice model', 'voice generation',
    'voice assistant', 'voice clone', 'voice cloning',
    'synthetic voice', 'ai voice', 'neural voice'
]

# Secondary keywords - help with context and relevance
SECONDARY_KEYWORDS = [
    'audio generation', 'speech generation', 'voice conversion',
    'voice transformer', 'speech-to-speech', 'voice streaming',
    'voice api', 'conversational ai', 'voice chat', 'voice bot'
]

# Company-specific keywords
COMPANY_KEYWORDS = [
    'elevenlabs', 'openai voice', 'google voice', 'amazon alexa',
    'microsoft cortana', 'apple siri', 'anthropic voice',
    'meta voice', 'nvidia voice', 'adobe voice'
]

# Technical terms
TECHNICAL_KEYWORDS = [
    'vocoder', 'neural vocoder', 'wavenet', 'tacotron',
    'fastspeech', 'melgan', 'hifigan', 'voice encoder',
    'speaker embedding', 'voice embedding', 'prosody',
    'phoneme', 'mel-spectrogram'
]

# Application keywords
APPLICATION_KEYWORDS = [
    'voice over', 'audiobook', 'podcast generation',
    'voice dubbing', 'voice translation', 'multilingual voice',
    'voice accessibility', 'voice interface', 'voice commerce',
    'voice search', 'voice control'
]

# Combine all keywords
ALL_VOICE_AI_KEYWORDS = (
    PRIMARY_VOICE_AI_KEYWORDS + 
    SECONDARY_KEYWORDS + 
    COMPANY_KEYWORDS + 
    TECHNICAL_KEYWORDS + 
    APPLICATION_KEYWORDS
)

# Context keywords that help determine relevance
CONTEXT_KEYWORDS = [
    'ai', 'artificial intelligence', 'model', 'neural',
    'deep learning', 'machine learning', 'generative',
    'algorithm', 'training', 'dataset', 'api', 'sdk'
]
