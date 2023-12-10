import pygame
import os
from Tile import Tile
from Pawn import Pawn
from Enums import EColor
from Main import window_height, board_size, window_width, board_size
from King import King


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
                    possible_tiles.append((self.tiles[new_y][new_x], None))

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
                        possible_tiles.append((self.tiles[new_y][new_x], None))
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
                            (
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
                                (self.tiles[new_y + dy][new_x + dx], found)
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

    def every_move_possible(self, from_tile: Tile, hasJumped: bool):
        jump_is_possible = self.jump_is_possible(
            self.get_pawn_from_tile[from_tile].color
        )
        possible_moves = self.where_can_jump(from_tile)
        if not hasJumped and not jump_is_possible:
            possible_moves += self.where_can_move(from_tile)
        return possible_moves

    def move(self, from_tile: Tile, to_tile: Tile, hasJumped: bool):
        possible_moves = self.every_move_possible(from_tile, hasJumped)
        hasJumped = False
        for possible_move in possible_moves:
            if possible_move[0] == to_tile:
                piece = self.get_pawn_from_tile[from_tile]
                if piece:
                    piece.move(to_tile)
                    self.get_pawn_from_tile[to_tile] = piece
                    self.get_pawn_from_tile[from_tile] = None
                    self.get_pawn_from_tile[to_tile].draw()
                    self.upgrade_to_king(to_tile)
                if possible_move[1] and possible_move[1].tile:
                    hasJumped = True
                    self.get_pawn_from_tile[possible_move[1].tile] = None
                    possible_move[1].killed()
                    self.pieces_list[possible_move[1].color.value - 1].remove(
                        possible_move[1]
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

    def show_avilable_moves(self, from_tile: Tile, has_jumped: bool):
        possible_tiles = self.every_move_possible(from_tile, has_jumped)

        for currTuple in possible_tiles:
            tile = currTuple[0]
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
