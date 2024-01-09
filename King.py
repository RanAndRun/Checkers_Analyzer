from Piece import *
from Enums import *
from Tile import *
import os


class King(Piece):
    white_king_img = os.path.join("assets", "redKing.png")
    black_king_img = os.path.join("assets", "blackKing.png")

    def __init__(self, tile: Tile, color: EColor):
        super().__init__(tile, color, self.white_king_img, self.black_king_img)
