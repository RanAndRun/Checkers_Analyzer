from Piece import *
from Enums import *
from Tile import *
import os
import copy


class King(Piece):
    white_king_img = os.path.join("assets", "redKing.png")
    black_king_img = os.path.join("assets", "blackKing.png")

    def __init__(self, tile: Tile, color: Eplayers):
        super().__init__(tile, color, self.white_king_img, self.black_king_img)

    # def __deepcopy__(self, memo):
    #     # Call the deepcopy method of the superclass (Piece)
    #     return super().__deepcopy__(memo)

    def __deepcopy__(self, memo):
        # Create a new Pawn instance with copied tile and same color
        new_tile = copy.deepcopy(self.tile, memo)
        new_king = King(new_tile, self.color)
        new_king.alive = self.alive
        return new_king
