from Piece import Piece
from Enums import EColor
from Tile import Tile
import os
import pygame
import copy


class Pawn(Piece):
    white_pawn_img = os.path.join("assets", "red.png")
    black_pawn_img = os.path.join("assets", "black.png")

    def __init__(self, tile: Tile, color: EColor):
        super().__init__(tile, color, self.white_pawn_img, self.black_pawn_img)
        # Store the image paths as attributes
        self.white_img_path = self.white_pawn_img
        self.black_img_path = self.black_pawn_img

    def __deepcopy__(self, memo):
        # Create a new Pawn instance with copied tile and same color
        new_tile = copy.deepcopy(self.tile, memo)
        new_pawn = Pawn(new_tile, self.color)
        new_pawn.alive = self.alive
        return new_pawn
