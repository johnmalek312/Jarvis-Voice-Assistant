# region imports
# logging
from logger import app_logger as logging
import logger
logging.info("Importing libraries...")
# Disable TensorFlow optimization for compatibility
import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Standard library imports
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# Audio processing imports
import sounddevice as sd
import soundfile as sf
import keyboard
from RealtimeTTS import TextToAudioStream
from RealtimeSTT import AudioToTextRecorder

# AI/ML imports
from helpers.utils import *
logger.log_with_stack("about to run 1")
from llm_response_generator import LLMResponseGenerator
from prompts import *
from config import *



# endregion imports

class AudioManager:
    @staticmethod
    def play_sound(file_path):
        """Plays audio from the given file path."""
        audio_data, samplerate = sf.read(file_path)
        sd.play(audio_data, samplerate)


class VoiceAssistant:
    def __init__(self):
        self.is_va_paused = False
        self.interrupt_audio_player = False
        self.is_active = True
        self.async_loop = None
        self.is_listening = False
        self.listen_lock = threading.Lock()
        self.assistant_lock = threading.Lock()
        self.thread_pool = ThreadPoolExecutor(max_workers=3)

        # Initialize components
        self.initialize_components()
        logging.info("Setting up hotkeys...")
        self.setup_hotkeys()

    def initialize_components(self):
        # Initialize text-to-speech engine based on selected Engine type
        logging.info(f"Initializing TTS Engine: {Engine}...")
        if Engine == "ElevenLabs":
            # Use ElevenLabs TTS engine
            from RealtimeTTS import ElevenlabsEngine
            self.audio_engine = ElevenlabsEngine(
                APIConfig.ELEVENLABS,
                voice=ElevenLabConfig.NAME,
                model=ElevenLabConfig.MODEL,
                id=ElevenLabConfig.ID
            )
        elif Engine == "Piper":
            # Use Piper local TTS engine
            from RealtimeTTS import PiperEngine, PiperVoice
            self.audio_engine = PiperEngine(
                piper_path=PiperEngineConfig.PIPER_PATH,
                voice=PiperVoice(
                    model_file=PiperEngineConfig.VOICE_MODEL,
                    config_file=PiperEngineConfig.VOICE_CONFIG
                )
            )
        elif Engine == "OpenAI":
            # Use OpenAI TTS engine
            from RealtimeTTS import OpenAIEngine
            self.audio_engine = OpenAIEngine(model=OpenAIConfig.model, voice=OpenAIConfig.voice)
        elif Engine == "GTTS":
            # Use GTTS engine
            from RealtimeTTS import GTTSEngine, GTTSVoice
            self.audio_engine = GTTSEngine(
                GTTSVoice(language=GTTSConfig.language, tld=GTTSConfig.tld, speed=GTTSConfig.speed))
        elif Engine == "Azure":
            # TODO: Implement Azure TTS engine configuration
            pass

        # Initialize audio player
        self.audio_player = TextToAudioStream(
            engine=self.audio_engine,
            on_audio_stream_stop=self.on_play_stop
        )
        logging.info("Initializing LLM Response Generator...")
        # Initialize LLM
        self.llm = LLMResponseGenerator(
            api_key=APIConfig.OPENAI,
            model_name=ModelConfig.LLM_MODEL,
            sys_prompt=sys_prompt_v2,
            n_message_history=ModelConfig.MAX_MESSAGE_HISTORY,
            trace=trace
        )
        logging.info("Initializing STT Engine...")
        # Initialize STT
        self.recorder = AudioToTextRecorder(
            model=ModelConfig.WHISPER_MODEL,
            language=ModelConfig.WHISPER_LANGUAGE,
            spinner=True,
            min_length_of_recording=1.1,
            on_vad_detect_start=partial(AudioManager.play_sound, AUDIO_FILES.ACTIVATE),
            on_recording_stop=partial(AudioManager.play_sound, AUDIO_FILES.DEACTIVATE),
        )

    def setup_hotkeys(self):
        # TODO: Fix pause when the assistant is going through the llama index workflow
        """Sets up keyboard hotkeys for controlling the assistant.

        This method configures the following keyboard shortcuts from config.HOTKEYS:
            - TOGGLE: Toggles the assistant on/off
            - QUIT: Stops the assistant completely
            - INTERRUPT: Interrupts any currently playing audio
        """
        keyboard.add_hotkey(HOTKEYS.TOGGLE, self.start_stop_assistant)
        keyboard.add_hotkey(HOTKEYS.QUIT, lambda: setattr(self, 'keep_running', False))
        keyboard.add_hotkey(HOTKEYS.INTERRUPT, lambda: setattr(self, 'interrupt_audio_player', True))

    def start_stop_assistant(self):
        """Toggles the assistant between active and paused states.
        Thread-safe using assistant_lock to prevent concurrent state changes.
        """
        with self.assistant_lock:
            if self.recorder.state != "inactive" or self.audio_player.is_playing():
                self.pause_assistant()
            else:
                self.start_assistant()

    def pause_assistant(self):
        """Pauses the assistant by stopping the audio player and recorder."""
        self.is_va_paused = True
        self.audio_player.stop()
        if self.recorder.state != "inactive":
            self.recorder.abort()
            if self.recorder.is_recording:
                self.recorder.stop()
        self.is_listening = False
        print("Paused AI assistant.")

    def start_assistant(self):
        """Starts the assistant by resuming the audio player and recorder."""
        print("Started AI assistant.")
        self.is_va_paused = False
        self.listen_to_user()

    def check_interruption(self):
        """Checks if the audio player should be interrupted and stops it if necessary."""
        if self.interrupt_audio_player and self.audio_player.is_playing():
            print("Interrupting assistant...")
            self.audio_player.stop()
            self.interrupt_audio_player = False

    def on_play_stop(self):
        """Callback function to be executed when the audio player finishes playing audio."""
        if self.is_active:
            self.listen_to_user()

    def listen_to_user(self):
        """Starts the audio recorder to listen for user input."""
        with self.listen_lock:
            if self.is_listening:
                return
            self.is_listening = True

        def wrapped():
            while not self.is_va_paused:
                text = self.recorder.text().strip()
                if text and not self.is_va_paused:
                    self.async_loop.create_task(self.process_response(text))
                    break
                # if is_listening is set to false by an outside function, the function shouldn't process any requests
                elif self.is_va_paused:
                    break
            with self.listen_lock:
                self.is_listening = False

        return self.thread_pool.submit(wrapped)

    async def process_response(self, text):
        """Processes the user's text input and generates a response using the LLM. Then it plays the response audio by sending it to the configured TTS Engine."""
        print(f'User: {text}')
        response: str = await self.llm.get_response(text)
        print(f"Assistant: {response}")
        if __name__ == '__main__':
            await self.play_audio(clean_text(response))

    async def play_audio(self, text):
        """Plays the given text as audio using the configured TTS Engine."""
        self.audio_player.feed(text)
        self.audio_player.play(muted=False, output_wavfile="assets/output1.wav")

    async def update_loop(self):
        """Continuously checks for interruptions and sleeps for a short duration."""
        while self.is_active:
            self.check_interruption()
            await asyncio.sleep(0.3)

    async def run(self):
        """Main entry point for the voice assistant."""
        print("Listening...")
        try:
            self.async_loop = asyncio.get_running_loop()
            self.listen_to_user()
            await self.update_loop()
        except asyncio.CancelledError:
            print("Cancelled")
        except Exception as e:
            print(e)
        finally:
            self.recorder.abort()
            if self.recorder.is_recording:
                self.recorder.stop()
            self.thread_pool.shutdown(wait=True)
            self.is_active = True


if __name__ == '__main__':
    print("Started")
    assistant = VoiceAssistant()
    asyncio.run(assistant.run())
