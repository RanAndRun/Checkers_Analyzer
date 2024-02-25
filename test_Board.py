import unittest
from unittest.mock import patch
from Board import Board, MoveNode, Pawn

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    @patch('builtins.print')
    def test_execute_move(self, mock_print):
        # Create a MoveNode object
        move_node = MoveNode(piece=Pawn(), from_tile=(0, 0), to_tile=(1, 1), killed=None, promoted=False)

        # Call the _execute_move method
        self.board._execute_move(move_node)

        # Assert that the print function was called with the expected arguments
        mock_print.assert_called_with(move_node.piece)

        # Assert that all the move_node properties are printed
        mock_print.assert_any_call(move_node.piece)
        mock_print.assert_any_call(move_node.from_tile)
        mock_print.assert_any_call(move_node.to_tile)
        mock_print.assert_any_call(move_node.killed)
        mock_print.assert_any_call(move_node.promoted)

if __name__ == '__main__':
    unittest.main()