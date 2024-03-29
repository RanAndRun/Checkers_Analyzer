import pygame
import copy
from Tile import Tile
from Pawn import Pawn
from Enums import Eplayers, Ecolors
from os import path
from Config import *
from King import King
from Piece import Piece
from MoveNode import MoveNode


class Board:

    board_image = pygame.image.load(path.join("assets", "8x8_checkered_board.png"))
    size = (WINDOW_SIZE, WINDOW_SIZE)
    board_image = pygame.transform.scale(board_image, size)

    whites_turn = path.join("assets", "RedsTurn.png")
    whites_turn = pygame.image.load(whites_turn)
    whites_turn = pygame.transform.scale(whites_turn, (TILE_SIZE, TILE_SIZE))

    blacks_turn = path.join("assets", "BlacksTurn.png")
    blacks_turn = pygame.image.load(blacks_turn)
    blacks_turn = pygame.transform.scale(blacks_turn, (TILE_SIZE, TILE_SIZE))

    # Board Initialization and Setup

    def __init__(self, screen):
        # start game board
        screen.blit(self.board_image, (0, 0))
        self.pieces_matrix = [
            [None for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)
        ]
        self.current_player = Eplayers.white
        self.winner = None
        self.pieces_list = [[], []]
        self.tiles = []
        self.move_history = []
        self.board_history = []
        self.tiles = self.create_tiles()
        self.starting_position()

    def create_tiles(self):
        # create tiles when the board initialze

        tiles = [[None for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]

        x_point = 0
        y_point = WINDOW_SIZE - TILE_SIZE

        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                tiles[y][x] = Tile(x, y, x_point, y_point)
                x_point = x_point + TILE_SIZE
            x_point = 0
            y_point = y_point - TILE_SIZE

        return tiles

    def starting_position(self):
        # set up the starting position of the pieces
        for row in range(3):
            mod = row % 2
            for column in range(0 + mod, BOARD_SIZE - 1 + mod, 2):
                curr = Pawn((column, row), color=Eplayers.white)
                self.pieces_matrix[row][column] = curr
                self.pieces_list[0].append(curr)

        for row in range(7, 4, -1):
            mod = row % 2
            for column in range(0 + mod, BOARD_SIZE - 1 + mod, 2):
                curr = Pawn((column, row), color=Eplayers.black)
                self.pieces_matrix[row][column] = curr
                self.pieces_list[1].append(curr)

    def __deepcopy__(self, memo):
        # Deep copy the board and its attributes
        new_board = self.__class__.__new__(self.__class__)
        memo[id(self)] = new_board

        # Deep copy attributes
        new_board.tiles = [
            [copy.deepcopy(self.tiles[y][x], memo) for x in range(BOARD_SIZE)]
            for y in range(BOARD_SIZE)
        ]
        new_board.pieces_list = [
            [copy.deepcopy(piece, memo) for piece in player_pieces]
            for player_pieces in self.pieces_list
        ]

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
        # Draw the board and all pieces

        screen.blit(self.board_image, (0, 0))
        if self.current_player == Eplayers.white:
            screen.blit(
                self.whites_turn,
                (WINDOW_SIZE - TILE_SIZE, WINDOW_SIZE - TILE_SIZE),
            )
        else:
            screen.blit(
                self.blacks_turn,
                (WINDOW_SIZE - TILE_SIZE, WINDOW_SIZE - TILE_SIZE),
            )
        for tile_x in range(BOARD_SIZE):
            for tile_y in range(BOARD_SIZE):
                pawn = self.pieces_matrix[tile_y][tile_x]
                if pawn and pawn.is_alive():
                    self.pieces_matrix[tile_y][tile_x].draw(screen)

    def show_move(
        self,
        move: MoveNode,
        screen,
        is_analyzing_player,
        display_state,
    ):
        if not move:
            return

        # Determine the color based on the player analyzing the move
        if display_state == "played_move_best":
            color = Ecolors.yellow
        elif display_state == "played_move":
            color = Ecolors.green if is_analyzing_player else Ecolors.red
        elif display_state == "best_move" or display_state == "show_best_move_sequence":
            color = Ecolors.blue

        # Iterate through the moves and their children to highlight tiles
        while move:
            from_tile_x, from_tile_y = move.get_from_tile()
            to_tile_x, to_tile_y = move.get_to_tile()

            self.tiles[from_tile_y][from_tile_x].glow(screen, color)
            self.tiles[to_tile_y][to_tile_x].glow(screen, color)

            # Move to the next move in the sequence, if it exists
            move = move.get_children()[0] if move.get_children() else None

    def show_available_moves(self, from_tile: tuple, has_jumped: Piece, screen):
        x, y = from_tile
        possible_moves, possible_jumps = self.every_move_possible_for_piece(
            self.pieces_matrix[y][x], has_jumped
        )
        possible_tiles = possible_jumps if possible_jumps else possible_moves
        for currTuple in possible_tiles:
            tile = currTuple.get_to_tile()
            x, y = tile
            self.tiles[y][x].glow(screen, Ecolors.yellow)

    def get_tile_at_pixel(self, mouse_x, mouse_y):
        for x_tile in range(BOARD_SIZE):
            for y_tile in range(BOARD_SIZE):
                currTile = self.get_tile_from_location(x_tile, y_tile)
                if currTile.get_tile_rect().collidepoint(mouse_x, mouse_y):
                    return currTile
        return None

    # Movement and Game Mechanics

    def where_can_move(self, tile: tuple):
        # Get all possible regular moves for a piece at a given tile
        piece = self.get_piece_at_tile(tile)
        x, y = tile
        possible_tiles = []

        if isinstance(piece, Pawn) and piece.is_alive():
            directions = (
                [(1, 1), (-1, 1)],
                [(1, -1), (-1, -1)],
            )  # White, Black, Right, Left
            directions = directions[piece.color.value - 1]

            for direction in directions:
                dx, dy = direction
                found = False
                new_x, new_y = x + dx, y + dy
                if self._is_location_inside_board(
                    new_x, new_y
                ) and not self._is_tile_taken(new_x, new_y):
                    promoted = self._can_get_promoted(piece, (new_x, new_y))
                    possible_tiles.append(
                        MoveNode(
                            piece, piece.get_tile(), (new_x, new_y), promoted=promoted
                        )
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

                for step in range(1, BOARD_SIZE):
                    new_x, new_y = x + step * dx, y + step * dy

                    if not self._is_location_inside_board(new_x, new_y):
                        break
                    elif not self._is_tile_taken(new_x, new_y):
                        possible_tiles.append(
                            MoveNode(piece, piece.tile, (new_x, new_y))
                        )
                    else:
                        break

        return possible_tiles

    def where_can_jump(self, tile: tuple):
        piece = self.get_piece_at_tile(tile)
        x, y = tile
        possible_jumps = []

        if isinstance(piece, Pawn) and piece.is_alive():
            directions = ([(1, 1), (-1, 1)], [(1, -1), (-1, -1)])
            directions = directions[piece.color.value - 1]

            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                jump_x, jump_y = x + 2 * dx, y + 2 * dy

                if self._is_location_inside_board(
                    new_x, new_y
                ) and self._is_location_inside_board(jump_x, jump_y):
                    if self._is_tile_taken(
                        new_x, new_y
                    ) and self._is_a_color_piece_on_tile(
                        new_x, new_y, Eplayers(3 - piece.get_color().value)
                    ):
                        if not self._is_tile_taken(jump_x, jump_y):
                            promoted = self._can_get_promoted(piece, (jump_x, jump_y))
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
                for step in range(1, BOARD_SIZE):
                    new_x, new_y = x + step * dx, y + step * dy

                    if not self._is_location_inside_board(
                        new_x, new_y
                    ) or self._is_a_color_piece_on_tile(
                        new_x, new_y, piece.get_color()
                    ):
                        break
                    if (
                        self._is_tile_taken(new_x, new_y)
                        and self._is_a_color_piece_on_tile(
                            new_x, new_y, Eplayers(3 - piece.get_color().value)
                        )
                        or found
                        and not self._is_tile_taken(new_x, new_y)
                    ):
                        if not found:
                            found = self.pieces_matrix[new_y][new_x]
                        if not self._is_location_inside_board(new_x + dx, new_y + dy):
                            break
                        if not self._is_tile_taken(new_x + dx, new_y + dy):

                            possible_jumps.append(
                                MoveNode(
                                    piece,
                                    piece.get_tile(),
                                    ((new_x + dx), (new_y + dy)),
                                    found,
                                )
                            )
                        else:
                            break

        return possible_jumps

    def every_move_possible_for_piece(self, piece: Piece, has_jumped: Piece = None):
        # Get both possible moves and jumps for the piece
        possible_moves = self.where_can_move(piece.get_tile())
        possible_jumps = self.where_can_jump(piece.get_tile())

        jump_is_possible = self._is_jump_possible(piece.color)

        # If the piece has just jumped, only consider further jumps for it
        if has_jumped is piece:
            return [], possible_jumps

        # other piece jumped, no moves to return
        if has_jumped and has_jumped is not piece:
            return [], []

        # If a jump is possible for any piece of the same color, don't consider regular moves
        if jump_is_possible:
            return [], possible_jumps

        # no piece has jumped and no jump is possible, return all possible moves
        return possible_moves, possible_jumps

    def every_move_for_player(
        self, color: Eplayers, has_jumped: Piece = None, depth=0, max_depth=4
    ):
        if depth > max_depth:
            return []  # Stop recursion if max depth is exceeded

        jump_moves = []
        found_jump = False
        promoted = False

        pieces_list = (
            self.pieces_list[color.value - 1] if not has_jumped else [has_jumped]
        )
        # Check all pieces for jump moves
        for piece in self.pieces_list[color.value - 1]:
            if piece.is_alive():
                jump_options = self.where_can_jump(piece.get_tile())
                if jump_options:
                    found_jump = True
                    for jump_move in jump_options:
                        # Create a new board for simulating the jump
                        temp_board = copy.deepcopy(self)
                        temp_board.apply_move(jump_move)

                        promoted = self._can_get_promoted(
                            piece, jump_move.get_to_tile()
                        )

                        new_node = MoveNode(
                            piece,
                            piece.get_tile(),
                            jump_move.get_to_tile(),
                            jump_move.get_killed(),
                            promoted=promoted,
                        )
                        promoted = False

                        # Recursively check for further jumps on the temporary board
                        if temp_board._has_more_jumps(jump_move.get_to_tile()):
                            new_node.set_children(
                                temp_board.every_move_for_player(
                                    color, piece, depth + 1, max_depth
                                )
                            )
                        else:
                            new_node.set_children([])

                        jump_moves.append(new_node)

        # If no jumps found, and no jump has been made yet, consider regular moves
        if not found_jump and not has_jumped:
            regular_moves = self.get_all_regular_moves_for_player(color)
            return regular_moves

        return jump_moves

    def get_all_regular_moves_for_player(self, color):
        regular_moves = []
        promoted = False
        for piece in self.pieces_list[color.value - 1]:
            if piece.is_alive():
                regular_options = self.where_can_move(piece.get_tile())
                for move in regular_options:
                    promoted = self._can_get_promoted(piece, move.get_to_tile())
                    new_node = MoveNode(
                        piece,
                        piece.get_tile(),
                        move.get_to_tile(),
                        None,
                        promoted=promoted,
                    )
                    promoted = False
                    regular_moves.append(new_node)
        return regular_moves

    def move(self, from_tile: tuple, to_tile: tuple, has_jumped: bool):
        x, y = from_tile
        piece = self.get_piece_at_tile(from_tile)
        regular_moves, jump_moves = self.every_move_possible_for_piece(
            piece, has_jumped
        )
        possible_moves = jump_moves if jump_moves else regular_moves

        has_jumped = None

        move = next(
            (move for move in possible_moves if move.get_to_tile() == to_tile), None
        )
        if move:
            self._execute_move(move)
            if move.get_killed():
                has_jumped = piece

            if move.get_promoted() == True:
                hashJumped = None

        # Check if the current piece has more jumps available
        if has_jumped and self._has_more_jumps(to_tile):
            # Do not switch player if more jumps are available
            return move, has_jumped
        else:
            # Switch player if no more jumps are available
            return move, None

    def apply_move(self, move_node: MoveNode, add_to_history=False):
        if add_to_history:
            self.add_move_to_history(move_node)

        self.switch_player()

        while move_node:
            move_node.set_piece(self.get_piece_at_tile(move_node.get_from_tile()))

            if move_node.killed:
                move_node.set_killed(self.get_piece_at_tile(move_node.killed.tile))

            self._execute_move(move_node)

            if move_node.children != []:
                move_node = move_node.get_children()[0]
            else:
                move_node = None

    def _execute_move(self, move_node: MoveNode):

        # Retrieve the piece to be moved

        from_tile = move_node.get_from_tile()
        piece = self.get_piece_at_tile(from_tile)
        to_tile = move_node.get_to_tile()
        killed_piece = move_node.get_killed()

        # Move the piece to the new tile
        to_tile_x, to_tile_y = to_tile
        self.pieces_matrix[to_tile_y][to_tile_x] = piece
        from_tile_x, from_tile_y = from_tile
        self.pieces_matrix[from_tile_y][from_tile_x] = None

        piece.move(to_tile)  # Update the piece's tile attribute

        # Handle any capture
        if killed_piece:
            killed_piece_tile_x, killed_piece_tile_y = killed_piece.get_tile()
            self.pieces_matrix[killed_piece_tile_y][killed_piece_tile_x] = None
            killed_piece.killed()  # Mark the killed piece as not alive
            self.pieces_list[killed_piece.get_color().value - 1].remove(killed_piece)

        # Handle promotion to King if necessary
        if isinstance(piece, Pawn) and move_node.get_promoted():
            self.upgrade_to_king(to_tile)

    def upgrade_to_king(self, tile: tuple):
        x, y = tile
        piece = self.get_piece_at_tile(tile)

        if self._can_get_promoted(piece, tile) == False:
            return

        king = King(tile, piece.color)
        self.pieces_matrix[y][x] = king
        self.pieces_list[piece.color.value - 1].remove(piece)
        self.pieces_list[piece.color.value - 1].append(king)

        piece.alive = False

    def demote_king_to_pawn(self, king, original_tile):
        x, y = original_tile
        if isinstance(king, King):
            pawn = Pawn(original_tile, king.color)  # Recreate the pawn
            self.pieces_matrix[y][x] = pawn

            self.pieces_list[king.color.value - 1].remove(king)
            self.pieces_list[pawn.color.value - 1].append(pawn)

    # Undo Mechanics

    def undo_move(self):
        if not self.move_history:
            return  # No move to undo

        self.switch_player()
        last_move_sequence = self.move_history.pop()

        # Create a stack to store the moves in reverse order
        reverse_move_stack = self._build_reverse_stack(last_move_sequence)

        # Now undo the moves in reverse order
        while reverse_move_stack:
            move_to_undo = reverse_move_stack.pop()
            self._undo_single_move(move_to_undo)

    def _build_reverse_stack(self, move_node):
        reverse_move_stack = []
        current_move = move_node
        while current_move != []:
            reverse_move_stack.append(current_move)

            if current_move.children != []:
                current_move = current_move.get_children()[0]
            else:
                current_move = []
        return reverse_move_stack

    def _undo_single_move(self, move_node):
        # Undo logic for a single move
        from_tile_x, from_tile_y = move_node.get_from_tile()
        to_tile_x, to_tile_y = move_node.get_to_tile()

        moved_piece = self.get_piece_at_tile(move_node.get_to_tile())
        if move_node.get_to_tile() and moved_piece is not None:
            self.pieces_matrix[from_tile_y][from_tile_x] = moved_piece
            self.pieces_matrix[to_tile_y][to_tile_x] = None
            moved_piece.set_tile(move_node.get_from_tile())

        if move_node.get_killed():
            captured_piece = move_node.get_killed()

            captured_piece_x, captured_piece_y = captured_piece.get_tile()
            self.pieces_matrix[captured_piece_y][captured_piece_x] = captured_piece
            captured_piece.set_alive(True)
            self.pieces_list[captured_piece.get_color().value - 1].append(
                captured_piece
            )
        if move_node.get_promoted() == True and isinstance(moved_piece, King):
            king = self.get_piece_at_tile(move_node.get_from_tile())
            self.demote_king_to_pawn(king, move_node.get_from_tile())

    # Game State and Rules

    def is_player_out_of_moves(self, player_color):
        # Check if a player has no legal moves left.

        for piece in self.pieces_list[player_color.value - 1]:
            if piece.is_alive() and self.every_move_possible_for_piece(piece) != (
                [],
                [],
            ):
                return False  # Found a piece with a legal move
        return True  # No legal moves found

    def is_player_out_of_pieces(self, player_color):
        # Check if a player has no pieces left.
        for piece in self.pieces_list[player_color.value - 1]:
            if piece.is_alive():
                return False
        return True

    def is_game_over(self):
        white_out_of_moves = self.is_player_out_of_moves(Eplayers.white)
        black_out_of_moves = self.is_player_out_of_moves(Eplayers.black)
        white_out_of_pieces = self.is_player_out_of_pieces(Eplayers.white)
        black_out_of_pieces = self.is_player_out_of_pieces(Eplayers.black)

        # Check for win conditions first
        if white_out_of_pieces or white_out_of_moves:
            self.winner = Eplayers.black  # Black wins
        elif black_out_of_pieces or black_out_of_moves:
            self.winner = Eplayers.white  # White wins
        # Then check for draw
        elif (
            not white_out_of_pieces
            and not black_out_of_pieces
            and white_out_of_moves
            and black_out_of_moves
        ):
            self.winner = "draw"  # Game is a draw
        # If none of the above, the game is still ongoing
        else:
            return None

        return self.winner

    def resign(self, player):
        if player == Eplayers.white:
            self.winner = Eplayers.black
        else:
            self.winner = Eplayers.white

    # Piece Management

    def piece_can_be_taken(self, piece):
        # Check if any opponent can jump over the piece
        for opponent_piece in self.pieces_list[piece.get_color().value - 1]:
            jumps = self.where_can_jump(opponent_piece.get_tile())
            for jump in jumps:
                if jump.get_killed() == piece:
                    return True
        return False

    def is_piece_protected(self, piece):
        # A piece is considered protected if it can't be eaten if not moved / pieces behind it moves.
        x, y = piece.get_tile()

        behind_moves = [
            [
                (-1, -1),
                (1, -1),
            ],
            [
                (-1, 1),
                (1, 1),
            ],
        ]
        behind_moves = behind_moves[piece.get_color().value - 1]

        for move in behind_moves:
            dx, dy = move
            behind_x, behind_y = x + dx, y + dy

            if not self._is_tile_taken(behind_x, behind_y):
                return False

        return True

    def evaluate_board_score(self):
        # Evaluate the board state and return an array for the current board

        #  Index 0: Number of pawns
        #  Index 1: Number of kings
        #  Index 2: Number in back row
        #  Index 3: Number in middle box
        #  Index 4: Number in middle 2 rows, not box
        #  Index 5: Number that can be taken this turn
        #  Index 6: Number that are protected

        p1_nums = [0] * 7  # Player 1 scores
        p2_nums = [0] * 7  # Player 2 scores

        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
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

    # Utilities

    def __repr__(self):
        board_representation = ""
        for y in reversed(range(BOARD_SIZE)):
            for x in range(BOARD_SIZE):
                piece = self.get_piece_at_tile((x, y))
                if piece:
                    if piece.get_color() == Eplayers.white:
                        board_representation += "W "
                    elif piece.get_color() == Eplayers.black:
                        board_representation += "B "
                else:
                    board_representation += ". "
            board_representation += "\n"
        return board_representation

    def _is_a_color_piece_on_tile(self, x, y, color):
        return self.pieces_matrix[y][x] and self.pieces_matrix[y][x].color == color

    def _is_tile_taken(self, x, y):
        return (
            self._is_location_inside_board(x, y)
            and self.pieces_matrix[y][x] is not None
        )

    def _has_more_jumps(self, tile: tuple) -> bool:
        return self.where_can_jump(tile) != []

    def _is_jump_possible(self, color: Eplayers) -> bool:
        for piece in self.pieces_list[color.value - 1]:
            if self._has_more_jumps(piece.get_tile()):
                return True
        return False

    def _can_get_promoted(self, piece: Piece, to_tile: tuple) -> bool:
        # Check if a piece can be promoted to a King
        if piece is King:
            return False
        if piece.color == Eplayers.white and to_tile[1] == BOARD_SIZE - 1:
            return True
        elif piece.color == Eplayers.black and to_tile[1] == 0:
            return True
        return False

    def _is_location_inside_board(self, x, y):
        return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

    # getters and setters

    def add_move_to_history(self, move: MoveNode):
        self.move_history.append(move)
        copy_of_board = copy.deepcopy(self)  # Renamed variable
        copy_of_board.undo_move()
        self.board_history.append(copy_of_board)

    def get_winner(self):
        return self.winner

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

    def get_piece_at_tile(self, tile: tuple):
        x, y = tile
        return self.pieces_matrix[y][x]

    def get_tile_from_location(self, x, y) -> Tile:
        return self.tiles[y][x]

    def get_current_player(self):
        return self.current_player

    def switch_player(self):
        # Switch the current player
        self.current_player = (
            Eplayers.black if self.current_player == Eplayers.white else Eplayers.white
        )

    # Serialization
    @staticmethod
    def serialize_move_node(move_node: MoveNode):
        piece_type = "king" if isinstance(move_node.get_piece(), King) else "pawn"
        piece_color = move_node.get_piece().get_color()
        from_tile = f"({move_node.get_from_tile()[0]},{move_node.get_from_tile()[1]})"  # Tuple to string
        to_tile = f"({move_node.get_to_tile()[0]},{move_node.get_to_tile()[1]})"
        killed = (
            str(move_node.get_killed().get_tile()) if move_node.get_killed() else "None"
        )
        promoted = str(move_node.get_promoted())
        children = ";".join(
            [Board.serialize_move_node(child) for child in move_node.get_children()]
        )

        serialized = f"{piece_type}${piece_color}${from_tile}${to_tile}${killed}${promoted}${children}"
        return serialized

    def unserialize_move_node(self, serialized):
        elements = serialized.split("$", 6)
        (
            piece_type,
            color,
            from_tile_str,
            to_tile_str,
            killed_tile_str,
            promoted_str,
            children_str,
        ) = elements

        piece = self.get_piece_at_tile(eval(from_tile_str))

        killed = (
            self.get_piece_at_tile(eval(killed_tile_str))
            if killed_tile_str != "None"
            else None
        )
        children = [
            self.unserialize_move_node(child_str)
            for child_str in children_str.split(";")
            if child_str
        ]

        move_node = MoveNode(
            piece,
            eval(from_tile_str),
            eval(to_tile_str),
            killed,
            eval(promoted_str),
            children,
        )

        return move_node
