import pygame
from Tile import Tile
from Pawn import Pawn
from Enums import EColor
from Main import *
from King import King
from Piece import Piece
from MoveNode import MoveNode


class Board:
    board_image = pygame.image.load(os.path.join("assets", "8x8_checkered_board.png"))
    tile_width, tile_height = window_width // board_size, window_height // board_size

    pieces_list = [[], []]
    get_pawn_from_tile = {}
    tiles = []

    def __init__(self):
        # start game board
        screen.blit(self.board_image, (0, 0))
        self.tiles = self.create_tiles()
        self.starting_position()

        # for row in self.tiles:
        #     for tile in row:
        #         self.get_pawn_from_tile[tile] = None
        # self.get_pawn_from_tile[self.tiles[3][3]] = Pawn(self.tiles[3][3], color=EColor.white)
        # self.pieces_list[0].append
        # self.get_pawn_from_tile[self.tiles[2][2]] = King(self.tiles[2][2], color=EColor.black)

    def draw(self):
        screen.blit(self.board_image, (0, 0))
        for tile_x in range(board_size):
            for tile_y in range(board_size):
                curr_tile = self.get_tile_from_location(tile_x, tile_y)
                pawn = self.get_pawn_from_tile[curr_tile]
                if pawn and pawn.is_alive():
                    self.get_pawn_from_tile[curr_tile].draw()

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
                    possible_tiles.append(MoveNode(piece, self.tiles[new_y][new_x]))

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
                        possible_tiles.append(MoveNode(piece, self.tiles[new_y][new_x]))
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
                                    self.tiles[new_y + dy][new_x + dx],
                                    found,
                                )
                            )
                        else:
                            break

        return possible_jumps

    def jump_is_possible(self, color: EColor) -> bool:
        for piece in self.pieces_list[color.value - 1]:
            if self.where_can_jump(piece.tile) != []:
                return True
        return False

    def has_more_jumps(self, tile):
        return self.where_can_jump(tile) != []

    def move(self, from_tile: Tile, to_tile: Tile, hasJumped: bool):
        possible_moves = self.every_move_possible_from_tile(from_tile, hasJumped)
        hasJumped = False
        for possible_move in possible_moves:
            if possible_move.to_tile == to_tile:
                piece = self.get_pawn_from_tile[from_tile]
                if piece:
                    piece.move(to_tile)
                    self.get_pawn_from_tile[to_tile] = piece
                    self.get_pawn_from_tile[from_tile] = None
                    self.get_pawn_from_tile[to_tile].draw()
                    self.upgrade_to_king(to_tile)
                if possible_move.killed and possible_move.killed.tile:
                    hasJumped = True
                    self.get_pawn_from_tile[possible_move.killed.tile] = None
                    possible_move.killed.killed()
                    self.pieces_list[possible_move.killed.color.value - 1].remove(
                        possible_move.killed
                    )
        return hasJumped

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

        piece.alive = False

    def every_move_possible_from_tile(
        self, from_tile: Tile, hasJumped: Piece = None
    ) -> list[MoveNode]:
        piece = self.get_pawn_from_tile[from_tile]
        possible_moves = []
        if (
            hasJumped is not None
            or hasJumped is not None
            and hasJumped.tile == from_tile
        ):
            possible_moves += self.where_can_jump(from_tile)
            if possible_moves:  # Check if the list is not empty
                last_move = possible_moves[-1]
                last_move.children = self.every_move_possible_from_tile(
                    last_move.to_tile
                )

        if piece and not self.jump_is_possible(piece.color):
            possible_moves += self.where_can_move(from_tile)
        return possible_moves

    def show_avilable_moves(self, from_tile: Tile, has_jumped: bool):
        possible_tiles = self.every_move_possible_from_tile(from_tile, has_jumped)

        for currTuple in possible_tiles:
            tile = currTuple.to_tile
            tile.glow_yellow()

    def get_tile_from_location(self, x, y) -> Tile:
        return self.tiles[y][x]

    def is_location_inside_board(self, x, y):
        return 0 <= x < len(self.tiles) and 0 <= y < len(self.tiles[0])

    def get_tile_at_pixel(self, mouse_x, mouse_y):
        for x_tile in range(board_size):
            for y_tile in range(board_size):
                currTile = self.get_tile_from_location(x_tile, y_tile)
                if currTile.tile_rect.collidepoint(mouse_x, mouse_y):
                    return currTile
        return None

    def every_move_for_player(self, color: EColor, hasJumped=False):
        moves_list = []
        for piece in self.pieces_list[color.value - 1]:
            for move in Board.every_move_possible_from_tile(
                self, piece.tile, hasJumped
            ):
                # moves_list.append((piece, piece.tile, move[0], move[1]))
                moves_list.append(MoveNode(piece, move.to_tile, move.killed))
                if move.killed is not None:
                    moves_list[-1].children = self.every_move_for_player(
                        piece.color, True
                    )
        return moves_list
        # TODO test if works

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

            # Check bounds and if a friendly piece is behind
            if 0 <= behind_x < board_size and 0 <= behind_y < board_size:
                behind_tile = self.tiles[behind_y][behind_x]
                behind_piece = self.get_pawn_from_tile[behind_tile]
                if behind_piece and behind_piece.color == piece.color:
                    # Check if there's no opponent piece in the position to jump over the current piece
                    opponent_jump_pos_x, opponent_jump_pos_y = x - dx, y - dy
                    if (
                        0 <= opponent_jump_pos_x < board_size
                        and 0 <= opponent_jump_pos_y < board_size
                    ):
                        opponent_jump_tile = self.tiles[opponent_jump_pos_y][
                            opponent_jump_pos_x
                        ]
                        opponent_piece = self.get_pawn_from_tile[opponent_jump_tile]
                        if not opponent_piece or opponent_piece.color == piece.color:
                            return True

        return False
