from Piece import Piece
from Enums import EColor
from Tile import Tile
import os
import pygame
from Main import screen

class Pawn(Piece):
    white_pawn_img = os.path.join("assets", "red.png")
    black_pawn_img = os.path.join("assets", "black.png")

    def __init__(self, tile: Tile, color: EColor):
        super().__init__(tile, color, self.white_pawn_img, self.black_pawn_img)









