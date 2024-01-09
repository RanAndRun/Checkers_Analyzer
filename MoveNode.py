class MoveNode:

    def __init__(self, from_tile, to_tile, killed, next_jump=None):
        self.from_tile = from_tile
        self.to_tile = to_tile
        self.killed = killed
        self.next_jump = next_jump
