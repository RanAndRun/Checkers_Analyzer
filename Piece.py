from Enums import *
from Tile import *
from time import sleep
from pygame import display


class Piece:
    def __init__(self, tile: Tile, color: EColor, white_img_path, black_img_path):
        self.alive = True
        self.tile = tile
        self.color = color
        if self.color == EColor.white:
            self.image = pygame.image.load(white_img_path)
        else:
            self.image = pygame.image.load(black_img_path)

    def move(self, to_tile: Tile):
        self.tile = to_tile

    def draw(self):
        dest = self.tile.x_point, self.tile.y_point
        screen.blit(self.image, dest=dest)

    def killed(self):
        self.alive = False

    def is_alive(self) -> bool:
        return self.alive

    def __str__(self):
        position = f"({self.tile.column}, {self.tile.row})" if self.tile else "None"
        status = "Alive" if self.alive else "Killed"
        return f"{self.color.name}] at {position} - {status}"
