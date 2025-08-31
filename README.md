# File: README.md
# Win7-style Chess (Python + Tkinter)

A lightweight chess app designed to give a Windows 7-ish look using Tkinter and python-chess.

Requirements:
- Python 3.8+
- Install dependencies: `pip install -r requirements.txt`

Run:
```
python main.py
```

Features included:
- 2-player local play
- Play vs a simple AI (material-only minimax with alpha-beta pruning)
- Undo, New Game, Flip Board
- Move list in SAN format
- Pawn promotion dialog

Notes & next steps:
- The AI is intentionally small and configured for quick response (change depth in GUI).
- If you want stronger AI, I can show how to integrate Stockfish (requires downloading the engine binary) and run it with python-chess's engine module.
- If you want Win7-specific piece art or sound effects, provide assets or I can recommend sprite packs and show how to load them.
