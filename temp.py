from Tile import Tile
from Pawn import Pawn
from Enms import EColor
from Main import *
from King import King


class Board:
    board_image = pygame.image.load(os.path.join("assets", "8x8_checkered_board.png"))
    tile_width, tile_height = window_width // board_size, window_height // board_size
    tile_pawn = {}

    def __init__(self):
        # start game board
        screen.blit(self.board_image, (0, 0))
        self.tiles = self.create_tiles()
        self.starting_position()

        # self.get_pawn_from_tile = {}
        # for row in self.tiles:
        #     for tile in row:
        #         self.get_pawn_from_tile[tile] = None
        # self.get_pawn_from_tile[self.tiles[3][3]] = Pawn(self.tiles[3][3], color=EColor.white)
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
                self.get_pawn_from_tile[self.tiles[row][column]] = Pawn(
                    self.tiles[row][column], color=EColor.white
                )

        for row in range(7, 4, -1):
            mod = row % 2
            for column in range(0 + mod, board_size - 1 + mod, 2):
                self.get_pawn_from_tile[self.tiles[row][column]] = Pawn(
                    self.tiles[row][column], color=EColor.black
                )

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
                [(1, 2), (-1, 1)],
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
                found = None

                for step in range(1, board_size):
                    new_x, new_y = x + step * dx, y + step * dy

                    if not self.is_location_inside_board(new_x, new_y):
                        break

                    if is_tile_not_taken(new_x, new_y) and not found:
                        possible_tiles.append((self.tiles[new_y][new_x], None))
                    elif is_opponent_pawn_on_tile(new_x, new_y, piece.color):
                        found = self.get_pawn_from_tile[self.tiles[new_y][new_x]]

        return possible_tiles

    def where_can_jump(self, tile: Tile) -> list[(Tile, bool)]:
        piece = self.get_pawn_from_tile[tile]
        x, y = tile.get_location()
        possible_jumps = []

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

                # might be able to delete this lines, is_lovation_inside_board is inside is_tile_not_taken
                if not self.is_location_inside_board(new_x, new_y):
                    continue

                elif not is_tile_not_taken(new_x, new_y) and is_opponent_pawn_on_tile(
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

                    if not self.is_location_inside_board(new_x, new_y):
                        break

                    elif is_opponent_pawn_on_tile(new_x, new_y, piece.color):
                        found = self.get_pawn_from_tile[self.tiles[new_y][new_x]]
                        if is_tile_not_taken(new_x, new_y):
                            possible_jumps.append((self.tiles[new_y][new_x], found))
                        if not is_tile_not_taken(new_x + dx, new_y + dy):
                            break

        return possible_jumps

    def move(self, from_tile: Tile, to_tile: Tile):
        possible_moves = self.where_can_move(from_tile)
        for possible_move in possible_moves:
            if possible_move[0] == to_tile:
                pawn = self.get_pawn_from_tile[from_tile]
                if pawn:
                    self.get_pawn_from_tile[from_tile].move(to_tile)
                    self.get_pawn_from_tile[to_tile] = self.get_pawn_from_tile[
                        from_tile
                    ]
                    self.get_pawn_from_tile[from_tile] = None
                    self.get_pawn_from_tile[to_tile].draw()
                    self.upgrade_to_king(to_tile)
                if possible_move[1] and possible_move[1].tile:
                    self.get_pawn_from_tile[possible_move[1].tile] = None
                    possible_move[1].killed()

    def upgrade_to_king(self, tile: Tile):
        piece = self.get_pawn_from_tile[tile]
        if piece is King:
            return

        if piece.color == EColor.white and tile.row != board_size - 1:
            return
        if piece.color == EColor.black and tile.row != 0:
            return

        self.get_pawn_from_tile[tile] = King(tile, piece.color)
        piece.alive = False

    def show_avilable_moves(self, from_tile: Tile):
        possible_tiles = self.where_can_move(from_tile)
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
