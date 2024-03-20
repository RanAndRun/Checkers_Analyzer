from Piece import Piece
from Tile import Tile
from King import King
from Pawn import Pawn
import copy


class MoveNode:
    def __init__(
        self,
        piece,
        from_tile: tuple[int, int],
        to_tile: tuple[int, int],
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
        if self.children:
            move_details += f", children: {len(self.children)}"
        return move_details

    def __deepcopy__(self, memo):
        # Deep copy each component
        new_piece = copy.deepcopy(self.piece, memo)
        new_from_tile = self.from_tile
        new_to_tile = self.to_tile
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MoveNode):
            return False

        # Compare simple attributes
        if not (
            self.piece.tile == other.piece.tile
            and self.from_tile == other.from_tile
            and self.to_tile == other.to_tile
            and self.promoted == other.promoted
        ):
            return False

        # Compare killed pieces
        if (self.killed is None) != (
            other.killed is None
        ):  # One is None, the other isn't
            return False
        if self.killed and not self.killed.tile == other.killed.tile:
            return False

        return True

    # Getters
    def get_piece(self):
        return self.piece

    def get_from_tile(self):
        return self.from_tile

    def get_to_tile(self):
        return self.to_tile

    def get_killed(self):
        return self.killed

    def get_promoted(self):
        return self.promoted

    def get_children(self):
        return self.children

    def get_parent(self):
        return self.parent

    # Setters
    def set_piece(self, piece):
        self.piece = piece

    def set_from_tile(self, from_tile):
        self.from_tile = from_tile

    def set_to_tile(self, to_tile):
        self.to_tile = to_tile

    def set_killed(self, killed):
        self.killed = killed

    def set_promoted(self, promoted):
        self.promoted = promoted

    def set_children(self, children):
        self.children = children

    def set_parent(self, parent):
        self.parent = parent
