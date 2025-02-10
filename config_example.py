
class APIConfig:
    """API keys for external services"""
    PHOENIX: str = "your api key here"  # optional for debugging
    ELEVENLABS: str = "your api key here"  # optional if not using ElevenLabs
    OPENAI: str = "your api key here"  # optional if not using openai
    GEMINI: str = "your api key here"  # optional if not using Gemini

# Phoenix tracing flag
trace: bool = False

# Text-to-Speech Engine Selection
Engine: str = "Piper"  # Available engines: "ElevenLabs", "OpenAI", "Azure", "GTTS", "Piper" (highly recommend Piper)

# Embedding model
EmbeddingModel: str = "huggingface" # Available models: "openai", "huggingface"

LMM_provider = "gemini" # Available models: "openai", "gemini"

MAX_MESSAGE_HISTORY: int = 3
timeout: int = 30


class ElevenLabConfig:
    ID: str = "XB0fDUnXU5powFXDhCwa"
    NAME: str = "Charlotte"
    MODEL: str = "eleven_flash_v2_5"

class OpenaiTTSConfig:
    model: str = "tts-1"
    voice: str = "nova"

class AzureEngineConfig:
    pass

class PiperEngineConfig:
    PIPER_PATH: str = "models/PiperVoice/piper/piper.exe"
    VOICE_MODEL: str = "models/PiperVoice/amy-low-voice.onnx"
    VOICE_CONFIG: str = "models/PiperVoice/amy-low-config.json"
    speed: int = 10

class GTTSConfig:
    language: str = 'en'
    tld: str = 'com'
    speed: float = 1.0

class STTConfig:
    WHISPER_MODEL: str = "medium"
    WHISPER_LANGUAGE: str = "en"

class OpenAILLMConfig:
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.1

class GeminiLLMConfig:
    LLM_MODEL: str = "models/gemini-2.0-flash"
    LLM_TEMPERATURE: float = 0.1


class OpenaiEmbeddingConfig:
    """Embedding model configuration"""
    MODEL: str = "text-embedding-ada-002"
    EMBED_BATCH_SIZE: int = 100

class HuggingFaceEmbeddingConfig:
    """Embedding model configuration"""
    MODEL: str = "Snowflake/snowflake-arctic-embed-l-v2.0" # change to any model of your choice, must be `sentence-transformers` compatible


class HOTKEYS:
    TOGGLE: str = 'pause'
    QUIT: str = 'home'
    INTERRUPT: str = '+'

class AUDIO_FILES:
    """Sound effect file paths"""
    ACTIVATE: str = "assets/active.wav"      # Sound played on activation
    DEACTIVATE: str = "assets/deactive.mp3"  # Sound played on deactivation

class FEATURES:
    """Feature flags"""
    GMAIL: bool = True
    BROWSER: bool = True
    WEATHER: bool = True
    GOOGLE: bool = True
    WIKIPEDIA: bool = True
    INSTAGRAM: bool = True
    URL_SHORTENER: bool = True
    SYSTEM_STATS: bool = True
    WINDOW_TOOLS: bool = True
    SHORT_COMMS: bool = True
    PYTHON: bool = True
    LLM_WORKFLOW: bool = True
    PASTEBIN: bool = True

CACHE_DIRECTORY = "./cache"  # Directory for index persistence

RETRIEVE_TOP_K = 3 # -1 for all # Number of top documents to retrieve when querying for tools

