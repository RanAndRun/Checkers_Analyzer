from Piece import *
from Enums import *
from Tile import *
import os


class King(Piece):
    white_king_img = os.path.join("assets", "redKing.png")
    black_king_img = os.path.join("assets", "blackKing.png")

    def __init__(self, tile: Tile, color: EColor):
        super().__init__(tile, color, self.white_king_img, self.black_king_img)

    def __deepcopy__(self, memo):
        # Call the deepcopy method of the superclass (Piece)
        return super().__deepcopy__(memo)