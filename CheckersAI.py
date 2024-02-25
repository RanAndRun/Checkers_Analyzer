from Board import Board
from MoveNode import MoveNode
from Enums import EColor
from time import sleep
import copy
from BoardNode import BoardNode


class CheckersAI:
    def __init__(self, board, depth=2):
        self.board = board
        self.depth = depth

    def evaluate_board(self, board):
        score_tuple = board.evaluate_board_score()
        weights = [5, 7.75, 4, 2.5, 0.5, -3, 3]
        score = sum([weight * score_tuple[i] for i, weight in enumerate(weights)])
        return score

    def minimax(self, node, depth, maximizingPlayer):
        if depth == 0 or node.board.is_game_over():
            return self.evaluate_board(node.board)

        if maximizingPlayer:
            maxEval = float("-inf")
            for child in node.get_children(has_jumped=None):
                eval = self.minimax(child, depth - 1, False)
                maxEval = max(maxEval, eval)
            return maxEval
        else:
            minEval = float("inf")
            for child in node.get_children(has_jumped=None):
                eval = self.minimax(child, depth - 1, True)
                minEval = min(minEval, eval)
            return minEval

    def find_best_move(self, has_jumped=None):
        og_board = self.board
        root_node = BoardNode(og_board)
        best_value = float("-inf")
        best_move = None

        for child in root_node.get_children(has_jumped):
            value = self.minimax(
                child,
                self.depth,
                True if root_node.board.current_player == EColor.white else False,
            )
            if value > best_value:
                best_value = value
                best_move = child.move

        # Apply best_move to the actual game board
        print("best move", best_move)

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
