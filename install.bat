@echo off
ren "scripts_data\general_data_example.json" "general_data.json"
ren "scripts_data\client_secret_info.json" "client_secret.json"
ren "config_example.py" "config.py"
echo Files renamed successfully.
echo This script does not perform all the necessary steps to install the project.

setlocal

:: Create target directory if it doesn't exist
mkdir "models\PiperVoice" 2>nul

:: Check and download the ONNX model
if not exist "models\PiperVoice\amy-low-voice.onnx" (
    echo Downloading amy-low-voice.onnx...
    curl -L -o "models\PiperVoice\amy-low-voice.onnx" ^
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx?download=true"
) else (
    echo amy-low-voice.onnx already exists. Skipping download.
)

:: Check and download the JSON config
if not exist "models\PiperVoice\amy-low-config.json" (
    echo Downloading amy-low-config.json...
    curl -L -o "models\PiperVoice\amy-low-config.json" ^
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx.json?download=true"
) else (
    echo amy-low-config.json already exists. Skipping download.
)

echo Done.
exit /b