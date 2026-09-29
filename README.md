# AI Chess

Chess game in Python/Pygame with a custom AI opponent.

## Features
- Start menu: Player vs Player, Play as White/Black vs AI, AI vs AI
- 4 difficulty levels (search depth 1–4)
- Minimax search with alpha-beta pruning and capture-first move ordering
- Custom board copying (~7x faster than deepcopy)
- Checkmate and stalemate detection

## Run
pip install pygame
python src/main.py

In game: R = restart, T = theme, Esc = menu

## Credits
Board, pieces, and GUI based on AlejoG10's python-chess-ai-yt tutorial.
The AI (src/ai.py), menu, game modes, and bug fixes are my own work.