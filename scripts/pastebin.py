"""Wrapper for Pastebin API library main functions with authentication in init."""

from pbwrap import Pastebin as OriginalPastebin  # Import original class and rename it
from .data_manager import DataManager
from tool_registry import register_tool
class PastebinWrapper:
    """
    A simplified wrapper for the Pastebin API, exposing only the most commonly used functions.
    All functions are now implemented as class methods.
    """
    
    _pastebin = None

    @classmethod
    def authenticate(cls, api_dev_key, username, password, verify_ssl=True):
        cls._pastebin = OriginalPastebin(api_dev_key=api_dev_key, verify_ssl=verify_ssl)
        try:
            result = cls._pastebin.authenticate(username, password)
            if not result:
                print("Authentication failed: Invalid username or password.")
            elif "Bad API request" in result:
                print(f"Authentication failed: {result}")
            else:
                print(f"Authentication successful. User key: {result[:10]}...")
        except Exception as e:
            print(f"Authentication failed with an exception: {e}")

    @classmethod
    @register_tool()
    def create_paste(
        cls,
        paste_code,
        private=2,
        name=None,
        expire_date=None,
        format=None,
    ):
        """
Creates a new paste on Pastebin.

Parameters:
- paste_code: The content of the paste.
- private: Visibility of the paste (0 = public, 1 = unlisted, 2 = private).
- name: Optional name for the paste.
- expire_date: Optional expiration date for the paste.
- format: Optional syntax highlighting format for the paste eg. 'python', 'javascript'.

Returns:
The new paste URL if successful, else an error message.
        """
        return cls._pastebin.create_paste(
            api_paste_code=paste_code,
            api_paste_private=private,
            api_paste_name=name,
            api_paste_expire_date=expire_date,
            api_paste_format=format,
        )

    @classmethod
    @register_tool()
    def get_trending_paste(cls):
        """
        Retrieves trending pastes from Pastebin.
        Returns a list of trending paste objects.
        """
        return cls._pastebin.get_trending()

    @classmethod
    @register_tool()
    def get_raw_paste(cls, paste_id):
        """
        Retrieves the raw text of a paste.
        Returns the paste content for the given paste ID.
        """
        return cls._pastebin.get_raw_paste(paste_id)

    @classmethod
    @register_tool()
    def delete_paste(cls, paste_key):
        """
        Deletes a user paste on Pastebin.
        Returns the deletion result or an error message.
        """
        return cls._pastebin.delete_user_paste(paste_key)

PastebinWrapper.authenticate(DataManager.pastebin["api_key"], DataManager.pastebin["username"], DataManager.pastebin["password"])  # Initialize the wrapper with your credentials



register_tool()(PastebinWrapper.create_paste) # unfortunately, the decorator does not work properly with class methods
register_tool()(PastebinWrapper.get_trending_paste) # :'( so this is needed
register_tool()(PastebinWrapper.get_raw_paste)

