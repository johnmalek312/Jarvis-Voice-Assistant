"""Wrapper for Pastebin API library main functions with authentication in init."""

from pbwrap import Pastebin as OriginalPastebin  # Import original class and rename it
from .data_manager import DataManager
from tool_registry import register_tool
from logger import app_logger as logging
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
                logging.warning("Authentication failed: Invalid username or password.")
            elif "Bad API request" in result:
                logging.warning(f"Authentication failed: {result}")
        except Exception as e:
            logging.warning(f"Authentication failed with an exception: {e}")

    @classmethod
    @register_tool()
    def create_paste(
        cls,
        paste_code: str,
        visibility: int = 0,
        name: str = None,
        format: str = None,
    ) -> str:
        """
Creates a new paste on Pastebin.

Parameters:
- paste_code: The content of the paste.
- visibility: Visibility of the paste (0 = public, 1 = unlisted, 2 = private) dont pass it unless specified.
- name: Optional name for the paste.
- expire_date: Optional expiration date for the paste.
- format: Optional syntax highlighting format for the paste eg. 'python', 'javascript'.

Returns:
The new paste URL if successful, else an error message.
        """
        return cls._pastebin.create_paste(
            api_paste_code=paste_code,
            api_paste_private=visibility,
            api_paste_name=name,
            api_paste_expire_date=None,
            api_paste_format=format,
        )

    @classmethod
    @register_tool()
    def get_trending_paste(cls) -> list[dict]:
        """
        Retrieves trending pastes from Pastebin.
        Returns a list of trending paste objects.
        """
        return cls._pastebin.get_trending()

    @classmethod
    @register_tool()
    def get_raw_paste(cls, paste_id: str) -> str:
        """
        Retrieves the raw text of a paste.
        Returns the paste content for the given paste ID.
        """
        return cls._pastebin.get_raw_paste(paste_id)

    @classmethod
    @register_tool()
    def delete_paste(cls, paste_key: str) -> str:
        """
        Deletes a user paste on Pastebin.
        Returns the deletion result or an error message.
        """
        return cls._pastebin.delete_user_paste(paste_key)

PastebinWrapper.authenticate(DataManager.pastebin["api_key"], DataManager.pastebin["username"], DataManager.pastebin["password"])  # Initialize the wrapper with your credentials



register_tool()(PastebinWrapper.create_paste) # unfortunately, the decorator does not work properly with class methods
register_tool()(PastebinWrapper.get_trending_paste) # :'( so this is needed
register_tool()(PastebinWrapper.get_raw_paste)

