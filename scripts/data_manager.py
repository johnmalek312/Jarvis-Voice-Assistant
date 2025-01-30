# data_manager.py

import json
import os

class DataManager:
    current_dir = os.path.dirname(__file__)
    # Define the file paths inside the DataManager
    FILE_PATHS = {
        "general_data.json": current_dir + "/general_data.json",
        "website_dict.json": current_dir + "/website_dict.json"
    }

    data_cache = {}

    @classmethod
    def save_data_cache(cls, file_name: str=""):
        """Saves the data cache to their respective JSON files."""
        if file_name:
            data = cls.data_cache.get(file_name)
            if data:
                file_path = cls.FILE_PATHS.get(file_name)
                if file_path:
                    with open(file_path, 'w') as f:
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
        data = cls._load_data('general_data.json')
        return data.get('user_data', {}).get('personal_information', {})

    @classmethod
    @property
    def websites(cls):
        """Access websites data like DataManager.websites."""
        return cls._load_data('website_dict.json')
    @classmethod
    @property
    def meteosource(cls):
        """Access meteosource data for the weather (api key)."""
        data = cls._load_data('general_data.json')
        return data.get('meteosource', {})
    @classmethod
    @property
    def google_search(cls):
        """Access meteosource data for the weather (api key)."""
        data = cls._load_data('general_data.json')
        return data.get('google_search', {})
    @classmethod
    @property
    def url_shortner(cls):
        """Access URL shortener data for the TinyURL API key."""
        data = cls._load_data('general_data.json')
        return data.get('url_shortner', {})
