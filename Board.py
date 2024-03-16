import pygame
import copy
from Tile import Tile
from Pawn import Pawn
from Enums import Eplayers, Ecolors
from config import window_width, window_height, board_size
from os import path
from config import window_width, window_height

from King import King
from Piece import Piece
from MoveNode import MoveNode


class Board:

    tile_width, tile_height = window_width // board_size, window_height // board_size
    board_image = pygame.image.load(path.join("assets", "8x8_checkered_board.png"))
    size = (window_width, window_height)
    board_image = pygame.transform.scale(board_image, size)

    pieces_list = [[], []]
    get_pawn_from_tile = {}
    tiles = []
    move_history = []
    board_history = []
    pieces_matrix = [[], []]

    # Board Initialization and Setup

    def __init__(self, screen):
        # start game board
        screen.blit(self.board_image, (0, 0))
        self.pieces_matrix = [
            [None for x in range(board_size)] for y in range(board_size)
        ]
        self.tiles = self.create_tiles()
        self.starting_position()
        self.move_history = []
        self.current_player = Eplayers.white

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
                curr = Pawn((column, row), color=Eplayers.white)
                self.pieces_matrix[row][column] = curr
                self.pieces_list[0].append(curr)

        for row in range(7, 4, -1):
            mod = row % 2
            for column in range(0 + mod, board_size - 1 + mod, 2):
                curr = Pawn((column, row), color=Eplayers.black)
                self.pieces_matrix[row][column] = curr
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
        for player_pieces in new_board.pieces_list:
            for piece in player_pieces:
                new_board.get_pawn_from_tile[piece.tile] = piece

        # Deep copy the pieces_matrix
        new_board.pieces_matrix = [
            [
                copy.deepcopy(self.pieces_matrix[y][x], memo)
                for x in range(len(self.pieces_matrix[0]))
            ]
            for y in range(len(self.pieces_matrix))
        ]

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
                pawn = self.pieces_matrix[tile_y][tile_x]
                if pawn and pawn.is_alive():
                    self.pieces_matrix[tile_y][tile_x].draw(screen)

    def show_better_move(self, move: MoveNode, screen):
        if move is None:
            return

        while move:
            from_tile_x, from_tile_y = move.from_tile
            to_tile_x, to_tile_y = move.to_tile

            self.tiles[from_tile_y][from_tile_x].glow(screen, Ecolors.blue)
            self.tiles[to_tile_y][to_tile_x].glow(screen, Ecolors.blue)

            # Move to the next move in the sequence, if it exists
            move = move.children[0] if move.children else None

    def show_move_made(
        self,
        move: MoveNode,
        screen,
        is_analyzing_player,
        is_played_best_move,
    ):
        if not move:
            print("No move to show")
            return

        # Determine the color based on the player analyzing the move
        if is_played_best_move:
            color = Ecolors.yellow
        else:
            color = Ecolors.green if is_analyzing_player else Ecolors.red

        # Iterate through the moves and their children to highlight tiles
        while move:
            from_tile_x, from_tile_y = move.from_tile
            to_tile_x, to_tile_y = move.to_tile

            self.tiles[from_tile_y][from_tile_x].glow(screen, color)
            self.tiles[to_tile_y][to_tile_x].glow(screen, color)

            # Move to the next move in the sequence, if it exists
            move = move.children[0] if move.children else None

    def show_avilable_moves(self, from_tile: tuple, has_jumped: Piece, screen):
        x, y = from_tile
        possible_moves, possible_jumps = self.every_move_possible_for_piece(
            self.pieces_matrix[y][x], has_jumped
        )
        possible_tiles = possible_jumps if possible_jumps else possible_moves
        for currTuple in possible_tiles:
            tile = currTuple.to_tile
            if type(tile) == list:
                for to_tile in tile:  # sometimes tile is a tuple, sometimes its a list.
                    x, y = to_tile
                    self.tiles[y][x].glow(screen, Ecolors.yellow)
            else:
                x, y = tile
                self.tiles[y][x].glow(screen, Ecolors.yellow)

    def get_tile_at_pixel(self, mouse_x, mouse_y):
        for x_tile in range(board_size):
            for y_tile in range(board_size):
                currTile = self.get_tile_from_location(x_tile, y_tile)
                if currTile.tile_rect.collidepoint(mouse_x, mouse_y):
                    return currTile
        return None

    # Movement and Game Mechanics
    def get_piece_at_tile(self, tile: tuple):
        x, y = tile
        return self.pieces_matrix[y][x]

    def where_can_move(self, tile: tuple) -> list[(Tile, bool)]:
        piece = self.get_piece_at_tile(tile)
        x, y = tile
        possible_tiles = []

        if isinstance(piece, Pawn) and piece.alive:
            directions = (
                [(1, 1), (-1, 1)],
                [(1, -1), (-1, -1)],
            )  # White, Black, Right, Left
            directions = directions[piece.color.value - 1]

            for direction in directions:
                dx, dy = direction
                found = False
                new_x, new_y = x + dx, y + dy
                if self.is_location_inside_board(
                    new_x, new_y
                ) and not self.is_tile_taken(new_x, new_y):
                    promoted = self.can_get_promoted(piece, (new_x, new_y))
                    possible_tiles.append(
                        MoveNode(piece, piece.tile, (new_x, new_y), promoted=promoted)
                    )

        if isinstance(piece, King) and piece.alive:
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

                    if not self.is_location_inside_board(new_x, new_y):
                        break
                    elif not self.is_tile_taken(new_x, new_y):
                        possible_tiles.append(
                            MoveNode(piece, piece.tile, (new_x, new_y))
                        )
                    else:
                        break

        return possible_tiles

    def is_tile_taken(self, x, y):
        return (
            self.is_location_inside_board(x, y) and self.pieces_matrix[y][x] is not None
        )

    def is_opponent_pawn_on_tile(self, x, y, color):
        return self.pieces_matrix[y][x] and self.pieces_matrix[y][x].color == Eplayers(
            3 - color.value
        )

    def is_a_color_pawn_on_tile(self, x, y, color):
        return self.pieces_matrix[y][x] and self.pieces_matrix[y][x].color == color

    def where_can_jump(self, tile: tuple):
        piece = self.get_piece_at_tile(tile)
        x, y = tile
        possible_jumps = []

        if isinstance(piece, Pawn) and piece.alive:
            directions = ([(1, 1), (-1, 1)], [(1, -1), (-1, -1)])
            directions = directions[piece.color.value - 1]

            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                jump_x, jump_y = x + 2 * dx, y + 2 * dy

                if self.is_location_inside_board(
                    new_x, new_y
                ) and self.is_location_inside_board(jump_x, jump_y):
                    if self.is_tile_taken(
                        new_x, new_y
                    ) and self.is_opponent_pawn_on_tile(new_x, new_y, piece.color):
                        if not self.is_tile_taken(jump_x, jump_y):
                            promoted = self.can_get_promoted(piece, (jump_x, jump_y))
                            possible_jumps.append(
                                MoveNode(
                                    piece,
                                    tile,
                                    (jump_x, jump_y),
                                    self.pieces_matrix[new_y][new_x],
                                    promoted=promoted,
                                )
                            )

        elif isinstance(piece, King) and piece.alive:
            directions = [
                (1, 1),
                (-1, 1),
                (1, -1),
                (-1, -1),
            ]

            for dx, dy in directions:
                found = None
                for step in range(1, board_size):
                    new_x, new_y = x + step * dx, y + step * dy

                    if not self.is_location_inside_board(
                        new_x, new_y
                    ) or self.is_a_color_pawn_on_tile(new_x, new_y, piece.color):
                        break
                    if (
                        self.is_tile_taken(new_x, new_y)
                        and self.is_opponent_pawn_on_tile(new_x, new_y, piece.color)
                        or found
                        and not self.is_tile_taken(new_x, new_y)
                    ):
                        if not found:
                            found = self.pieces_matrix[new_y][new_x]
                        if not self.is_location_inside_board(new_x + dx, new_y + dy):
                            break
                        if not self.is_tile_taken(new_x + dx, new_y + dy):

                            possible_jumps.append(
                                MoveNode(
                                    piece,
                                    piece.tile,
                                    ((new_x + dx), (new_y + dy)),
                                    found,
                                )
                            )
                        else:
                            break

        return possible_jumps

    def can_get_promoted(self, piece: Piece, to_tile: tuple) -> bool:
        if piece.color == Eplayers.white and to_tile[1] == board_size - 1:
            print("can get promoted", piece, to_tile, piece.color)

            return True
        elif piece.color == Eplayers.black and to_tile[1] == 0:
            print("can get promoted", piece, to_tile, piece.color)

            return True
        return False

    def every_move_possible_for_piece(self, piece: Piece, hasJumped: Piece = None):
        # Get both possible moves and jumps for the piece
        possible_moves = self.where_can_move(piece.tile)
        possible_jumps = self.where_can_jump(piece.tile)

        jump_is_possible = self.jump_is_possible(piece.color)

        # If the piece has just jumped, only consider further jumps for it
        if hasJumped is piece:
            return [], possible_jumps

        # another piece jumped, no moves returns
        if hasJumped and hasJumped is not piece:
            return [], []

        # If a jump is possible for any piece of the same color, don't consider regular moves
        if jump_is_possible:
            return [], possible_jumps

        # no piece has jumped and no jump is possible, return all possible moves
        return possible_moves, possible_jumps

    def every_move_for_player(
        self, color: Eplayers, hasJumped: Piece = None, depth=0, max_depth=3
    ):
        if depth > max_depth:
            return []  # Stop recursion if max depth is exceeded

        jump_moves = []
        found_jump = False
        promoted = False

        # Check all pieces for jump moves
        for piece in self.pieces_list[color.value - 1]:
            if piece.is_alive():
                jump_options = self.where_can_jump(piece.tile)
                if jump_options:
                    found_jump = True
                    for jump_move in jump_options:
                        # Create a new board for simulating the jump
                        temp_board = copy.deepcopy(self)
                        temp_board.apply_move(jump_move)

                        if (
                            piece.color == Eplayers.white
                            and jump_move.to_tile[1] == board_size - 1
                        ) or (
                            piece.color == Eplayers.black and jump_move.to_tile[1] == 0
                        ):
                            promoted = True

                        new_node = MoveNode(
                            piece,
                            piece.tile,
                            jump_move.to_tile,
                            jump_move.killed,
                            promoted=promoted,
                        )
                        promoted = False

                        # Recursively check for further jumps on the temporary board
                        if temp_board.has_more_jumps(jump_move.to_tile):
                            new_node.children = temp_board.every_move_for_player(
                                color, piece, depth + 1, max_depth
                            )
                        else:
                            new_node.children = []

                        jump_moves.append(new_node)

        # If no jumps found, and no jump has been made yet, consider regular moves
        if not found_jump and not hasJumped:
            regular_moves = self.get_regular_moves(color)
            return regular_moves

        return jump_moves

    def get_regular_moves(self, color):
        regular_moves = []
        promoted = False
        for piece in self.pieces_list[color.value - 1]:
            if piece.is_alive():
                regular_options, _ = self.every_move_possible_for_piece(piece, None)
                for move in regular_options:
                    if (
                        piece.color == Eplayers.white
                        and move.to_tile[1] == board_size - 1
                    ) or (piece.color == Eplayers.black and move.to_tile[1] == 0):
                        promoted = True
                    new_node = MoveNode(
                        piece,
                        piece.tile,
                        move.to_tile,
                        None,
                        promoted=promoted,
                    )
                    promoted = False
                    regular_moves.append(new_node)
        return regular_moves

    def move(self, from_tile: tuple, to_tile: tuple, hasJumped: bool, screen):
        x, y = from_tile
        piece = self.pieces_matrix[y][x]
        regular_moves, jump_moves = self.every_move_possible_for_piece(piece, hasJumped)
        possible_moves = jump_moves if jump_moves else regular_moves

        hasJumped = None
        was_promoted = False

        for possible_move in possible_moves:
            if possible_move.to_tile == to_tile:

                if piece:
                    piece.move(to_tile)
                    from_tile_x, from_tile_y = from_tile
                    to_tile_x, to_tile_y = to_tile
                    self.pieces_matrix[to_tile_y][to_tile_x] = piece
                    self.pieces_matrix[from_tile_y][from_tile_x] = None
                    self.pieces_matrix[to_tile_y][to_tile_x].draw(screen)

                    if possible_move.killed and possible_move.killed.tile:
                        hasJumped = piece
                        killed_x, killed_y = possible_move.killed.tile
                        self.pieces_matrix[killed_y][killed_x] = None
                        possible_move.killed.killed()
                        self.pieces_list[possible_move.killed.color.value - 1].remove(
                            possible_move.killed
                        )

                    if isinstance(piece, Pawn):
                        if (
                            piece.color == Eplayers.white
                            and to_tile[1] == board_size - 1
                        ) or (piece.color == Eplayers.black and to_tile[1] == 0):
                            was_promoted = True
                            self.upgrade_to_king(to_tile)
                            piece = self.get_piece_at_tile(
                                to_tile
                            )  # Update piece to the new King
                            hasJumped = None

        move = MoveNode(
            piece, from_tile, to_tile, possible_move.killed, promoted=was_promoted
        )

        # Check if the current piece has more jumps available
        if hasJumped and self.has_more_jumps(to_tile):
            # Do not switch player if more jumps are available
            return move, hasJumped
        else:
            # Switch player if no more jumps are available
            return move, None

    def apply_move(self, move_node: MoveNode, has_jumped: Piece = None):
        if has_jumped is None:
            self.add_move_to_history(move_node)
            self.switch_player()
        while move_node:
            x, y = move_node.from_tile
            move_node.piece = self.pieces_matrix[y][x]

            if move_node.killed:
                x, y = move_node.killed.tile
                move_node.killed = self.pieces_matrix[y][x]
            self._execute_move(move_node)

            if move_node.children != []:
                move_node = move_node.children[0]
            else:
                move_node = None

    def _execute_move(self, move_node: MoveNode):

        # Retrieve the piece to be moved

        from_tile = move_node.from_tile
        piece = self.get_piece_at_tile(from_tile)
        to_tile = move_node.to_tile
        killed_piece = move_node.killed

        # Move the piece to the new tile
        to_tile_x, to_tile_y = to_tile
        self.pieces_matrix[to_tile_y][to_tile_x] = piece
        from_tile_x, from_tile_y = from_tile
        self.pieces_matrix[from_tile_y][from_tile_x] = None

        piece.move(to_tile)  # Update the piece's tile attribute

        # Handle any capture
        if killed_piece:
            killed_piece_tile_x, killed_piece_tile_y = killed_piece.tile
            self.pieces_matrix[killed_piece_tile_y][killed_piece_tile_x] = None
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
        while current_move != []:
            reverse_move_stack.append(current_move)

            if current_move.children != []:
                current_move = current_move.children[0]
            else:
                current_move = []
        print("reverse_move_stack", reverse_move_stack)
        return reverse_move_stack

    def undo_single_move(self, move_node):
        # Undo logic for a single move
        from_tile_x, from_tile_y = move_node.from_tile
        to_tile_x, to_tile_y = move_node.to_tile

        moved_piece = self.get_piece_at_tile(move_node.to_tile)
        if move_node.to_tile and moved_piece is not None:
            self.pieces_matrix[from_tile_y][from_tile_x] = moved_piece
            self.pieces_matrix[to_tile_y][to_tile_x] = None
            moved_piece.tile = move_node.from_tile
        # else:
        #     print(f"No piece found at {move_node.to_tile} to move back")

        # Restore the captured piece, if any
        if move_node.killed:
            captured_piece = move_node.killed

            captured_piece_x, captured_piece_y = captured_piece.tile
            self.pieces_matrix[captured_piece_y][captured_piece_x] = captured_piece
            captured_piece.alive = True
            self.pieces_list[captured_piece.color.value - 1].append(captured_piece)
        if move_node.promoted is True and isinstance(moved_piece, King):
            king = self.get_piece_at_tile(move_node.from_tile)
            self.demote_king_to_pawn(king, move_node.from_tile)

    # Game State and Rules

    def jump_is_possible(self, color: Eplayers) -> bool:
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
            - None if the game is not over.
        """
        white_out_of_moves = self.is_player_out_of_moves(Eplayers.white)
        black_out_of_moves = self.is_player_out_of_moves(Eplayers.black)
        white_out_of_pieces = self.is_player_out_of_pieces(Eplayers.white)
        black_out_of_pieces = self.is_player_out_of_pieces(Eplayers.black)

        if white_out_of_pieces or white_out_of_moves:
            return Eplayers.black  # Black wins
        elif black_out_of_pieces or black_out_of_moves:
            return Eplayers.white  # White wins
        else:
            return None  # Game is not over

    # Piece Management

    def upgrade_to_king(self, tile: tuple):
        x, y = tile
        piece = self.pieces_matrix[y][x]
        if piece is King:
            return

        if piece.color == Eplayers.white and tile[1] != board_size - 1:
            return
        if piece.color == Eplayers.black and tile[1] != 0:
            return

        king = King(tile, piece.color)
        self.pieces_matrix[y][x] = king
        self.pieces_list[piece.color.value - 1].remove(piece)
        self.pieces_list[piece.color.value - 1].append(king)

        print("adding king to pieces_list", king, piece.color.value - 1)
        piece.alive = False

    def demote_king_to_pawn(self, king, original_tile):
        # print("list before demoting", self.pieces_list[king.color.value - 1])
        print("demoting king to pawn")
        print(king, original_tile)
        print(
            "piece in original tile",
            self.pieces_matrix[original_tile[1]][original_tile[0]],
        )
        x, y = original_tile
        if isinstance(king, King):
            pawn = Pawn(original_tile, king.color)  # Recreate the pawn
            self.pieces_matrix[y][x] = pawn

            self.pieces_list[king.color.value - 1].remove(king)
            self.pieces_list[pawn.color.value - 1].append(pawn)
            # except ValueError:
            #     print("ValueError: King not found in pieces_list")
            #     print("king", king, "original tile", original_tile)
            #     print("pieces_list", self.pieces_list)

    def piece_can_be_taken(self, piece):
        # Check if any opponent can jump over the piece
        for opponent_piece in self.pieces_list[piece.color.value - 1]:
            jumps = self.where_can_jump(opponent_piece.tile)
            for jump in jumps:
                if jump.killed == piece:
                    return True
        return False

    def is_piece_protected(self, piece):
        # A piece is considered protected if it can't be eaten if not moved / pieces behind it moves.
        x, y = piece.tile

        if piece.color == Eplayers.white:
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
        return 0 <= x < board_size and 0 <= y < board_size

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

        for x in range(board_size):
            for y in range(board_size):
                piece = self.pieces_matrix[y][x]
                if piece is not None:
                    color = piece.color

                    # Check for pawns and kings
                    if isinstance(piece, Pawn):
                        if color == Eplayers.white:
                            p1_nums[0] += 1
                        else:
                            p2_nums[0] += 1
                    elif isinstance(piece, King):
                        if color == Eplayers.white:
                            p1_nums[1] += 1
                        else:
                            p2_nums[1] += 1

                    # Check for pieces in the back row
                    if (color == Eplayers.white and x == 0) or (
                        color == Eplayers.black and x == 7
                    ):
                        if color == Eplayers.white:
                            p1_nums[2] += 1
                        else:
                            p2_nums[2] += 1

                    # Check for middle rows
                    if x == 3 or x == 4:
                        if 2 <= y <= 5:
                            if color == Eplayers.white:
                                p1_nums[3] += 1
                            else:
                                p2_nums[3] += 1
                        else:
                            if color == Eplayers.white:
                                p1_nums[4] += 1
                            else:
                                p2_nums[4] += 1

                    # Check if can be taken this turn
                    if self.piece_can_be_taken(piece):
                        if color == Eplayers.white:
                            p1_nums[5] += 1
                        else:
                            p2_nums[5] += 1

                    # Check for protected pieces
                    if self.is_piece_protected(piece):
                        if color == Eplayers.white:
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
            Eplayers.black if self.current_player == Eplayers.white else Eplayers.white
        )

    def add_move_to_history(self, move: MoveNode):
        self.move_history.append(move)
        copy_of_board = copy.deepcopy(self)  # Renamed variable
        copy_of_board.undo_move()
        self.board_history.append(copy_of_board)

    def get_history(self):
        history = []
        for counter in range(len(self.move_history)):
            history.append((self.move_history[counter], self.board_history[counter]))
        return history

    def set_history(self, history: list[tuple[MoveNode, "Board"]]):
        move_history = []
        board_history = []
        for move, board in history:
            move_history.append(move)
            board_history.append(board)
        self.move_history = move_history
        self.board_history = board_history

    def __repr__(self):
        board_representation = ""
        for y in reversed(range(board_size)):
            for x in range(board_size):
                piece = self.pieces_matrix[y][x]
                if piece:
                    if piece.color == Eplayers.white:
                        board_representation += "W "
                    elif piece.color == Eplayers.black:
                        board_representation += "B "
                else:
                    board_representation += ". "
            board_representation += "\n"
        return board_representation

    @staticmethod
    def serialize_move_node(move_node):
        serialized = {
            "piece": [
                "king" if isinstance(move_node.piece, King) else "pawn",
                move_node.piece.color,
            ],
            "from_tile": move_node.from_tile,
            "to_tile": move_node.to_tile,
            "killed": move_node.killed.tile if move_node.killed else None,
            "promoted": move_node.promoted,
            "children": [
                Board.serialize_move_node(child) for child in move_node.children
            ],
            "parent": None,
        }
        return serialized

    def unserialize_move_node(self, serialized):
        piece_type, color = serialized["piece"]
        piece = King((0, 0), color) if piece_type == "king" else Pawn((0, 0), color)
        piece.tile = serialized["from_tile"]
        killed = (
            self.get_piece_at_tile(serialized["killed"])
            if serialized["killed"]
            else None
        )
        move_node = MoveNode(
            piece,
            serialized["from_tile"],
            serialized["to_tile"],
            killed,
            serialized["promoted"],
            [self.unserialize_move_node(child) for child in serialized["children"]],
        )
        return move_node


# TODO undo board_history when undoing moves
