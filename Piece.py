from Enums import *
from Tile import *
from time import sleep
from pygame import display


class Piece:

    scale_factor_width = 1
    scale_factor_height = 1

    def __init__(self, tile: Tile, color: EColor, white_img_path, black_img_path):
        self.alive = True
        self.tile = tile
        self.color = color
        self.white_img_path = white_img_path
        self.black_img_path = black_img_path
        if self.color == EColor.white:
            self.image = pygame.image.load(white_img_path)
        else:
            self.image = pygame.image.load(black_img_path)

    def move(self, to_tile: Tile):
        self.tile = to_tile

    def draw(self, screen):
        dest = (
            self.tile.x_point * Piece.scale_factor_width,
            self.tile.y_point * Piece.scale_factor_height,
        )
        screen.blit(self.image, dest=dest)

    @classmethod
    def update_scale_factors(cls, scale_factor_width, scale_factor_height):
        cls.scale_factor_width = scale_factor_width
        cls.scale_factor_height = scale_factor_height

    def killed(self):
        self.alive = False

    def is_alive(self) -> bool:
        return self.alive

    def __repr__(self):
        position = f"({self.tile.column}, {self.tile.row})" if self.tile else "None"
        status = "Alive" if self.alive else "Killed"
        return f"{self.color.name}] at {position} - {status}"

    def __deepcopy__(self, memo):
        # Create an instance of the correct subclass
        copied_piece = self.__class__.__new__(self.__class__)
        memo[id(self)] = copied_piece

        # Copy attributes
        copied_piece.alive = self.alive
        copied_piece.tile = copy.deepcopy(self.tile, memo)
        copied_piece.color = self.color
        # Assuming you have paths for images as class variables like white_img_path, black_img_path
        copied_piece.image = pygame.image.load(
            self.white_img_path if self.color == EColor.white else self.black_img_path
        )

        return copied_piece
