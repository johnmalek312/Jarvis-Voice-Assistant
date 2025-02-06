import os
import glob
from pathlib import Path

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



@register_tool()
def get_username_folder() -> str:
    """Get the path of the current user's directory"""
    return str(Path.home())

@register_tool()
def get_desktop_folder() -> str:
    """Get the default desktop path for the current user"""
    import win32com.client

    shell = win32com.client.Dispatch("WScript.Shell")
    return (shell.SpecialFolders("Desktop"))

@register_tool()
def get_downloads_folder() -> str:
    """Returns the path to the user's Downloads folder."""
    try:
        import win32com.client
        return win32com.client.Dispatch("WScript.Shell").SpecialFolders("{374DE290-123F-4565-9164-39C4925E467B}")
    except Exception as e:
        return f"Error: {e}"

@register_tool()
def get_documents_folder() -> str:
    """Returns the path to the user's Documents folder."""
    try:
        import win32com.client
        return win32com.client.Dispatch("WScript.Shell").SpecialFolders("MyDocuments")
    except Exception as e:
        return f"Error: {e}"

@register_tool()
def rename_file(file_path: str, new_name: str) -> str:
    """Rename a file or folder at the specified path to the new name"""
    try:
        if not Path(file_path).exists():
            return f"File/Folder does not exist: {file_path}"
        new_path = Path(file_path).parent / new_name
        Path(file_path).rename(new_path)
        return f"File/Folder renamed to: {new_name}"
    except Exception as e:
        return f"Error renaming file: {e}"

@register_tool()
def move_file(file_path: str, destination_path: str) -> str:
    """Move a file or folder from the source path to the destination path"""
    try:
        if not Path(file_path).exists():
            return f"File/Folder does not exist: {file_path}"
        Path(file_path).rename(destination_path)
        return f"File/Folder moved to: {destination_path}"
    except Exception as e:
        return f"Error moving file: {e}"

@register_tool()
def delete_file(file_path: str) -> str:
    """Delete a file or folder at the specified path"""
    try:
        if Path(file_path).is_dir():
            Path(file_path).rmdir()
            return f"Folder deleted: {file_path}"
        elif Path(file_path).is_file():
            Path(file_path).unlink()
            return f"File deleted: {file_path}"
        else:
            Path(file_path).unlink()
            return f"Deleted: {file_path}"
    except Exception as e:
        return f"Error deleting file: {e}"
@register_tool()
def create_folder(folder_path: str) -> str:
    """Create a new folder at the specified path"""
    try:
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        return f"Folder created: {folder_path}"
    except Exception as e:
        return f"Error creating folder: {e}"
@register_tool()
def create_file(file_path: str) -> str:
    """Create a new file at the specified path"""
    try:
        Path(file_path).touch()
        return f"File created: {file_path}"
    except Exception as e:
        return f"Error creating file: {e}"
@register_tool()
def open_file(file_path: str) -> str:
    """Open a file or folder at the specified path using the default application"""
    try:
        if not Path(file_path).exists():
            return f"File does not exist: {file_path}"
        os.startfile(file_path)
        if Path(file_path).is_dir():
            return f"Opened folder: {file_path}"
        return f"Opened file: {file_path}"
    except Exception as e:
        return f"Error opening file: {e}"
@register_tool()
def list_files(folder_path: str) -> list[str]:
    """List all files and folders in the specified directory"""
    try:
        return [str(f) for f in Path(folder_path).iterdir()]
    except Exception as e:
        return [f"Error listing files: {e}"]
@register_tool()
def get_file_details(file_path: str) -> str:
    """Get details about a file or folder at the specified path"""
    try:
        if not Path(file_path).exists():
            return f"File/Folder does not exist: {file_path}"
        details = Path(file_path).stat()
        return f"File/Folder details: {details}"
    except Exception as e:
        return f"Error getting file details: {e}"

@register_tool()
def get_file_size(file_path: str) -> str:
    """Get the size of a file in bytes"""
    try:
        if not Path(file_path).exists():
            return f"File does not exist: {file_path}"
        size = Path(file_path).stat().st_size
        return f"File size: {size} bytes"
    except Exception as e:
        return f"Error getting file size: {e}"
