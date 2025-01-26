# API Keys for various services
API_KEYS = {
    'PHOENIX': "Your_api_key_here", # optional for debugging
    'ELEVENLABS': "Your_api_key_here", # optional if you are not using ElevenLabs in the `Engine`
    'OPENAI': "Your_api_key_here" # unfortunately it is currently required.
}

# Phoenix tracing flag
trace = False

# Text-to-Speech Engine Selection
Engine = "Piper"  # Available engines: "ElevenLabs", "OpenAI", "Azure", "GTTS", "Piper" (highly recommend Piper)

# ElevenLabs Voice Configuration
ElevenLabConfig = {
    'ID': "XB0fDUnXU5powFXDhCwa",
    'NAME': "Charlotte",
    'MODEL': "eleven_flash_v2_5"
}

# OpenAI TTS Configuration
OpenAIConfig = {
    "model": "tts-1",
    "voice": "nova"
}

# Azure TTS Configuration (Empty for now)
AzureEngineConfig = {

}

# Piper TTS Configuration with file paths. This is very fast model
PiperEngineConfig = {
    'PIPER_PATH': "models/PiperVoice/piper/piper.exe",
    'VOICE_MODEL': "models/PiperVoice/amy-low-voice.onnx",
    'VOICE_CONFIG': "models/PiperVoice/amy-low-config.json",
    'speed': 10
}
# Google TTS Configuration
GTTSConfig = {
    'language': 'en',
    'tld': 'com',
    'speed': 1
}

# AI Model Configuration
MODEL_CONFIG = {
    'WHISPER_MODEL': "medium",      # Speech recognition model size
    'WHISPER_LANGUAGE': "en",       # Target language
    'LLM_MODEL': "gpt-4o-mini",    # Language model
    'MAX_MESSAGE_HISTORY': 3,        # Number of messages to retain in history, the lower the cheaper the model would cost.
    'timeout': 20                  # Timeout for LLM response generation
}

# Hotkey Configuration
HOTKEYS = {
    'TOGGLE': 'pause',    # Toggle assistant on/off
    'QUIT': 'home',       # Stop assistant completely
    'INTERRUPT': '+'      # Interrupt current audio
}

# Sound Effect File Paths
AUDIO_FILES = {
    'ACTIVATE': "assets/active.wav",    # Sound played on activation
    'DEACTIVATE': "assets/deactive.mp3" # Sound played on deactivation
}
