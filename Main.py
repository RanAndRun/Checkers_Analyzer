import pygame, sys
import os
from Board import *
from time import sleep
from Enums import EColor


window_width = 1200
window_height = 1200
board_size = 8

FPS = 30
fps_clock = pygame.time.Clock()

pygame.init()

screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Checkers_Analyzer")


def handle_mouse_click(
    board,
    tile,
    first_selection,
    second_selection,
    is_white_to_play,
    hasJumped,
    before_move,
):
    if first_selection is None:
        if board.get_pawn_from_tile[tile] and board.get_pawn_from_tile[tile].color == (
            EColor.white if is_white_to_play else EColor.black
        ):
            first_selection = tile
    elif board.get_pawn_from_tile[tile] is None:
        second_selection = tile

        move, hasJumped = board.move(first_selection, second_selection, hasJumped)

        if before_move:
            # if not the first move in the sequance, add this move at the last of the linked list
            p = before_move
            while p.children is not None:
                p = p.children
            p.childran = move

        else:
            before_move = move

        first_selection = None
        # if has more jumps possible, dont change color to play
        if not hasJumped or hasJumped and not board.has_more_jumps(second_selection):
            is_white_to_play = not is_white_to_play
            hasJumped = False
            board.add_move_to_history(before_move)
            before_move = None
            print(board.get_move_history())

        second_selection = None

    return first_selection, second_selection, is_white_to_play, hasJumped, before_move


def main():
    mouse_x = 0  # store x cordinate of mouse event
    mouse_y = 0  # y cordinate
    board = Board()
    first_selection = None
    second_selection = None
    is_white_to_play = True
    hasJumped = False
    run = True
    timer = 0
    before_move = None
    while run:

        timer += fps_clock.tick_busy_loop(
            30
        )  # Adjust the frame rate as needed (30 frames per second in this example)

        # Check if one second has passed
        if timer >= 2000:  # 1000 milliseconds = 1 second
            # print(board.every_move_for_player(EColor.white, hasJumped=False))
            timer = 0

        board.draw()
        mouse_clicked = False
        # who plays now
        # can you jump
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                run = False
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_x, mouse_y = event.pos
                mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k:  # Check if 'K' key is pressed
                    board.undo_move()
                    is_white_to_play = not is_white_to_play
        mouse_on_tile = board.get_tile_at_pixel(mouse_x, mouse_y)
        if mouse_on_tile:
            mouse_on_pawn = board.get_pawn_from_tile[mouse_on_tile]

        if mouse_on_tile:
            if mouse_on_pawn and mouse_on_pawn.color == (
                EColor.white if is_white_to_play else EColor.black
            ):
                board.show_avilable_moves(mouse_on_tile, hasJumped)
            if (
                mouse_clicked
                and mouse_on_pawn
                and mouse_on_pawn.color
                == (EColor.white if is_white_to_play else EColor.black)
            ):
                (
                    first_selection,
                    second_selection,
                    is_white_to_play,
                    hasJumped,
                    before_move,
                ) = handle_mouse_click(
                    board,
                    mouse_on_tile,
                    first_selection,
                    second_selection,
                    is_white_to_play,
                    hasJumped,
                    before_move,
                )

            elif mouse_clicked:
                (
                    first_selection,
                    second_selection,
                    is_white_to_play,
                    hasJumped,
                    before_move,
                ) = handle_mouse_click(
                    board,
                    mouse_on_tile,
                    first_selection,
                    second_selection,
                    is_white_to_play,
                    hasJumped,
                    before_move,
                )

        if first_selection:
            board.show_avilable_moves(first_selection, hasJumped)
            first_selection.glow_blue()

        pygame.display.update()


if __name__ == "__main__":
    main()
