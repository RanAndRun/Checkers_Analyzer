from Enums import *
from Tile import *
from time import sleep
from pygame import display


class Piece:

    scale_factor_width = 1
    scale_factor_height = 1

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

        size = (window_width / 8, window_height / 8)
        self.image = pygame.transform.scale(self.image, size)

    def move(self, to_tile: tuple[int, int]):
        self.tile = to_tile

    def get_coordinates(self):
        tile_width, tile_height = (
            window_width / board_size,
            window_height / board_size,
        )
        x = self.tile[0] * tile_width
        # Invert the y-coordinate so (0,0) is at the top-left instead of the bottom-left
        y = (board_size - 1 - self.tile[1]) * tile_height
        return x, y

    def draw(self, screen):
        # Assuming self.tile is a Tile object with x, y pixel coordinates
        x, y = self.get_coordinates()
        dest = (
            x * Piece.scale_factor_width,
            y * Piece.scale_factor_height,
        )
        screen.blit(self.image, dest)

    @classmethod
    def update_scale_factors(cls, scale_factor_width, scale_factor_height):
        cls.scale_factor_width = scale_factor_width
        cls.scale_factor_height = scale_factor_height

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
