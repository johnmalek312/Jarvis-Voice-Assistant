# JARVIS

**JARVIS** is an AI voice assistant (inspired by `JARVIS` from Iron Man) that leverages Retrieval-Augmented Generation (RAG) and LlamaIndex to provide intelligent and context-aware interactions. Designed to assist users through voice commands, Jarvis integrates various AI models and tools to deliver a seamless experience.

## Features

- **Voice Interaction**: Communicate with Jarvis using natural language.
- **Retrieval-Augmented Generation (RAG)**: Enhances responses by retrieving relevant information from indexed data.
- **Integration of various services**: This includes gmail, [gpt researcher](https://github.com/assafelovic/gpt-researcher/), pastebin, wikipedia and more.
- **LlamaIndex Integration**: Efficiently handles data indexing and retrieval.
- **Multiple TTS Engines**: Supports ElevenLabs, Piper, OpenAI, Azure, and GTTS for text-to-speech functionality.
- **Configurable AI Models**: Customize AI behavior with different model configurations.
- **Hotkey Controls**: Manage assistant functionality using keyboard shortcuts.

## Installation
1. **Install NVIDIA CUDA Toolkit**
   
   - Visit the [NVIDIA CUDA Downloads](https://developer.nvidia.com/cuda-downloads) to install.
2. **Clone the Repository**
   ```bash
   git clone https://github.com/johnmalek312/Jarvis-Voice-Assistant.git
   cd Jarvis-Voice-Assistant
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
## Workflow diagram
![Image](https://github.com/user-attachments/assets/b18b71c9-aa85-44d1-8756-6a6a67444e88)

## Minimal Configuration
1. **Run  `install.bat`**
2. **API Keys**

   Update the `config.py` file with your required API keys:
   ```python
   APIConfig.GEMINI = "your_gemini_api_key" # required
   APIConfig.TAVILY = "your_tavily_api_key" # highly recommended for researching feature.
   ```

## Usage

Run the voice assistant from venv using the following command:
```bash
python main.py
```

Once running, Jarvis will listen for voice commands and respond accordingly. Use the configured hotkeys to control the assistant:

- **Pause Key**: Toggles the assistant on/off.
- **Home Key**: Close the app.
- **Plus Key**: Interrupts any currently playing audi.

## Features

To integrate with more external services, you have to add you api keys and info in `scripts_data/general_data.json`

You can also enable/disable features in `config.py` from the `FEATURES` class.

## TODO

- [x] **Fix Hotkey Functionalities**: Finalize the setup and handling of hotkeys for controlling the assistant.
- [x] **Add Support for Gemini.**
- [ ] **Add image support**: This includes image generation, recognition and extraction from clipboard.
- [ ] **User Interface Improvements**: Develop a graphical interface for easier interaction and control.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your enhancements.

## License

#### While the source of this library is open-source, the usage of many of the engines it depends on is not: External engine providers often restrict commercial use in their free plans.
