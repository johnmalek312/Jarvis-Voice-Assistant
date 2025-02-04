import os
import glob
from tool_registry import register_tool

@register_tool()
def get_apps() -> list[str] | str:
    """Gets the list of all available applications and returns their path that can be used in the open_app function or other functions to open or do some operation."""
    root_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs')
    shortcut_paths = []

    # Get all .lnk files in the root folder
    for filepath in glob.glob(os.path.join(root_folder, '*.lnk')):
        relative_path = os.path.relpath(filepath, start=root_folder)
        shortcut_paths.append(relative_path)

    # Get all .lnk files in the immediate subfolders
    for subfolder in glob.glob(os.path.join(root_folder, '*', '')):
        for filepath in glob.glob(os.path.join(subfolder, '*.lnk')):
            relative_path = os.path.relpath(filepath, start=root_folder)
            shortcut_paths.append(relative_path)

    return shortcut_paths

@register_tool()
def open_shortcut(path: str) -> str:
    """Opens a file or shortcut at the given path, the path can be obtained from the get_apps function. Use %USERNAME% instead of the actual username in the path."""
    try:
        path.replace('%USERNAME%', os.getenv('USERNAME'))
        root_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs')
        # Convert relative path to absolute path
        absolute_path = os.path.join(root_folder, path)

        # Check if the file exists before trying to open it
        if os.path.exists(absolute_path):
            os.startfile(absolute_path)  # This opens the shortcut
            return f"Opened: {absolute_path}"
        else:
            return f"Shortcut does not exist: {absolute_path}"
    except Exception as e:
        return f"Failed to open shortcut: {str(e)}"

