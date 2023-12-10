from Board import Board


class Analyzer:
    def __init__(self, board: Board):
        self.board = board

    def every_move_for_player(self, color: EColor, hasJumped: bool):
        # moves_list = [(pawn, from_tile, to_tile), (), ()]
        moves_list = []
        for piece in self.board.pieces_list[color.value - 1]:
            for move in Board.every_move_possible(self.board, piece.tile, hasJumped):
                moves_list.append(piece, piece.tile, move[0], move[1])

        return moves_list
