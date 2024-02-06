from Piece import Piece
from Tile import Tile


class MoveNode:
    def __init__(
        self, piece: Piece, to_tile: Tile, killed: Piece = None, children: list = None
    ):
        self.piece = piece
        self.to_tile = to_tile
        self.killed = killed
        self.children = children

    def add_child(self, child):
        self.children.append(child)
