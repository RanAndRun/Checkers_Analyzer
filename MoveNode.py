from Piece import Piece
from Tile import Tile


class MoveNode:
    def __init__(
        self,
        piece,
        from_tile,
        to_tile,
        killed=None,
        promoted=False,
        children=None,
        parent=None,
    ):
        self.piece = piece
        self.from_tile = from_tile
        self.to_tile = to_tile
        self.killed = killed
        self.promoted = promoted  # Flag to track if the move involved a promotion
        self.children = children if children is not None else []
        self.parent = parent

    def add_child(self, child):
        child.parent = self
        self.children.append(child)
