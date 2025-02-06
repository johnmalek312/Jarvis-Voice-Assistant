"""
This module provides tools for seamless data sharing between the user and the AI assistant.
The module offers functionality to:
- Retrieve content from the clipboard
- Set content to the clipboard
- Clear the clipboard contents
- Get user input through interactive dialog boxes
- Display messages to the user in a dialog box
- Get file or folder paths using system dialogs
- Get color selections using a color picker dialog
These operations facilitate smooth data transfer and communication with the assistant.
"""
import threading
from pathlib import Path

import pyperclip
import tkinter as tk
from tkinter import filedialog, colorchooser, ttk
from tool_registry import register_tool
from functools import partial


@register_tool()
def get_clipboard() -> str:
    """Retrieve the current content of the system clipboard.

    Returns:
        str: The clipboard contents as a string. If an error occurs, an error message detailing the exception is returned.
    """
    """Get the current clipboard content. Returns the content as a string."""
    try:
        return pyperclip.paste()
    except Exception as e:
        return f"Error while getting clipboard content: {e}"

@register_tool()
def set_clipboard(text: str) -> None | str:
    """Set the clipboard content"""
    try:
        pyperclip.copy(text)
        return "Clipboard content set successfully"
    except Exception as e:
        return f"Error while setting clipboard content: {e}"

@register_tool()
def clear_clipboard() -> None | str:
    """Clears the clipboard content"""
    try:
        pyperclip.copy("")
    except Exception as e:
        return f"Error while clearing clipboard content: {e}"
    

@register_tool()
def get_input(message: str, multi_line=False) -> None | str:
    """
    Displays an interactive dialog box to collect user input with a customizable interface.
    Parameters:
    message : str
        The prompt message to display to the user in the dialog box
    multi_line : bool, optional
        If True, shows a multi-line text area. If False, shows a single-line entry field (default: False)
    Returns the user input as a string if successful.
    """
    try:
        # Create the root window and hide it
        root = tk.Tk()
        root.title("Input")
        root.configure(bg='#f4f4f4')  # Light gray background

        # Add a label with the message
        label = tk.Label(root, text=message, bg='#f4f4f4', fg='#333333', font=('Arial', 12))
        label.pack(pady=10)

        # Add an entry field or text field for user input
        if multi_line:
            root.minsize(237, 223)
            root.geometry("400x270")
            input_widget = tk.Text(root, font=('Arial', 12), bg='#ffffff', fg='#333333', bd=2, relief='solid', height=5)
            input_widget.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        else:
            root.minsize(233, 155)
            root.geometry("400x200")
            input_widget = tk.Entry(root, font=('Arial', 12), bg='#ffffff', fg='#333333', bd=2, relief='solid',
                                    justify='center')
            input_widget.pack(pady=10, padx=20, fill=tk.X)

        # Create a function to handle the submit action
        def on_submit():
            nonlocal user_input
            user_input = input_widget.get("1.0", tk.END).strip() if multi_line else input_widget.get().strip()
            root.destroy()

        # Add buttons with a modern design
        button_frame = tk.Frame(root, bg='#f4f4f4')
        submit_button = ttk.Button(button_frame, text="Submit", command=on_submit)
        submit_button.pack(side=tk.LEFT, padx=10, pady=5, ipadx=10, ipady=5)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=root.destroy)
        cancel_button.pack(side=tk.LEFT, padx=10, pady=5, ipadx=10, ipady=5)
        button_frame.pack(pady=10)

        # Apply modern styling to buttons
        submit_button.config(style="TButton")
        cancel_button.config(style="TButton")

        # Make the window always on top until it's ready to close
        root.attributes('-topmost', True)
        root.update()
        root.attributes('-topmost', False)

        # Wait for the user to provide input or cancel
        user_input = None
        center_window(root)
        root.wait_window()

        return user_input
    except Exception as e:
        return f"Error getting input: {e}"

@register_tool()
def show_message_box(message: str, title: str = "Message") -> str:
    """Shows a message box with the given message with a custom title and a copy button"""
    try:
        #create thread event
        finished = threading.Event()
        def show_message_box():
            root = tk.Tk()
            root.title(title)
            root.configure(bg='#f4f4f4')  # Set the background color to light gray

            # Add a text widget for displaying the message
            text_widget = tk.Text(root, wrap=tk.WORD, height=10, width=40, bg='#ffffff', fg='#333333',
                                  font=('Arial', 12))
            text_widget.insert("1.0", message)
            text_widget.configure(state=tk.DISABLED)  # Make the text read-only
            text_widget.pack(padx=20, pady=0, fill=tk.BOTH, expand=True)

            # Create a stylish frame for buttons
            button_frame = tk.Frame(root, bg='#f4f4f4')
            copy_button = ttk.Button(button_frame, text="Copy", command=partial(set_clipboard, message))
            copy_button.pack(side=tk.LEFT, padx=10, pady=5, ipadx=10, ipady=5)
            close_button = ttk.Button(button_frame, text="Close", command=root.destroy)
            close_button.pack(side=tk.LEFT, padx=10, pady=5, ipadx=10, ipady=5)
            button_frame.pack(pady=10)

            # Apply modern styling to buttons
            copy_button.config(style="TButton")
            close_button.config(style="TButton")

            # Center the window
            center_window(root)

            # Make the window always on top until it's ready to close
            root.attributes('-topmost', True)
            root.update()
            root.attributes('-topmost', False)
            finished.set()
            root.wait_window()

        thread = threading.Thread(target=show_message_box)
        thread.start()
        finished.wait()
        return "Message displayed successfully"
    except Exception as e:
        return f"Error displaying message box: {e}"

@register_tool()
def get_path(type: str = "file") -> str:
    """Get the path of a file or folder selected by the user via a system dialog

    This function opens a native file/folder selection dialog window that allows the user
    to interactively choose either a file or directory path. The dialog window type shown
    depends on the 'type' parameter.

        type (str): Dialog type to show - use 'file' to select a file (default) or 'folder' 
                    to select a directory/folder

    the path is returned as a string. If the user cancels the dialog, an empty string is returned.

    Examples:
        # Select a file
        file_path = get_path()
        # or explicitly
        file_path = get_path("file")
        
        # Select a folder
        folder_path = get_path("folder")
    """
    root = tk.Tk()
    root.withdraw()
    path = ""
    root.wm_attributes("-topmost", 1)
    if type.lower() == "file":
        path = tk.filedialog.askopenfilename(parent=root)
    elif type.lower() == "folder":
        path = tk.filedialog.askdirectory(parent=root)
    root.destroy()
    return path


@register_tool()
def get_color() -> str | None:
    """Get the color selected by the user via a color picker dialog

    This function opens a native color picker dialog window that allows the user
    to interactively choose a color. The selected color is returned as a hexadecimal
    color code string.

    Returns:
        str | None: The hexadecimal color code of the selected color, or None if cancelled

    """
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)
    center_window(root)
    result = colorchooser.askcolor()
    root.destroy()
    return result[1] if result else None




def center_window(window):
    """Center a Tkinter window on the screen"""
    window.update_idletasks()
    width = window.winfo_width()
    frm_width = window.winfo_rootx() - window.winfo_x()
    win_width = width + 2 * frm_width
    height = window.winfo_height()
    titlebar_height = window.winfo_rooty() - window.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = window.winfo_screenwidth() // 2 - win_width // 2
    y = window.winfo_screenheight() // 2 - win_height // 2
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))