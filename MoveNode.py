from Piece import Piece
from Tile import Tile


class MoveNode:
    def __init__(
        self,
        piece: Piece,
        from_tile: Tile,
        to_tile: Tile,
        killed: Piece = None,
        promoted: bool = False,
        children: list = None,
    ):
        self.piece = piece
        self.to_tile = to_tile
        self.from_tile = from_tile
        self.killed = killed
        self.promoted = promoted
        self.children = children

    def add_child(self, child):
        self.children.append(child)
