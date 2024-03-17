from Piece import Piece
from Enums import Eplayers
from Tile import Tile
import os
import pygame
import copy


class Pawn(Piece):

    def __init__(self, tile: Tile, color: Eplayers):
        self.white_pawn_img = os.path.join("assets", "red.png")
        self.black_pawn_img = os.path.join("assets", "black.png")
        super().__init__(tile, color, self.white_pawn_img, self.black_pawn_img)

    def __deepcopy__(self, memo):
        # Create a new Pawn instance with copied tile and same color
        new_tile = copy.deepcopy(self.tile, memo)
        new_pawn = Pawn(new_tile, self.color)
        new_pawn.alive = self.alive
        return new_pawn
