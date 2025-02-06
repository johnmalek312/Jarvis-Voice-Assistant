# data_manager.py

import json
import os
from pathlib import Path

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from llm_response_generator import LLMResponseGenerator
    from main import VoiceAssistant
    from llama_index.core.callbacks import TokenCountingHandler


class DataManager:
    # Define the file paths inside the DataManager
    FILE_PATHS = {
        "general_data.json": Path("scripts_data/general_data.json").resolve(),
    }

    llm = None
    va = None
    token_counter = None
    data_cache = {}

    @classmethod
    def save_data_cache(cls, file_name: str=""):
        """Saves the data cache to their respective JSON files."""
        if file_name:
            data = cls.data_cache.get(file_name)
            if data:
                file_path = cls.FILE_PATHS.get(file_name)
                if file_path:
                    with open(file_path, 'w', encoding="utf-8") as f:
                        json.dump(data, f, indent=4)
        else:
            for file_name, data in cls.data_cache.items():
                file_path = cls.FILE_PATHS.get(file_name)
                if file_path:
                    with open(file_path, 'w') as f:
                        json.dump(data, f, indent=4)

    @classmethod
    def _load_data(cls, file_name):
        """Loads data from a JSON file lazily when requested."""
        if file_name not in cls.data_cache:
            file_path = cls.FILE_PATHS.get(file_name)
            if file_path and os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    cls.data_cache[file_name] = data
            else:
                raise FileNotFoundError(f"File '{file_name}' not found.")
        return cls.data_cache[file_name]

    @classmethod
    @property
    def user(cls):
        """Access user data directly like DataManager.user."""
        data = cls._load_data("general_data.json")
        return data.get('user_data', {}).get('personal_information', {})

    @classmethod
    @property
    def meteosource(cls):
        """Access meteosource data for the weather (api key)."""
        data = cls._load_data("general_data.json")
        return data.get('meteosource', {})
    @classmethod
    @property
    def google_search(cls):
        """Access meteosource data for the weather (api key)."""
        data = cls._load_data("general_data.json")
        return data.get('google_search', {})
    @classmethod
    @property
    def url_shortner(cls):
        """Access URL shortener data for the TinyURL API key."""
        data = cls._load_data("general_data.json")
        return data.get('url_shortner', {})
    @classmethod
    @property
    def browser(cls):
        """Access browser data for the browser settings."""
        data = cls._load_data("general_data.json")
        return data.get('browser_data', {})
    @classmethod
    @property
    def pastebin(cls):
        """Access pastebin data for the pastebin settings."""
        data = cls._load_data("general_data.json")
        return data.get('pastebin', {})
