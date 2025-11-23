import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def format_message(template, data):
    """
    Replaces {name} in the template.
    """
    try:
        return template.format(
            name=data.get('name', '')
        )
    except KeyError as e:
        return f"Error processing template: Missing key {e}"