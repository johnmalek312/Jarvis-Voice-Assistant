import webbrowser
import json
import os
import sys
from functools import cache

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from tool_registry import register_tool

# Dictionary mapping short names to full URLs like youtube to https://www.youtube.com
with open(os.path.join(current_dir, 'website_dict.json'), 'r') as f:
    websites = json.load(f)

default_browser = webbrowser.get()

@register_tool()
def open_new_tab(url: str = None) -> None:
    """Opens a new tab with the specified URL. If url is not specified, opens a new tab with the default homepage"""
    if url is None:
        default_browser.open_new_tab("https://")
    else:
        default_browser.open_new_tab(url)
@register_tool()
def open_shortcut(shortcut: str) -> bool:
    """Opens a website using predefined shortcut like using 'github' to open 'https://github.com'"""
    if shortcut.lower() in websites:
        open_new_tab(websites[shortcut.lower()])
        return True
    return False
@register_tool()
def list_shortcuts() -> list:
    """Returns list of all available shortcuts"""
    return sorted(list(websites.keys()))

@register_tool()
def search_google(query: str) -> None:
    """Performs a Google search in browser. Try not to use this unless specified otherwise use your own knowledge"""
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    open_new_tab(search_url)
@register_tool()
def open_youtube(search_query: str = None) -> None:
    """Opens YouTube, optionally with a search query"""
    if search_query:
        url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
    else:
        url = websites['youtube']
    open_new_tab(url)
