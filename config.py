# config.py
# Description: This file contains the configuration for the game.
import os, pygame

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
GREY = (100, 100, 100)

FPS = 30

EXPLAIN = os.path.join("assets", "scroll.png")
EXPLAIN = pygame.image.load(EXPLAIN)
EXPLAIN = pygame.transform.scale(EXPLAIN, SIZE)

QUESTION_MARK = os.path.join("assets", "questionMark.png")
QUESTION_MARK = pygame.image.load(QUESTION_MARK)
QUESTION_MARK = pygame.transform.scale(QUESTION_MARK, (TILE_SIZE, TILE_SIZE))

BACKROUND = os.path.join("assets", "backround.jpg")
BACKROUND = pygame.image.load(BACKROUND)
BACKROUND = pygame.transform.scale(BACKROUND, SIZE)

YOU_WIN = os.path.join("assets", "you_win.png")
YOU_WIN = pygame.image.load(YOU_WIN)

YOU_LOSE = os.path.join("assets", "you_lose.png")
YOU_LOSE = pygame.image.load(YOU_LOSE)
