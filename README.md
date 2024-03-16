# Checkers Analyser

Welcome to the Checkers Analyser, a comprehensive checkers game with advanced features designed for both fun and learning. Developed with Pygame, this project integrates gameplay, analysis tools, online play, and statistical tracking to offer a unique gaming experience.

## Features

- **Graphical User Interface**: Enjoy a fully interactive checkers game with a user-friendly GUI, created using Pygame.
- **Game Analysis**: Learn from your gameplay with an in-built analysis function that helps you understand and improve your strategy.
- **Online Play**: Challenge your friends online using a robust socket-based multiplayer option.
- **Statistical Tracking**: Track your performance over time with a detailed win/loss database, visualized through graphs using SQLite and Matplotlib.

## Configuration

Before you start, you can customize your experience:

- **Online Mode**: Set `is_online` to `True` in `config.py` to enable online play.
- **Screen Adjustment**: Modify `window_height` and `window_width` in `config.py` to fit the game board to your screen.

## Libraries Used

- Pygame
- Sockets
- Matplotlib
- Numpy
- Pickle
- SQLite

## How to Play

1. Run `main.py` to start the game.
2. Click to select a checker piece. Valid moves are highlighted on the board.
3. Click a highlighted square to move your piece. Mandatory jumps are enforced.
4. Play alternates between players. Capture or block all the opponent's pieces to win.
5. When the game ends, press ENTER and enter your name to record your game.
6. The game will then analyse your play. Navigate your moves using the right and left arrow keys.
7. Press the question mark icon for detailed information about the analysis tools.
8. After analysis, press ESCAPE to view your win/loss graph.

## Enjoy Playing

Immerse yourself in this classic game with a modern twist. The Checkers Analyser is more than just a game – it's a tool to sharpen your skills and enjoy the timeless strategy of checkers.
