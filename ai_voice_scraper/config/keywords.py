"""
Keywords configuration for AI Voice News Scraper
"""

# Primary keywords that are directly related to voice AI
PRIMARY_VOICE_AI_KEYWORDS = [
    "voice ai", "voice assistant", "voice synthesis", "voice clone", "voice cloning",
    "speech synthesis", "speech recognition", "text to speech", "tts", "speech to text",
    "stt", "voice generation", "voice model", "voice transformer", "voice conversion",
    "voice deepfake", "synthetic voice", "ai voice", "neural voice", "voice neural network",
    "voice ml", "voice machine learning", "voice deep learning", "voice transformer",
    "elevenlabs", "play.ht", "murf.ai", "resemble.ai", "wellsaid", "wellsaidlabs",
    "voice recognition", "voice interface", "voice user interface", "vui",
    "voice computing", "voice tech", "voice technology", "voice-first", "voice first",
    "voice application", "voice app", "voice-enabled", "voice enabled",
    "voice-activated", "voice activated", "voice-controlled", "voice controlled",
    "voice-driven", "voice driven", "voice-based", "voice based",
    "voice-powered", "voice powered", "voice-operated", "voice operated",
    "voice-directed", "voice directed", "voice-guided", "voice guided",
    "voice-centric", "voice centric", "voice-focused", "voice focused",
    "voice-oriented", "voice oriented", "voice-optimized", "voice optimized",
    "voice-specific", "voice specific", "voice-targeted", "voice targeted",
    "voice-only", "voice only", "voice-exclusive", "voice exclusive",
    "voice-primary", "voice primary", "voice-secondary", "voice secondary",
    "voice-tertiary", "voice tertiary", "voice-quaternary", "voice quaternary",
    "voice-quinary", "voice quinary", "voice-senary", "voice senary",
    "voice-septenary", "voice septenary", "voice-octonary", "voice octonary",
    "voice-nonary", "voice nonary", "voice-denary", "voice denary",
    "voice-undenary", "voice undenary", "voice-duodenary", "voice duodenary",
    "voice-tredenary", "voice tredenary", "voice-quattuordenary", "voice quattuordenary",
    "voice-quindenary", "voice quindenary", "voice-sexdenary", "voice sexdenary",
    "voice-septendenary", "voice septendenary", "voice-octodenary", "voice octodenary",
    "voice-novemdenary", "voice novemdenary", "voice-vigintenary", "voice vigintenary",
]

# Additional keywords that are related to voice AI
SECONDARY_VOICE_AI_KEYWORDS = [
    "audio generation", "audio synthesis", "audio clone", "audio cloning",
    "audio deepfake", "synthetic audio", "ai audio", "neural audio",
    "audio neural network", "audio ml", "audio machine learning",
    "audio deep learning", "audio transformer", "audio model",
    "audio generation", "audio synthesis", "audio clone", "audio cloning",
    "audio deepfake", "synthetic audio", "ai audio", "neural audio",
    "audio neural network", "audio ml", "audio machine learning",
    "audio deep learning", "audio transformer", "audio model",
]

# Context keywords that might indicate voice AI when combined with primary keywords
CONTEXT_KEYWORDS = [
    "generative ai", "gen ai", "artificial intelligence", "machine learning",
    "deep learning", "neural network", "transformer", "model", "algorithm",
    "training", "fine-tuning", "fine tuning", "dataset", "data set",
    "corpus", "corpora", "sample", "samples", "sampling", "generation",
    "synthesis", "synthetic", "clone", "cloning", "deepfake", "deep fake",
    "fake", "real-time", "real time", "realtime", "streaming", "stream",
    "api", "apis", "service", "services", "platform", "platforms",
    "tool", "tools", "toolkit", "toolkits", "library", "libraries",
    "framework", "frameworks", "sdk", "sdks", "development kit",
    "development kits", "developer kit", "developer kits",
    "developer tool", "developer tools", "development tool",
    "development tools", "developer platform", "developer platforms",
    "development platform", "development platforms",
]

# Combine all keywords
ALL_VOICE_AI_KEYWORDS = PRIMARY_VOICE_AI_KEYWORDS + SECONDARY_VOICE_AI_KEYWORDS

# Company names related to voice AI
VOICE_AI_COMPANIES = [
    "elevenlabs", "eleven labs", "play.ht", "playht", "murf.ai", "murf ai",
    "resemble.ai", "resemble ai", "wellsaid", "wellsaidlabs", "wellsaid labs",
    "descript", "speechify", "coqui", "synthesia", "lovo.ai", "lovo ai",
    "respeecher", "replica", "sonantic", "deepzen", "deepzen.io", "deepzen io",
    "aflorithmic", "aflorithmic.ai", "aflorithmic ai", "speechelo", "synthesys",
    "synthesys.io", "synthesys io", "listnr", "listnr.tech", "listnr tech",
    "voicemod", "voicemod.net", "voicemod net", "voicery", "voicery.com",
    "voicery com", "lyrebird", "lyrebird.ai", "lyrebird ai", "overdub",
    "overdub.ai", "overdub ai", "vocalid", "vocalid.ai", "vocalid ai",
    "voctro labs", "voctrolabs", "voctro", "voxygen", "cereproc", "acapela",
    "acapela group", "acapelagroup", "nuance", "nuance communications",
    "nuancecommunications", "amazon polly", "amazonpolly", "google wavenet",
    "googlewavenet", "microsoft azure", "microsoftazure", "ibm watson",
    "ibmwatson", "baidu deep voice", "baidudeepvoice", "mozilla tts",
    "mozillatts", "mozilla common voice", "mozillacommonvoice",
]

# Product names related to voice AI
VOICE_AI_PRODUCTS = [
    "siri", "alexa", "google assistant", "googleassistant", "cortana",
    "bixby", "aura", "voice match", "voicematch", "voice access",
    "voiceaccess", "voice search", "voicesearch", "voice typing",
    "voicetyping", "voice commands", "voicecommands", "voice control",
    "voicecontrol", "voice input", "voiceinput", "voice output",
    "voiceoutput", "voice feedback", "voicefeedback", "voice response",
    "voiceresponse", "voice prompt", "voiceprompt", "voice query",
    "voicequery", "voice answer", "voiceanswer", "voice reply",
    "voicereply", "voice message", "voicemessage", "voice mail",
    "voicemail", "voice note", "voicenote", "voice memo", "voicememo",
    "voice recording", "voicerecording", "voice dictation", "voicedictation",
    "voice transcription", "voicetranscription", "voice translation",
    "voicetranslation", "voice chat", "voicechat", "voice call",
    "voicecall", "voice conference", "voiceconference", "voice meeting",
    "voicemeeting", "voice assistant", "voiceassistant", "voice bot",
    "voicebot", "voice agent", "voiceagent", "voice persona", "voicepersona",
    "voice character", "voicecharacter", "voice avatar", "voiceavatar",
    "voice clone", "voiceclone", "voice twin", "voicetwin", "voice double",
    "voicedouble", "voice replica", "voicereplica", "voice copy",
    "voicecopy", "voice duplicate", "voiceduplicate", "voice synthesis",
    "voicesynthesis", "voice generator", "voicegenerator", "voice creator",
    "voicecreator", "voice maker", "voicemaker", "voice builder",
    "voicebuilder", "voice designer", "voicedesigner", "voice developer",
    "voicedeveloper", "voice engineer", "voiceengineer", "voice architect",
    "voicearchitect", "voice artist", "voiceartist", "voice actor",
    "voiceactor", "voice talent", "voicetalent", "voice over", "voiceover",
    "voice acting", "voiceacting", "voice performance", "voiceperformance",
    "voice direction", "voicedirection", "voice production", "voiceproduction",
    "voice post-production", "voice postproduction", "voicepostproduction",
    "voice editing", "voiceediting", "voice mixing", "voicemixing",
    "voice mastering", "voicemastering", "voice processing", "voiceprocessing",
    "voice effects", "voiceeffects", "voice filter", "voicefilter",
    "voice modulation", "voicemodulation", "voice modification",
    "voicemodification", "voice transformation", "voicetransformation",
    "voice conversion", "voiceconversion", "voice changing", "voicechanging",
    "voice changer", "voicechanger", "voice morphing", "voicemorphing",
    "voice warping", "voicewarping", "voice pitching", "voicepitching",
    "voice shifting", "voiceshifting", "voice tuning", "voicetuning",
    "voice correction", "voicecorrection", "voice enhancement",
    "voiceenhancement", "voice improvement", "voiceimprovement",
    "voice optimization", "voiceoptimization", "voice restoration",
    "voicerestoration", "voice repair", "voicerepair", "voice fixing",
    "voicefixing", "voice cleaning", "voicecleaning", "voice denoising",
    "voicedenoising", "voice noise reduction", "voicenoisereduction",
    "voice noise cancellation", "voicenoisecancellation",
    "voice noise suppression", "voicenoisesuppression",
    "voice echo cancellation", "voiceechocancellation",
    "voice echo suppression", "voiceechosuppression",
    "voice feedback cancellation", "voicefeedbackcancellation",
    "voice feedback suppression", "voicefeedbacksuppression",
]

# Combine all voice AI related terms
ALL_VOICE_AI_TERMS = (
    PRIMARY_VOICE_AI_KEYWORDS +
    SECONDARY_VOICE_AI_KEYWORDS +
    VOICE_AI_COMPANIES +
    VOICE_AI_PRODUCTS
)
