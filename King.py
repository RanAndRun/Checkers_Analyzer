from Piece import *
from Enums import *
from Tile import *
import os
import copy


class King(Piece):

    def __init__(self, tile: Tile, color: Eplayers):
        self.white_king_img = os.path.join("assets", "redKing.png")
        self.black_king_img = os.path.join("assets", "blackKing.png")
        super().__init__(tile, color, self.white_king_img, self.black_king_img)

    def __deepcopy__(self, memo):
        # Create a new Pawn instance with copied tile and same color
        new_tile = copy.deepcopy(self.tile, memo)
        new_king = King(new_tile, self.color)
        new_king.alive = self.alive
        return new_king
