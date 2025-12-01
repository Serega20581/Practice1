import tkinter as tk
from controller import MainController

try:
    import ttkbootstrap as tb
    _HAS_TTB = True
except Exception:
    _HAS_TTB = False

if __name__ == '__main__':
    if _HAS_TTB:
        root = tb.Window(themename='litera')
    else:
        root = tk.Tk()
    controller = MainController(root)
    root.mainloop()
