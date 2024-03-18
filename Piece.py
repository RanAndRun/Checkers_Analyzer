from Enums import *
from Tile import *
from time import sleep
from pygame import display
from config import *


class Piece:

    def __init__(self, tile: tuple, color: Eplayers, white_img_path, black_img_path):
        self.alive = True
        self.tile = tile
        self.color = color
        self.white_img_path = white_img_path
        self.black_img_path = black_img_path
        if self.color == Eplayers.white:
            self.image = pygame.image.load(white_img_path)
        else:
            self.image = pygame.image.load(black_img_path)

        size = (WINDOW_SIZE / BOARD_SIZE, WINDOW_SIZE / BOARD_SIZE)
        self.image = pygame.transform.scale(self.image, size)

    def move(self, to_tile: tuple[int, int]):
        self.tile = to_tile

    def get_coordinates(self):
        tile_width, tile_height = (
            WINDOW_SIZE / BOARD_SIZE,
            WINDOW_SIZE / BOARD_SIZE,
        )
        x = self.tile[0] * tile_width
        y = (BOARD_SIZE - 1 - self.tile[1]) * tile_height

        return x, y

    def draw(self, screen):
        x, y = self.get_coordinates()
        dest = (x, y)
        screen.blit(self.image, dest)

    def killed(self):
        self.alive = False

    def is_alive(self) -> bool:
        return self.alive

    def __repr__(self):
        position = f"({self.tile[0]}, {self.tile[1]})" if self.tile else "None"
        status = "Alive" if self.alive else "Killed"
        return f"{self.color.name} {type(self).__name__} at {position} - {status}!"

    def __deepcopy__(self, memo):
        # Create an instance of the correct subclass
        copied_piece = self.__class__.__new__(self.__class__)
        memo[id(self)] = copied_piece

        # Copy attributes
        copied_piece.alive = self.alive
        copied_piece.tile = self.tile
        copied_piece.color = self.color
        # Assuming you have paths for images as class variables like white_img_path, black_img_path
        copied_piece.image = pygame.image.load(
            self.white_img_path if self.color == Eplayers.white else self.black_img_path
        )

        return copied_piece
