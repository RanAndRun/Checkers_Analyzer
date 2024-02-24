import copy
from Board import Board
from config import board_size
from Enums import EColor


class BoardNode:
    def __init__(self, board: Board, move=None, parent=None):
        self.board = board
        self.move = move
        self.parent = parent
        self.value = None

    def get_children(self, has_jumped=None):
        print("Original board before deepcopy:")
        print(self.board)

        current_board = copy.deepcopy(self.board)

        print("Original board after deepcopy:")
        print(self.board)
        print("Deep copied board:")
        print(current_board)

        children_states = []
        color = current_board.current_player
        moves = current_board.every_move_for_player(color, has_jumped)
        print(moves)
        for move in moves:
            new_board = copy.deepcopy(
                self.board
            )  # Create a new deep copy for each iteration

            print("new board copy of current \n")
            print(new_board)
            new_board.apply_move(move)

            print("New board after move:")
            print(new_board)
            print("Original board after applying move on new board:")
            print(self.board)  # Replace 'current_board' with 'self.board'

            children_states.append(BoardNode(new_board, move, self))

        return children_states

    def __repr__(self):
        board_representation = ""

        for y in reversed(range(board_size)):
            for x in range(board_size):
                tile = self.board.tiles[y][x]
                piece = self.board.get_pawn_from_tile.get(tile)
                if piece:
                    if piece.color == EColor.white:
                        board_representation += "W "
                    elif piece.color == EColor.black:
                        board_representation += "B "
                else:
                    board_representation += ". "
            board_representation += "\n"
        return board_representation


# TODO watch mandetory jump
