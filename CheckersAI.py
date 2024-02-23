from Board import Board
from MoveNode import MoveNode
from Enums import EColor
from time import sleep
import copy


class CheckersAI:
    def __init__(self, board, depth=4):
        self.board = board
        self.depth = depth

    def evaluate_board(self, board):
        score_tuple = board.evaluate_board_score()
        weights = [5, 7.75, 4, 2.5, 0.5, -3, 3]
        score = sum([weight * score_tuple[i] for i, weight in enumerate(weights)])
        return score

    def minimax(self, board, depth, maximizingPlayer):
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        if maximizingPlayer:
            maxEval = -float("inf")
            for move in board.every_move_for_player(board.current_player):
                new_board = copy.deepcopy(board)
                new_board.apply_move(move)
                print(new_board)
                sleep(2)
                eval = self.minimax(new_board, depth - 1, False)
                maxEval = max(maxEval, eval)
            return maxEval
        else:
            minEval = float("inf")
            for move in board.every_move_for_player(board.current_player):
                new_board = copy.deepcopy(board)
                new_board.apply_move(move)
                print(new_board)
                sleep(2)
                eval = self.minimax(new_board, depth - 1, True)
                minEval = min(minEval, eval)
            return minEval

    def find_best_move(self, color_of_player):
        best_move = None
        best_value = -float("inf")

        for move in self.board.every_move_for_player(color_of_player):
            new_board = copy.deepcopy(self.board)
            new_board.apply_move(move)
            move_value = self.minimax(new_board, self.depth - 1, False)
            if move_value > best_value:
                best_value = move_value
                best_move = move

        return best_move

    def evaluate_and_compare_move(self, played_move: MoveNode):
        # Temporarily apply the played move
        color_of_player = played_move.piece.color
        self.board.apply_move(played_move)
        played_move_score = self.minimax(self.depth, False, -float("inf"), float("inf"))
        self.board.undo_move()

        # Find and evaluate the best possible move
        best_move = self.find_best_move(color_of_player)
        if best_move:
            self.board.apply_move(best_move)
            best_move_score = self.minimax(
                self.depth, False, -float("inf"), float("inf")
            )
            self.board.undo_move()
        else:
            best_move_score = -float("inf")

        return played_move_score, best_move_score

    def analyze_game(self, moves_list):
        analysis_results = []
        for move in moves_list:
            score, best_score = self.evaluate_and_compare_move(move)
            analysis_results.append((move, score, best_score))
        return analysis_results
