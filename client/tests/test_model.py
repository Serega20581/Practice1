import sys
import os
import tkinter as tk

# Ensure repository root is on sys.path so 'client' package can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from client.controller import MainController


def test_controller_instantiation():
    # Smoke test: instantiate controller with a hidden Tk root
    root = tk.Tk()
    root.withdraw()
    c = MainController(root)
    # controller should expose a books cache attribute
    assert hasattr(c, '_books')
    # cleanup
    try:
        root.destroy()
    except Exception:
        pass