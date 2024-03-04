from Piece import Piece
from Tile import Tile
import copy


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

    def __repr__(self):
        move_details = f"Move from {self.from_tile} to {self.to_tile}"
        if self.killed:
            move_details += f", capturing piece at {self.killed.tile}"
        if self.promoted:
            move_details += ", piece promoted"
        return move_details

    def __deepcopy__(self, memo):
        # Deep copy each component
        new_piece = copy.deepcopy(self.piece, memo)
        new_from_tile = this.
        new_to_tile = copy.deepcopy(self.to_tile, memo)
        new_killed = copy.deepcopy(self.killed, memo) if self.killed else None
        new_children = copy.deepcopy(self.children, memo) if self.children else []
        # Parent is usually not deep-copied to avoid circular references
        return MoveNode(
            new_piece,
            new_from_tile,
            new_to_tile,
            new_killed,
            self.promoted,
            new_children,
            self.parent,
        )
