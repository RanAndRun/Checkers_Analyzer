from Board import Board
class CheckersAI:
    def __init__(self, board, depth=3):
        self.board = board
        self.depth = depth

    def evaluate_board(self):
        score_tuple = self.board.evaluate_board_score()
        weights = [5, 7.75, 4, 2.5, 0.5, -3, 3]
        score = sum([weight * score_tuple[i] for i, weight in enumerate(weights)])
        return score

    def minimax(self, depth, is_maximizing_player, alpha, beta):
        if depth == 0 or self.board.is_game_over():
            return self.evaluate_board()

        if is_maximizing_player:
            max_eval = -float('inf')
            for move in self.board.every_move_for_player(self.board.current_player):
                self.board.apply_move(move)  # Temporarily make the move
                eval = self.minimax(depth - 1, False, alpha, beta)
                self.board.undo_move(move)  # Undo the move
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.board.every_move_for_player(self.board.opponent_player()):
                self.board.apply_move(move)  # Temporarily make the move
                eval = self.minimax(depth - 1, True, alpha, beta)
                self.board.undo_move(move)  # Undo the move
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def find_best_move(self):
        best_move = None
        best_value = -float('inf')
        alpha = -float('inf')
        beta = float('inf')

        for move in self.board.every_move_for_player(self.board.current_player):
            self.board.apply_move(move)  # Temporarily make the move
            move_value = self.minimax(self.depth - 1, False, alpha, beta)
            self.board.undo_move(move)  # Undo the move

            if move_value > best_value:
                best_value = move_value
                best_move = move

        return best_move
