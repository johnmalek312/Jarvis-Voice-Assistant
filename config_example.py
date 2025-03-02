class APIConfig:
    """API keys for external services"""
    PHOENIX: str = "replace with your api key"  # only used for debugging (not required)
    ELEVENLABS: str = "replace with your api key"  # optional if not using ElevenLabs
    OPENAI: str = "replace with your api key"  # optional if not using openai or the researcher
    GEMINI: str = "replace with your api key"  # optional if not using Gemini or the researcher
    TAVILY: str = "replace with your api key" # optional, used for the researcher
# Phoenix tracing flag
trace: bool = False

# Text-to-Speech Engine Selection
Engine: str = "Piper"  # Available engines: "ElevenLabs", "OpenAI", "Azure", "GTTS", "Piper" (highly recommend Piper)

# Embedding model
EmbeddingModel: str = "huggingface" # Available models: "openai", "huggingface"

LLM_provider = "openai" # Available models: "openai", "gemini"

MAX_MESSAGE_HISTORY: int = 3
timeout: int = 120
thinking_mode: bool = True
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
    GPT_RESEARCHER: bool = True

CACHE_DIRECTORY = "./cache"  # Directory for index persistence

Top_K_Retriever = -1 # Number of top documents to retrieve when querying for tools. use -1 to retrieve all tools.




def researcher_config(): # read https://docs.gptr.dev/docs/gpt-researcher/gptr/config for config options and more details
    import os
    os.environ["GOOGLE_API_KEY"] = APIConfig.GEMINI
    os.environ["FAST_LLM"] = "google_genai:gemini-2.0-flash"
    os.environ["SMART_LLM"] = "google_genai:gemini-2.0-flash"
    os.environ["STRATEGIC_LLM"] = "google_genai:gemini-2.0-flash"
    os.environ["EMBEDDING"] = "google_genai:models/text-embedding-004"
    os.environ["TAVILY_API_KEY"] = APIConfig.TAVILY
