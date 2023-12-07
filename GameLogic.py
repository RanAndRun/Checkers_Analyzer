from Piece import Piece
from Pawn import Pawn
from King import King
from Enums import EColor
from Tile import Tile
from Board import Board


# game logic class is responsible for moving a piece. upgrading a piece. jumping over a piece. shows where can a piece move.
# TODO check where can a peice move


def where_can_move(tile: Tile) -> list[Tile]:
    piece = Board.get_pawn_from_tile(tile=tile)
    tiles = Board.get_tiles()
    x, y = tile.get_location()
    possible_tiles = []
    if type(piece) is Pawn:
        if piece.color == EColor.white:
            print("white")
            if (
                x + 1 < len(tiles)
                and y + 1 < len(tiles[0])
                and type(Board.get_pawn_from_tile(tiles[x + 1][y + 1])) != Pawn
            ):
                possible_tiles.append(tiles[x + 1][y - 1])

            if (
                x - 1 >= 0
                and y + 1 < len(tiles[0])
                and type(Board.get_pawn_from_tile(tiles[x - 1][y + 1])) != Pawn
            ):
                possible_tiles.append(tiles[x - 1][y - 1])

        else:
            if (
                x + 1 < len(tiles)
                and y - 1 >= 0
                and type(Board.get_pawn_from_tile(tiles[x + 1][y - 1])) != Pawn
            ):
                possible_tiles.append(tiles[x + 1][y + 1])

            if (
                x - 1 >= 0
                and y - 1 >= 0
                and type(Board.get_pawn_from_tile(tiles[x - 1][y - 1])) != Pawn
            ):
                possible_tiles.append(tiles[x - 1][y + 1])

        # TODO king moves

    return possible_tiles
