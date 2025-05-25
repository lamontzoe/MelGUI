import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # Resources are bundled at the root of _MEIPASS
        base_path = sys._MEIPASS
    else:
        # Not running in a PyInstaller bundle.
        # This assumes this utils.py is in src/, and main.py is in src/,
        # and resources (models/, Resources/) are at the project root.
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    return os.path.join(base_path, relative_path)
