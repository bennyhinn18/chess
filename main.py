"""
Win7-style Chess (Python + tkinter)
Files:
- main.py (entrypoint)
- gui.py (tkinter GUI)
- ai.py (simple minimax AI)
- assets/ (optional folder for piece images if you want to swap unicode for images)
- requirements.txt

Run: python main.py
"""
from gui import ChessGUI

if __name__ == '__main__':
    ChessGUI().run()
