import pygame
import copy
from Tile import Tile
from Pawn import Pawn
from Enums import EColor
from config import window_width, window_height, board_size
from os import path

from King import King
from Piece import Piece
from MoveNode import MoveNode


class Board:

    tile_width, tile_height = window_width // board_size, window_height // board_size
    board_image = pygame.image.load(path.join("assets", "8x8_checkered_board.png"))

    pieces_list = [[], []]
    get_pawn_from_tile = {}
    tiles = []
    move_history = []

    # Board Initialization and Setup

    def __init__(self, screen):
        # start game board
        screen.blit(self.board_image, (0, 0))
        self.tiles = self.create_tiles()
        self.starting_position()
        self.move_history = []
        self.current_player = EColor.white

    def create_tiles(self):
        tiles = [[None for x in range(board_size)] for y in range(board_size)]

        x_point = 0
        y_point = window_height - self.tile_height

        for y in range(board_size):
            for x in range(board_size):
                tiles[y][x] = Tile(x, y, x_point, y_point)
                x_point = x_point + self.tile_width
            x_point = 0
            y_point = y_point - self.tile_height

        return tiles

    def starting_position(self):
        self.get_pawn_from_tile = {}
        for row in self.tiles:
            for tile in row:
                self.get_pawn_from_tile[tile] = None

        for row in range(3):
            mod = row % 2
            for column in range(0 + mod, board_size - 1 + mod, 2):
                curr = Pawn(self.tiles[row][column], color=EColor.white)
                self.get_pawn_from_tile[self.tiles[row][column]] = curr
                self.pieces_list[0].append(curr)

        for row in range(7, 4, -1):
            mod = row % 2
            for column in range(0 + mod, board_size - 1 + mod, 2):
                curr = Pawn(self.tiles[row][column], color=EColor.black)
                self.get_pawn_from_tile[self.tiles[row][column]] = curr
                self.pieces_list[1].append(curr)

    def __deepcopy__(self, memo):
        new_board = self.__class__.__new__(self.__class__)
        memo[id(self)] = new_board

        # Deep copy attributes
        new_board.tiles = [
            [copy.deepcopy(self.tiles[y][x], memo) for x in range(board_size)]
            for y in range(board_size)
        ]
        new_board.pieces_list = [
            [copy.deepcopy(piece, memo) for piece in player_pieces]
            for player_pieces in self.pieces_list
        ]

        # Rebuild the get_pawn_from_tile dictionary
        new_board.get_pawn_from_tile = {
            tile: None for row in new_board.tiles for tile in row
        }
        for player_pieces in new_board.pieces_list:
            for piece in player_pieces:
                new_board.get_pawn_from_tile[piece.tile] = piece

        # Deep copy other attributes as needed
        new_board.move_history = copy.deepcopy(self.move_history, memo)
        new_board.current_player = self.current_player
        # Copy other necessary attributes...

        return new_board

    # Drawing and Display

    def draw(self, screen):
        screen.blit(self.board_image, (0, 0))
        for tile_x in range(board_size):
            for tile_y in range(board_size):
                curr_tile = self.get_tile_from_location(tile_x, tile_y)
                pawn = self.get_pawn_from_tile[curr_tile]
                if pawn and pawn.is_alive():
                    self.get_pawn_from_tile[curr_tile].draw(screen)

    def show_avilable_moves(self, from_tile: Tile, has_jumped: Piece, screen):
        possible_moves, possible_jumps = self.every_move_possible_for_piece(
            self.get_pawn_from_tile[from_tile], has_jumped
        )
        possible_tiles = possible_jumps if possible_jumps else possible_moves
        for currTuple in possible_tiles:
            tile = currTuple.to_tile
            tile.glow_yellow(screen)

    def get_tile_at_pixel(self, mouse_x, mouse_y):
        for x_tile in range(board_size):
            for y_tile in range(board_size):
                currTile = self.get_tile_from_location(x_tile, y_tile)
                if currTile.tile_rect.collidepoint(mouse_x, mouse_y):
                    return currTile
        return None

    # Movement and Game Mechanics

    def where_can_move(self, tile: Tile) -> list[(Tile, bool)]:

        piece = self.get_pawn_from_tile[tile]
        x, y = tile.get_location()
        possible_tiles = []

        is_tile_not_taken = (
            lambda x, y: self.is_location_inside_board(x, y)
            and self.get_pawn_from_tile[self.tiles[y][x]] is None
        )
        is_opponent_pawn_on_tile = lambda x, y, color: self.get_pawn_from_tile[
            self.tiles[y][x]
        ] and self.get_pawn_from_tile[self.tiles[y][x]].color == EColor(
            3 - piece.color.value
        )
        if type(piece) == Pawn and piece.alive:
            directions = (
                [(1, 1), (-1, 1)],
                [(1, -1), (-1, -1)],
            )  # White, Black, Right, Left
            directions = directions[piece.color.value - 1]

            for direction in directions:
                dx, dy = direction
                found = False
                new_x, new_y = x + dx, y + dy
                if not self.is_location_inside_board(new_x, new_y):
                    continue
                if is_tile_not_taken(new_x, new_y):
                    possible_tiles.append(
                        MoveNode(piece, piece.tile, self.tiles[new_y][new_x])
                    )

        if type(piece) == King and piece.alive:
            directions = [
                (1, 1),
                (-1, 1),
                (1, -1),
                (-1, -1),
            ]  # Up-right, Up-left, Down-right, Down-left

            for direction in directions:
                dx, dy = direction

                for step in range(1, board_size):
                    new_x, new_y = x + step * dx, y + step * dy

                    if is_tile_not_taken(new_x, new_y):
                        possible_tiles.append(
                            MoveNode(piece, piece.tile, self.tiles[new_y][new_x])
                        )
                    else:
                        break

        return possible_tiles

    def where_can_jump(self, tile: Tile):
        piece = self.get_pawn_from_tile[tile]
        x, y = tile.get_location()
        possible_jumps = []

        # might be able to delete IsLocationInsideBoard from isTileNotTaken
        is_tile_not_taken = (
            lambda x, y: self.is_location_inside_board(x, y)
            and self.get_pawn_from_tile[self.tiles[y][x]] is None
        )
        is_tile_taken = (
            lambda x, y: self.is_location_inside_board(x, y)
            and self.get_pawn_from_tile[self.tiles[y][x]] is not None
        )
        is_opponent_pawn_on_tile = lambda x, y, color: self.get_pawn_from_tile[
            self.tiles[y][x]
        ] and self.get_pawn_from_tile[self.tiles[y][x]].color == EColor(
            3 - piece.color.value
        )

        if type(piece) == Pawn and piece.alive:
            directions = (
                [(1, 1), (-1, 1)],
                [(1, -1), (-1, -1)],
            )  # White, Black, Right, Left
            directions = directions[piece.color.value - 1]

            for direction in directions:
                dx, dy = direction

                new_x, new_y = x + dx, y + dy

                if is_tile_taken(new_x, new_y) and is_opponent_pawn_on_tile(
                    new_x, new_y, piece.color
                ):
                    # found is here to tell that player must eat now. can be eliminated, if possible_jumps not None, must jump.
                    if is_tile_not_taken(new_x + dx, new_y + dy):
                        possible_jumps.append(
                            MoveNode(
                                piece,
                                piece.tile,
                                self.tiles[new_y + dy][new_x + dx],
                                self.get_pawn_from_tile[self.tiles[new_y][new_x]],
                            )
                        )

        if type(piece) == King and piece.alive:
            directions = [
                (1, 1),
                (-1, 1),
                (1, -1),
                (-1, -1),
            ]  # Up-right, Up-left, Down-right, Down-left

            for direction in directions:
                dx, dy = direction
                found = None
                for step in range(1, board_size):
                    new_x, new_y = x + step * dx, y + step * dy

                    if (
                        is_tile_taken(new_x, new_y)
                        and is_opponent_pawn_on_tile(new_x, new_y, piece.color)
                        or found
                        and is_tile_not_taken(new_x, new_y)
                    ):
                        if not found:
                            found = self.get_pawn_from_tile[self.tiles[new_y][new_x]]
                        if is_tile_not_taken(new_x + dx, new_y + dy):
                            possible_jumps.append(
                                MoveNode(
                                    piece,
                                    piece.tile,
                                    self.tiles[new_y + dy][new_x + dx],
                                    found,
                                )
                            )
                        else:
                            break

        return possible_jumps

    def every_move_possible_for_piece(self, piece: Piece, hasJumped: Piece = None):
        # Get both possible moves and jumps for the piece
        possible_moves = self.where_can_move(piece.tile)
        possible_jumps = self.where_can_jump(piece.tile)

        # Check if a jump is possible for any piece of the same color
        jump_is_possible = self.jump_is_possible(piece.color)

        # If the piece has just jumped, only consider further jumps for it
        if hasJumped is piece:
            return [], possible_jumps

        # If another piece has jumped, no moves should be returned for this piece
        if hasJumped and hasJumped is not piece:
            return [], []

        # If a jump is possible for any piece of the same color, don't consider regular moves
        if jump_is_possible:
            return [], possible_jumps

        # If no piece has jumped and no jump is possible, return all possible moves
        return possible_moves, possible_jumps

    def every_move_for_player(
        self, color: EColor, hasJumped: Piece = None, depth=0, max_depth=3
    ):
        if depth > max_depth:
            return []  # Stop recursion if max depth is exceeded

        jump_moves = []
        found_jump = False

        # First, check all pieces for jump moves
        for piece in self.pieces_list[color.value - 1]:
            if piece.is_alive():
                jump_options = self.where_can_jump(piece.tile)
                if jump_options:
                    found_jump = True
                    for jump_move in jump_options:
                        new_node = MoveNode(
                            piece, piece.tile, jump_move.to_tile, jump_move.killed
                        )
                        # Recursively find further jumps from the new position
                        new_node.children = self.every_move_for_player(
                            color, piece, depth + 1, max_depth
                        )
                        jump_moves.append(new_node)

        # If no jumps are found, and no jump has been made yet, consider regular moves for all pieces
        if not found_jump and not hasJumped:
            regular_moves = []
            for piece in self.pieces_list[color.value - 1]:
                if piece.is_alive():
                    regular_options, _ = self.every_move_possible_for_piece(
                        piece, hasJumped
                    )
                    for move in regular_options:
                        new_node = MoveNode(
                            piece, piece.tile, move.to_tile, move.killed
                        )
                        regular_moves.append(new_node)
            return regular_moves

        return jump_moves

    def move(self, from_tile: Tile, to_tile: Tile, hasJumped: bool, screen):
        piece = self.get_pawn_from_tile[from_tile]
        regular_moves, jump_moves = self.every_move_possible_for_piece(piece, hasJumped)
        possible_moves = jump_moves if jump_moves else regular_moves

        hasJumped = None
        was_promoted = False

        for possible_move in possible_moves:
            if possible_move.to_tile == to_tile:

                if piece:
                    piece.move(to_tile)
                    self.get_pawn_from_tile[to_tile] = piece
                    self.get_pawn_from_tile[from_tile] = None
                    self.get_pawn_from_tile[to_tile].draw(screen)

                    if possible_move.killed and possible_move.killed.tile:
                        hasJumped = piece
                        self.get_pawn_from_tile[possible_move.killed.tile] = None
                        possible_move.killed.killed()
                        self.pieces_list[possible_move.killed.color.value - 1].remove(
                            possible_move.killed
                        )

                    if isinstance(piece, Pawn):
                        if (
                            piece.color == EColor.white
                            and to_tile.row == board_size - 1
                        ) or (piece.color == EColor.black and to_tile.row == 0):
                            was_promoted = True
                            self.upgrade_to_king(to_tile)
                            print("PROMOPTEDDD")
                            piece = self.get_pawn_from_tile[
                                to_tile
                            ]  # Update piece to the new King
                            hasJumped = None
        if not hasJumped or (
            self.every_move_possible_for_piece(piece, hasJumped) == ([], [])
        ):
            self.switch_player()
        move = MoveNode(
            piece, from_tile, to_tile, possible_move.killed, promoted=was_promoted
        )

        return move, hasJumped

    def apply_move(self, move_node: MoveNode):
        # Update all the parameters of the move_node with their corresponding objects on the board
        x, y = move_node.piece.tile.get_location()
        move_node.piece = self.get_pawn_from_tile[self.tiles[y][x]]

        x, y = move_node.from_tile.get_location()
        move_node.from_tile = self.tiles[y][x]

        x, y = move_node.to_tile.get_location()
        move_node.to_tile = self.tiles[y][x]

        if move_node.killed:
            x, y = move_node.killed.tile.get_location()
            move_node.killed = self.get_pawn_from_tile[self.tiles[y][x]]
        # Apply the initial move
        self._execute_move(move_node)
        self.switch_player()
        # Apply subsequent moves in the multi-jump sequence
        current_move = move_node
        while current_move.children:
            # Assuming each node has at most one child in a multi-jump sequence
            current_move = current_move.children[0]
            # Update all the parameters of the current_move with their corresponding objects on the board
            x, y = current_move.piece.tile.get_location()
            current_move.piece = self.get_pawn_from_tile[self.tiles[y][x]]

            x, y = current_move.from_tile.get_location()
            current_move.from_tile = self.tiles[y][x]

            x, y = current_move.to_tile.get_location()
            current_move.to_tile = self.tiles[y][x]

            if current_move.killed:
                x, y = current_move.killed.tile.get_location()
                current_move.killed = self.get_pawn_from_tile[self.tiles[y][x]]
            self._execute_move(current_move)

    def _execute_move(self, move_node: MoveNode):
        # Retrieve the piece to be moved
        piece = move_node.piece
        from_tile = move_node.from_tile
        to_tile = move_node.to_tile
        killed_piece = move_node.killed

        # Move the piece to the new tile
        self.get_pawn_from_tile[to_tile] = piece
        self.get_pawn_from_tile[from_tile] = None
        piece.move(to_tile)  # Update the piece's tile attribute

        # Handle any capture
        if killed_piece:
            print("killed piece", killed_piece)
            killed_piece_tile = killed_piece.tile
            self.get_pawn_from_tile[killed_piece_tile] = None
            killed_piece.killed()  # Mark the killed piece as not alive
            self.pieces_list[killed_piece.color.value - 1].remove(killed_piece)

        # Handle promotion to King if necessary
        if isinstance(piece, Pawn) and move_node.promoted:
            self.upgrade_to_king(to_tile)

    # Undo Mechanics

    def undo_move(self):
        if not self.move_history:
            return  # No move to undo

        self.switch_player()
        last_move_sequence = self.move_history.pop()

        # Create a stack to store the moves in reverse order
        reverse_move_stack = self.build_reverse_stack(last_move_sequence)

        # Now undo the moves in reverse order
        while reverse_move_stack:
            move_to_undo = reverse_move_stack.pop()
            self.undo_single_move(move_to_undo)

    def build_reverse_stack(self, move_node):
        reverse_move_stack = []
        current_move = move_node
        while current_move:
            reverse_move_stack.append(current_move)
            # Add all child moves to the stack in reverse order
            reverse_move_stack.extend(reversed(current_move.children))
            current_move = current_move.parent
        return reverse_move_stack

    def undo_single_move(self, move_node):
        # Undo logic for a single move
        if move_node.to_tile and self.get_pawn_from_tile[move_node.to_tile]:
            moved_piece = self.get_pawn_from_tile[move_node.to_tile]
            self.get_pawn_from_tile[move_node.from_tile] = moved_piece
            self.get_pawn_from_tile[move_node.to_tile] = None
            moved_piece.tile = move_node.from_tile
        else:
            print(f"No piece found at {move_node.to_tile} to move back")

        # Restore the captured piece, if any
        if move_node.killed:
            captured_piece = move_node.killed
            self.get_pawn_from_tile[captured_piece.tile] = captured_piece
            captured_piece.alive = True
            self.pieces_list[captured_piece.color.value - 1].append(captured_piece)
        if move_node.promoted is True:
            self.demote_king_to_pawn(move_node.piece, move_node.from_tile)

    # Game State and Rules

    def is_tile_taken(self, x, y):
        return (
            self.is_location_inside_board(x, y)
            and self.get_pawn_from_tile[self.tiles[y][x]] is not None
        )

    def jump_is_possible(self, color: EColor) -> bool:
        for piece in self.pieces_list[color.value - 1]:
            if self.where_can_jump(piece.tile) != []:
                return True
        return False

    def has_more_jumps(self, tile):
        return self.where_can_jump(tile) != []

    def is_player_out_of_moves(self, player_color):
        """
        Check if a player has no legal moves left.
        """
        for piece in self.pieces_list[player_color.value - 1]:
            if piece.is_alive() and self.every_move_possible_for_piece(piece):
                return False  # Found a piece with a legal move
        return True  # No legal moves found

    def is_player_out_of_pieces(self, player_color):
        """
        Check if a player has no pieces left.
        """
        return all(
            not piece.is_alive() for piece in self.pieces_list[player_color.value - 1]
        )

    def is_game_over(self):
        """
        Check if the game is over and return the game status.
        Returns:
            - 'white' if White wins.
            - 'black' if Black wins.
            - 'draw' if the game is a draw.
            - None if the game is not over.
        """
        white_out_of_moves = self.is_player_out_of_moves(EColor.white)
        black_out_of_moves = self.is_player_out_of_moves(EColor.black)
        white_out_of_pieces = self.is_player_out_of_pieces(EColor.white)
        black_out_of_pieces = self.is_player_out_of_pieces(EColor.black)

        if white_out_of_pieces and black_out_of_pieces:
            return "draw"  # Both players have no pieces left
        elif white_out_of_pieces or white_out_of_moves:
            return "black"  # Black wins
        elif black_out_of_pieces or black_out_of_moves:
            return "white"  # White wins
        else:
            return None  # Game is not over

    # Piece Management

    def upgrade_to_king(self, tile: Tile):
        piece = self.get_pawn_from_tile[tile]
        if piece is King:
            return

        if piece.color == EColor.white and tile.row != board_size - 1:
            return
        if piece.color == EColor.black and tile.row != 0:
            return

        king = King(tile, piece.color)
        self.get_pawn_from_tile[tile] = king
        self.pieces_list[piece.color.value - 1].remove(piece)
        self.pieces_list[piece.color.value - 1].append(king)
        self.switch_player()
        piece.alive = False

    def demote_king_to_pawn(self, king, original_tile):
        if isinstance(king, King):
            pawn = Pawn(original_tile, king.color)  # Recreate the pawn
            self.get_pawn_from_tile[original_tile] = pawn
            self.pieces_list[king.color.value - 1].remove(king)
            self.pieces_list[pawn.color.value - 1].append(pawn)

    def piece_can_be_taken(self, piece):
        # Check if any opponent can jump over the piece
        for opponent_piece in self.pieces_list[2 - piece.color.value]:
            jumps = self.where_can_jump(opponent_piece.tile)
            for jump in jumps:
                if jump.killed == piece:
                    return True
        return False

    def is_piece_protected(self, piece):
        # A piece is considered protected if it can't be eaten if not moved / pieces behind it moves.
        x, y = piece.tile.column, piece.tile.row

        if piece.color == EColor.white:
            behind_moves = [
                (-1, -1),
                (1, -1),
            ]  # Moves to check pieces behind a white piece
        else:
            behind_moves = [
                (-1, 1),
                (1, 1),
            ]  # Moves to check pieces behind a black piece

        for move in behind_moves:
            dx, dy = move
            behind_x, behind_y = x + dx, y + dy

            if not self.is_tile_taken(behind_x, behind_y):
                return False

        return True

    # Utilities

    def get_tile_from_location(self, x, y) -> Tile:
        return self.tiles[y][x]

    def is_location_inside_board(self, x, y):
        return 0 <= x < len(self.tiles) and 0 <= y < len(self.tiles[0])

    def evaluate_board_score(self):
        # Scoring categories

        #  Index 0: Number of pawns
        #  Index 1: Number of kings
        #  Index 2: Number in back row
        #  Index 3: Number in middle box
        #  Index 4: Number in middle 2 rows, not box
        #  Index 5: Number that can be taken this turn
        #  Index 6: Number that are protected

        p1_nums = [0] * 7  # Player 1 scores
        p2_nums = [0] * 7  # Player 2 scores

        for tile_row in self.tiles:
            for tile in tile_row:
                piece = self.get_pawn_from_tile[tile]
                if piece is not None:
                    color = piece.color
                    r = piece.tile.row
                    c = piece.tile.column

                    # Check for pawns and kings
                    if isinstance(piece, Pawn):
                        if color == EColor.white:
                            p1_nums[0] += 1
                        else:
                            p2_nums[0] += 1
                    elif isinstance(piece, King):
                        if color == EColor.white:
                            p1_nums[1] += 1
                        else:
                            p2_nums[1] += 1

                    # Check for pieces in the back row
                    if (color == EColor.white and r == 0) or (
                        color == EColor.black and r == 7
                    ):
                        if color == EColor.white:
                            p1_nums[2] += 1
                        else:
                            p2_nums[2] += 1

                    # Check for middle rows
                    if r == 3 or r == 4:
                        if 2 <= c <= 5:
                            if color == EColor.white:
                                p1_nums[3] += 1
                            else:
                                p2_nums[3] += 1
                        else:
                            if color == EColor.white:
                                p1_nums[4] += 1
                            else:
                                p2_nums[4] += 1

                    # Check if can be taken this turn
                    if self.piece_can_be_taken(piece):
                        if color == EColor.white:
                            p1_nums[5] += 1
                        else:
                            p2_nums[5] += 1

                    # Check for protected pieces
                    if self.is_piece_protected(piece):
                        if color == EColor.white:
                            p1_nums[6] += 1
                        else:
                            p2_nums[6] += 1

        # Subtract Player 2's scores from Player 1's to get a single score array
        for i in range(len(p1_nums)):
            p1_nums[i] -= p2_nums[i]

        return p1_nums

    def switch_player(
        self,
    ):
        self.current_player = (
            EColor.black if self.current_player == EColor.white else EColor.white
        )

    def add_move_to_history(self, move: MoveNode):
        self.move_history.append(move)

    def get_move_history(self):
        return self.move_history

    def __repr__(self):
        board_representation = ""
        for y in reversed(range(board_size)):
            for x in range(board_size):
                tile = self.tiles[y][x]
                piece = self.get_pawn_from_tile.get(tile)
                if piece:
                    if piece.color == EColor.white:
                        board_representation += "W "
                    elif piece.color == EColor.black:
                        board_representation += "B "
                else:
                    board_representation += ". "
            board_representation += "\n"
        return board_representation
