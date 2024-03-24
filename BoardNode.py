import copy
from Board import Board
from Config import BOARD_SIZE
from Enums import Eplayers


class BoardNode:
    def __init__(self, board: Board, move=None, parent=None):
        self.board = board
        self.move = move
        self.parent = parent
        self.value = None

    def get_children(self):

        current_board = copy.deepcopy(self.board)
        children_states = []
        color = current_board.current_player
        moves = current_board.every_move_for_player(color)
        for move in moves:
            new_board = copy.deepcopy(
                self.board
            )  # Create a new deep copy for each iteration
            new_board.apply_move(move)

            children_states.append(BoardNode(new_board, move, self))
        return children_states

    def __repr__(self):
        board_representation = "\n"
        for y in reversed(range(BOARD_SIZE)):
            for x in range(BOARD_SIZE):
                piece = self.board.pieces_matrix[y][x]
                if piece:
                    if piece.color == Eplayers.white:
                        board_representation += "W "
                    elif piece.color == Eplayers.black:
                        board_representation += "B "
                else:
                    board_representation += ". "
            board_representation += "\n"
        return board_representation + "\n"
