from Board import Board
from MoveNode import MoveNode
from Enums import EColor
from time import sleep
import copy
from BoardNode import BoardNode
from concurrent.futures import ThreadPoolExecutor, as_completed


class CheckersAI:
    def __init__(self, board, depth=3):
        self.board = board
        self.depth = depth

    def evaluate_board(self, board):
        score_tuple = board.evaluate_board_score()
        weights = [5, 7.75, 4, 2.5, 0.5, -3, 3]
        score = sum([weight * score_tuple[i] for i, weight in enumerate(weights)])
        return score

    def minimax(self, node, depth, alpha, beta, maximizingPlayer):
        if depth == 0 or node.board.is_game_over():
            return self.evaluate_board(node.board)

        if maximizingPlayer:
            maxEval = float("-inf")
            for child in node.get_children(has_jumped=None):
                eval = self.minimax(child, depth - 1, alpha, beta, False)
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cut-off
            return maxEval
        else:
            minEval = float("inf")
            for child in node.get_children(has_jumped=None):
                eval = self.minimax(child, depth - 1, alpha, beta, True)
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cut-off
            return minEval

    def find_best_move(self, has_jumped=None):
        og_board = self.board
        root_node = BoardNode(og_board)
        best_value = float("-inf")
        best_move = None
        futures = []

        with ThreadPoolExecutor() as executor:
            for child in root_node.get_children(has_jumped):
                future = executor.submit(
                    self.minimax,
                    child,
                    self.depth,
                    float("-inf"),
                    float("inf"),
                    True if og_board.current_player == EColor.white else False,
                )
                futures.append((future, child.move))

            for future, move in futures:
                value = future.result()
                if value > best_value:
                    best_value = value
                    best_move = move

        print("best move", best_move)
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
