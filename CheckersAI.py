from Board import Board
from MoveNode import MoveNode
from Enums import Eplayers
from time import sleep
import copy
from BoardNode import BoardNode
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import DEPTH


class CheckersAI:
    def __init__(self, board, depth=DEPTH):
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

    def find_best_move(self, board):

        is_max = board.current_player == Eplayers.white
        root_node = BoardNode(board)
        best_value = float("-inf") if is_max else float("inf")
        best_move = None
        futures = []

        with ThreadPoolExecutor() as executor:
            children = root_node.get_children()
            for child in children:
                future = executor.submit(
                    self.minimax,
                    child,
                    DEPTH - 1,
                    float("-inf"),
                    float("inf"),
                    not is_max,  # The next player is the opposite of the current player
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
        copy_of_board = copy.deepcopy(board)
        secend_copy_of_board = copy.deepcopy(board)

        # Temporarily apply the played move
        color_of_player = played_move.piece.color
        is_max = color_of_player == Eplayers.white
        # If the played move is white, the next move is black, and vice versa
        copy_of_board.apply_move(played_move)

        # Create a BoardNode for the current board state after the move

        board_after_move = BoardNode(copy_of_board)

        only_one_move = False
        if len(board.every_move_for_player(color_of_player)) == 1:
            only_one_move = True
            print("only one move")

        with ThreadPoolExecutor() as executor:
            played_move_score = executor.submit(
                self.minimax,
                board_after_move,
                self.depth - 1,
                float("-inf"),
                float("inf"),
                not is_max,
            )
            played_move_score = played_move_score.result()

        if only_one_move:
            best_move = played_move
            best_move_score = played_move_score
        else:
            best_move, best_move_score = self.find_best_move(secend_copy_of_board)

        return played_move_score, best_move_score, best_move

    def analyze_game(self, history, color):
        analysis_results = []
        prev_score = 0
        sum_of_played_move_scores = 0

        length = len(history)
        index = 0
        # Iterate over each move and corresponding board state
        for move, board in history:
            print("move", index, "of", length)
            index += 1
            move.piece = board.get_piece_at_tile(move.from_tile)
            if move.killed is not None:
                move.killed = board.get_piece_at_tile(move.killed.tile)

            # Skip if the move's piece color doesn't match the specified color
            if move.piece.color != color:
                continue

            # Perform evaluation and comparison for the move
            played_move_score, best_value, best_move = self.evaluate_and_compare_move(
                move, board
            )

            sum_of_played_move_scores += played_move_score - prev_score
            prev_score = played_move_score
            # Append the results to the analysis_results list

            analysis_results.append((move, played_move_score, best_value, best_move))

        # Calculate the average score of the played moves
        average_played_move_score = sum_of_played_move_scores / len(history)
        print("results", analysis_results)
        return analysis_results, average_played_move_score
