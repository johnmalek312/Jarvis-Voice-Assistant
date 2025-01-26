# Nova

**Nova** is an AI voice assistant that leverages Retrieval-Augmented Generation (RAG) and LlamaIndex to provide intelligent and context-aware interactions. Designed to assist users through voice commands, Nova integrates various AI models and tools to deliver a seamless experience.

## Features

- **Voice Interaction**: Communicate with Nova using natural language.
- **Retrieval-Augmented Generation (RAG)**: Enhances responses by retrieving relevant information from indexed data.
- **LlamaIndex Integration**: Efficiently handles data indexing and retrieval.
- **Multiple TTS Engines**: Supports ElevenLabs, Piper, OpenAI, Azure, and GTTS for text-to-speech functionality.
- **Configurable AI Models**: Customize AI behavior with different model configurations.
- **Hotkey Controls**: Manage assistant functionality using keyboard shortcuts.

## Installation
1. **Install NVIDIA CUDA Toolkit**
   
   - Visit the [NVIDIA CUDA Downloads](https://developer.nvidia.com/cuda-downloads) to install.
2. **Clone the Repository**
   ```bash
   git clone https://github.com/johnmalek312/Nova-Voice-Assistant.git
   cd Nova-Voice-Assistant
   ```

3. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
5. **Install ffmpeg**
   
   - **Download Installer**: You can download an installer from the [ffmpeg Website](https://ffmpeg.org/download.html).
   
   - **Using Chocolatey**:
     ```bash
     choco install ffmpeg
     ```

## Configuration

1. **API Keys**

   Update the 

config.py

 file with your API key (currently only support openai for llm responses and function calling):
   ```python
   API_KEYS = {
       'OPENAI': "your_openai_api_key"
   }
   ```

2. **TTS Engine Configuration**

   Choose and configure your preferred Text-to-Speech engine in 

config.py

:
   ```python
   Engine = "Piper"  # Options: "ElevenLabs", "OpenAI", "Azure", "GTTS", "Piper"
   ```

3. **Model Configuration**

   Adjust AI model settings in 

config.py

 as needed:
   ```python
   MODEL_CONFIG = {
       'WHISPER_MODEL': "medium",
       'WHISPER_LANGUAGE': "en",
       'LLM_MODEL': "gpt-4o-mini",
       'MAX_MESSAGE_HISTORY': 3, # recommended 3 to reduce token cost
       'timeout': 20
   }
   ```

## Usage

Run the voice assistant using the following command:
```bash
python main.py
```

Once running, Nova will listen for voice commands and respond accordingly. Use the configured hotkeys to control the assistant:

- **Pause Key**: Toggles the assistant on/off (Requires some fixing)
- **Home Key**: Stops the assistant completely
- **Plus Key**: Interrupts any currently playing audio

## TODO

- [ ] **Fix Hotkey Functionalities**: Finalize the setup and handling of hotkeys for controlling the assistant.
- [ ] **Add Support for Gemini.**
- [ ] **Enhance Error Handling.**
- [ ] **Integrate More Tools.**
- [ ] **Expand Configuration Options**: Provide more customizable settings for users to tailor the assistant to their preferences.
- [ ] **User Interface Improvements**: Develop a graphical interface for easier interaction and control.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your enhancements.

## License

#### While the source of this library is open-source, the usage of many of the engines it depends on is not: External engine providers often restrict commercial use in their free plans.
