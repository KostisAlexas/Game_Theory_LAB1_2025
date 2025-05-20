# launch.py
"""
Αυτό το αρχείο λειτουργεί ως το εκτελέσιμο entry point για την εφαρμογή GUI.
Τρέξε το με:
    python launch.py
"""
import tkinter as tk
from gui import GameGUI

def main():
    root = tk.Tk()
    app = GameGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
