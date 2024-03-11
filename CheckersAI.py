from Board import Board
from MoveNode import MoveNode
from Enums import Eplayers
from time import sleep
import copy
from BoardNode import BoardNode
from concurrent.futures import ThreadPoolExecutor, as_completed


class CheckersAI:
    def __init__(self, board, depth=2):
        self.board = board
        self.depth = depth

    def evaluate_board(self, board):
        score_tuple = board.evaluate_board_score()

        # magic numbers approved by research
        weights = [5, 7.75, 4, 2.5, 0.5, -3, 3]

        score = sum([weight * score_tuple[i] for i, weight in enumerate(weights)])
        return score

    def minimax(self, node, depth, alpha, beta, maximizingPlayer):
        # input: BoardNode of the current board state, depth of the search tree, alpha, beta, and a boolean indicating if the current player is maximizing score or not
        # output: the score of the best move for the current player

        if depth == 0 or node.board.is_game_over():
            return self.evaluate_board(node.board)

        if maximizingPlayer:
            maxEval = float("-inf")
            children = node.get_children()
            for child in children:
                eval = self.minimax(child, depth - 1, alpha, beta, False)
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cut-off
            node.value = maxEval
            return maxEval
        else:
            minEval = float("inf")
            children = node.get_children()
            for child in children:
                eval = self.minimax(child, depth - 1, alpha, beta, True)
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cut-off
            node.value = minEval
            return minEval

    def find_best_move(self, board=None, depth=None, is_max=True):
        if board is None:
            board = self.board
        if depth is None:
            depth = self.depth

        root_node = BoardNode(board)
        best_value = float("-inf") if is_max else float("inf")
        best_move = None
        futures = []

        with ThreadPoolExecutor() as executor:
            children = root_node.get_children()
            for child in children:
                if len(children) == 1:
                    depth = 0
                future = executor.submit(
                    self.minimax,
                    child,
                    depth,
                    float("-inf"),
                    float("inf"),
                    not is_max,  # Swap maximizingPlayer if is_max is False
                )
                futures.append((future, child.move))

            for future, move in futures:
                value = future.result()
                if (is_max and value > best_value) or (
                    not is_max and value < best_value
                ):
                    best_value = value
                    best_move = move

        return best_move, best_value

    def evaluate_and_compare_move(self, played_move: MoveNode, board: Board):
        # Temporarily apply the played move
        color_of_player = played_move.piece.color
        is_max = (
            color_of_player == Eplayers.black
        )  # If the played move is white, the next move is black, and vice versa
        board.apply_move(played_move)

        # Create a BoardNode for the current board state after the move
        after_move_node = BoardNode(board)

        # Use minimax to evaluate the board state after the played move, looking 2 moves ahead
        played_move_score = self.minimax(
            after_move_node,
            self.depth - 1,
            -float("inf"),
            float("inf"),
            not is_max,
        )

        # Undo the move to restore the original board state
        board.undo_move()

        # Find and evaluate the best possible move from the original board state
        best_move, best_move_score = self.find_best_move(board=board)
        print("best move", best_move, best_move_score)
        if best_move:
            # Temporarily apply the best move
            board.apply_move(best_move)
            best_move_node = BoardNode(board)

            # Evaluate the score after the best move
            best_move_score = self.minimax(
                best_move_node, self.depth, -float("inf"), float("inf"), is_max
            )
            board.undo_move()
        else:
            best_move_score = -float("inf")

        return played_move_score, best_move_score, best_move

    def analyze_game(self, history, color):
        analysis_results = []

        # Iterate over each move and corresponding board state
        for move, board in history:

            move.piece = board.get_piece_at_tile(move.from_tile)
            if move.killed is not None:
                move.killed = board.get_piece_at_tile(move.killed.tile)
            print(move.piece, "move")
            # Skip if the move's piece color doesn't match the specified color
            if move.piece.color != color:
                print("history color not matching", move.piece.color, color)
                continue
            # Perform evaluation and comparison for the move
            played_move_score, best_value, best_move = self.compare_move(move, board)

            # Append the results to the analysis_results list

            analysis_results.append((move, played_move_score, best_value, best_move))
        print("results", analysis_results)
        return analysis_results

    def find_move_score(self, move, board):
        color_of_player = move.piece.color
        is_max = color_of_player == Eplayers.white
        board.apply_move(move)
        move_node = BoardNode(board)
        score = self.minimax(
            move_node, self.depth - 1, -float("inf"), float("inf"), is_max
        )
        board.undo_move()
        return score

    def compare_move(self, move, board):
        is_max = True if move.piece.color == Eplayers.white else False
        best_move, best_value = self.find_best_move(board=board, is_max=is_max)
        played_move_score = self.find_move_score(move, board)

        return played_move_score, best_value, best_move
