# config.py
# Description: This file contains the configuration for the game.

WINDOW_SIZE = 1000
BOARD_SIZE = 8
GAME_ONLINE = False

TILE_SIZE = WINDOW_SIZE / BOARD_SIZE
SIZE = (WINDOW_SIZE, WINDOW_SIZE)
DEPTH = 3
DISCONNECT_MSG = "DISCONNECT!"
DISCONNECT_ACK_MSG = "DISCONNECT_ACK!"
BUFFER_SIZE = 2048
SERVER_ADDRESS = ("10.100.102.33", 12345)


BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

FPS = 30
