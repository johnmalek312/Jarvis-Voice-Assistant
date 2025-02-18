# region imports
if __name__ == "__main__": # important to stop RealtimeSTT from reloading modules in child process.
    # logging
    from logger import app_logger as logging
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
    from llm_response_generator import LLMResponseGenerator
    from prompts import *
    from config import *
    from scripts import data_manager

    # Helper imports
    from helpers import llamaindex_helper
    from helpers.utils import *



# endregion imports

class AudioManager:
    @staticmethod
    def play_sound(file_path):
        """Plays audio from the given file path."""
        audio_data, samplerate = sf.read(file_path)
        sd.play(audio_data, samplerate)


class VoiceAssistant:
    def __init__(self):
        self.paused = False
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

        self.paused = False # used to toggle pause

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
            self.audio_engine = OpenAIEngine(model=OpenaiTTSConfig.model, voice=OpenaiTTSConfig.voice)
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
            sys_prompt=gemini_prompt,
            n_message_history=timeout,
            trace=trace
        )
        data_manager.DataManager.va = self
        logging.info("Initializing STT Engine...")
        # Initialize STT
        self.recorder = AudioToTextRecorder(
            model=STTConfig.WHISPER_MODEL,
            language=STTConfig.WHISPER_LANGUAGE,
            spinner=True,
            min_length_of_recording=1.1,
            on_vad_detect_start=partial(AudioManager.play_sound, AUDIO_FILES.ACTIVATE),
            on_recording_stop=partial(AudioManager.play_sound, AUDIO_FILES.DEACTIVATE),
        )

    def setup_hotkeys(self):
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
            if not self.paused:
                self.paused = True
                self.pause_assistant()
            else:
                self.paused = False
                self.start_assistant()

    def pause_assistant(self):
        """Pauses the assistant by stopping the audio player and recorder."""
        if self.llm.workflow_handler:
            try:
                self.async_loop.create_task(self.llm.workflow_handler.cancel_run())
            except Exception:
                pass
        self.audio_player.stop()
        state = self.recorder.state
        self.recorder.abort()
        self.is_listening = False
        if state != "recording":
            AudioManager.play_sound(AUDIO_FILES.DEACTIVATE)
        logging.info("Paused AI assistant.")

    def start_assistant(self):
        """Starts the assistant by resuming the audio player and recorder."""
        logging.info("Started AI assistant.")
        self.paused = False
        self.listen_to_user()

    def check_interruption(self):
        """Checks if the audio player should be interrupted and stops it if necessary."""
        if self.interrupt_audio_player and self.audio_player.is_playing():
            logging.info("Interrupting assistant...")
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
            while not self.paused:
                text = self.recorder.text().strip()
                if text and not self.paused:
                    self.async_loop.create_task(self.process_response(text))
                    break
                # if is_listening is set to false by an outside function, the function shouldn't process any requests
                elif self.paused:
                    break
            with self.listen_lock:
                self.is_listening = False

        return self.thread_pool.submit(wrapped)

    async def process_response(self, text):
        """Processes the user's text input and generates a response using the LLM. Then it plays the response audio by sending it to the configured TTS Engine."""
        logging.info(f'User: {text}')
        response: str | None = await self.llm.get_response(text)
        if response is None:
            return
        logging.info(f"Assistant: {response}")
        self.play_audio(clean_text(response))

    def play_audio(self, text):
        """Plays the given text as audio using the configured TTS Engine."""
        self.audio_player.feed(text)
        self.audio_player.play_async(muted=False, output_wavfile="assets/output1.wav")

    async def update_loop(self):
        """Continuously checks for interruptions and sleeps for a short duration."""
        while self.is_active:
            self.check_interruption()
            await asyncio.sleep(0.3)

    async def run(self):
        """Main entry point for the voice assistant."""
        logging.info("Listening...")
        try:
            self.async_loop = asyncio.get_running_loop()
            self.listen_to_user()
            await self.update_loop()
        except asyncio.CancelledError:
            logging.info("Cancelled")
        except Exception as e:
            logging.info(e)
        finally:
            self.recorder.abort()
            if self.recorder.is_recording:
                self.recorder.stop()
            self.thread_pool.shutdown(wait=True)
            self.is_active = True


if __name__ == '__main__':
    assistant = VoiceAssistant()
    asyncio.run(assistant.run())
