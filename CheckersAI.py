from Board import Board
from MoveNode import MoveNode
from Enums import Eplayers
from time import sleep
import copy
from BoardNode import BoardNode
from concurrent.futures import ThreadPoolExecutor
from Config import DEPTH


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

    def minimax(self, node, depth, alpha, beta, maximizingPlayer, moves_list=[]):
        if depth == 0 or node.board.is_game_over():
            return moves_list, self.evaluate_board(node.board)

        if maximizingPlayer:
            maxEval = float("-inf")
            best_sequence = None
            children = node.get_children()
            for child in children:
                sequence, eval = self.minimax(
                    child, depth - 1, alpha, beta, False, moves_list + [child.move]
                )
                if eval > maxEval:
                    maxEval = eval
                    best_sequence = sequence
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cut-off
            return best_sequence, maxEval
        else:
            minEval = float("inf")
            best_sequence = None
            children = node.get_children()
            for child in children:
                sequence, eval = self.minimax(
                    child, depth - 1, alpha, beta, True, moves_list + [child.move]
                )
                if eval < minEval:
                    minEval = eval
                    best_sequence = sequence
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cut-off
            return best_sequence, minEval

    def evaluate_and_compare_move(self, played_move: MoveNode, board: Board):
        # input: MoveNode of the played move and the current board state
        # output: the score of the played move, the score of the best move after the played move, and the best move after the played move

        # Create a copy of the board before and after the move

        copy_of_board_after_move = copy.deepcopy(board)
        copy_of_board_after_move.apply_move(played_move)

        # If the played move is white, the next move is black, and vice versa
        color_of_player = played_move.piece.color
        is_max = color_of_player == Eplayers.white

        # find the played move sequence
        board_node_after_move = BoardNode(copy_of_board_after_move)
        with ThreadPoolExecutor() as executor:
            played_move_score = executor.submit(
                self.minimax,
                board_node_after_move,
                self.depth - 1,
                float("-inf"),
                float("inf"),
                not is_max,
            )
            played_sequance, played_move_score = played_move_score.result()

        only_one_move = len(board.every_move_for_player(color_of_player)) == 1

        # if there is only one move, return the played move as the best move
        if only_one_move:
            best_sequence = [played_move]
            best_move_score = played_move_score
        else:
            # find the best move sequence
            copy_of_board_before_move = copy.deepcopy(board)
            root_node = BoardNode(copy_of_board_before_move)

            with ThreadPoolExecutor() as executor:
                best_move_score = executor.submit(
                    self.minimax,
                    root_node,
                    self.depth,
                    float("-inf"),
                    float("inf"),
                    is_max,
                )
                best_sequence, best_move_score = best_move_score.result()

        return (
            played_move_score,
            best_move_score,
            best_sequence,
            [played_move] + played_sequance,
        )

    def analyze_game(self, history, color):
        # input: the history of the game and the color of the player to analyze
        # output: the results of the analysis and the average score of the played moves
        analysis_results = []
        prev_score = 0
        sum_of_played_move_scores = 0

        length = len(history)
        index = 0
        # Iterate over each move and corresponding board state
        for move, board in history:
            print("move", index, "of", length)  # print the move that is being analyzed
            index += 1

            # Skip if the move's piece color doesn't match the specified color
            if move.piece.color != color:
                continue

            # Perform evaluation and comparison for the move
            played_move_score, best_value, best_sequence, played_sequance = (
                self.evaluate_and_compare_move(move, board)
            )

            sum_of_played_move_scores += played_move_score - prev_score
            prev_score = played_move_score
            # Append the results to the analysis_results list

            analysis_results.append(
                (move, played_move_score, best_value, best_sequence, played_sequance)
            )

        # Calculate the average score of the played moves
        if len(history) == 0:
            average_played_move_score = 0
        else:
            average_played_move_score = sum_of_played_move_scores / len(history)
            if color == Eplayers.white:
                average_played_move_score = -average_played_move_score

        print("results", analysis_results)
        return analysis_results, average_played_move_score
