import webbrowser
import os
import sys
from .data_manager import DataManager as dm
# Get the directory of the current file
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from tool_registry import register_tool

default_browser = webbrowser.get()
@register_tool()
def open_new_tab(url: str = None) -> None | str:
    """Opens a new tab with the specified URL. If url is not specified, opens a new tab with the default homepage"""
    try:
        if url is None:
            default_browser.open_new_tab("https://")
        else:
            default_browser.open_new_tab(url)
        return "New tab opened in browser"
    except Exception as e:
        return f"Error while opening new tab: {e}"

@register_tool()
def open_shortcut(shortcut: str) -> bool | str:
    """Opens a website using predefined shortcut like using 'github' to open 'https://github.com'"""
    try:
        websites = dm.websites
        if shortcut.lower() in websites:
            open_new_tab(websites[shortcut.lower()])
            return True
        return False
    except Exception as e:
        return f"Error while opening shortcut: {e}"

@register_tool()
def list_shortcuts() -> list | str:
    """Returns list of all available shortcuts"""
    try:
        return sorted(list(dm.websites.keys()))
    except Exception as e:
        return f"Error while listing shortcuts: {e}"

@register_tool()
def open_google(query: str = "") -> None | str:
    """Opens browser with a Google search query in browser. Try not to use this unless specified otherwise use your own knowledge"""
    try:
        if query:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        else:
            search_url = "https://www.google.com"
        open_new_tab(search_url)
        return "Google search opened in browser"
    except Exception as e:
        return f"Error while searching Google: {e}"

@register_tool()
def open_youtube(search_query: str = None) -> None | str:
    """Opens YouTube, optionally with a search query"""
    try:
        if search_query:
            url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
        else:
            url = f"https://www.youtube.com"
        open_new_tab(url)
        return "YouTube opened in browser"
    except Exception as e:
        return f"Error while opening YouTube: {e}"

register_tool(open_new_tab)
register_tool(open_shortcut)
register_tool(list_shortcuts)
register_tool(open_google)
register_tool(open_youtube)
