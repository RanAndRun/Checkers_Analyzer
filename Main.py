import pygame, sys
import os
from Board import *
from time import sleep
from Enums import EColor
from BoardNode import BoardNode
from Network import Network
import math

from CheckersAI import CheckersAI
from config import window_width, window_height, board_size


FPS = 30
fps_clock = pygame.time.Clock()

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

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
    x, y = tile.get_location()
    if first_selection is None:
        if board.pieces_matrix[y][x] and board.pieces_matrix[y][x].color == (
            EColor.white if is_white_to_play else EColor.black
        ):
            first_selection = (x, y)
    elif board.pieces_matrix[y][x] is None:
        second_selection = (x, y)

        move, hasJumped = board.move(
            first_selection, second_selection, hasJumped, screen
        )

        if before_move:
            # Find the last node in the existing move sequence
            last_node = before_move
            while last_node.children:
                last_node = last_node.children[
                    0
                ]  # Assuming each node has at most one child

            # Link the new move to the existing sequence
            last_node.add_child(move)
        else:
            before_move = move

        first_selection = None
        # if has more jumps possible, don't change color to play
        if not hasJumped or hasJumped and not board.has_more_jumps(second_selection):
            is_white_to_play = not is_white_to_play
            board.switch_player()
            hasJumped = None
            board.add_move_to_history(before_move)
            before_move = None

        second_selection = None

    return first_selection, second_selection, is_white_to_play, hasJumped, before_move


def draw_arrow(screen, from_coordinates, to_coordinates):
    pygame.draw.line(screen, BLACK, from_coordinates, to_coordinates, 2)
    # Calculate angle between the line and x-axis
    angle = math.atan2(
        to_coordinates[1] - from_coordinates[1], to_coordinates[0] - from_coordinates[0]
    )
    # Draw arrow head
    pygame.draw.polygon(
        screen,
        RED,
        [
            (
                to_coordinates[0] - 10 * math.cos(angle - math.pi / 6),
                to_coordinates[1] - 10 * math.sin(angle - math.pi / 6),
            ),
            (to_coordinates[0], to_coordinates[1]),
            (
                to_coordinates[0] - 10 * math.cos(angle + math.pi / 6),
                to_coordinates[1] - 10 * math.sin(angle + math.pi / 6),
            ),
        ],
    )


def display_analysis(screen, game_analysis, history, analysis_color):

    def update():
        screen.fill((255, 255, 255))
        analysis_board.draw(screen)
        pygame.display.update()

    running = True
    analysis_board = Board(screen)
    update()
    move_index = 0
    analysis_move_index = 0
    display_state = "start"  # Can be 'start', 'played_move', 'best_move'
    last_update_time = pygame.time.get_ticks()

    while running:
        current_time = pygame.time.get_ticks()
        if current_time - last_update_time > 1500 and move_index < len(
            history
        ):  # 1.5 seconds per move
            last_update_time = current_time
            if move_index < len(history):
                current_move, _ = history[move_index]

                if display_state == "start":
                    # Reset the board to the start of the current move

                    # analysis_board.set_history(history[:move_index])

                    if current_move.piece.color == analysis_color:
                        played_move, move_score, best_move_score, best_move = (
                            game_analysis[analysis_move_index]
                        )
                        analysis_move_index += 1

                        # Apply the best move for display
                        analysis_board.apply_move(best_move)
                        display_state = "best_move"
                        update()
                        sleep(1)
                    else:
                        # Apply the actual move made by the player
                        analysis_board.apply_move(current_move)
                        display_state = "played_move"

                elif display_state == "best_move":
                    # Undo the best move and apply the actual move played
                    analysis_board.undo_move()
                    update()
                    sleep(1)
                    analysis_board.apply_move(played_move)
                    display_state = "played_move"

                elif display_state == "played_move":
                    # Ready for the next move
                    move_index += 1
                    display_state = "start"

                update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    running = False


def main():
    mouse_x = 0  # store x cordinate of mouse event
    mouse_y = 0  # y cordinate
    board = Board(screen)
    checkers_ai = CheckersAI(board)
    network = Network()
    network.connect()
    first_selection = None
    second_selection = None
    is_white_to_play = True
    hasJumped = None
    run = True
    timer = 0
    before_move = None
    analysis_started = False
    while run:

        timer += fps_clock.tick_busy_loop(
            30
        )  # Adjust the frame rate as needed (30 frames per second in this example)

        # Check if one second has passed
        if timer >= 2000:  # 1000 milliseconds = 1 second
            timer = 0

        board.draw(screen)
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

                elif event.key == pygame.K_p:  # Check if 'P' key is pressed
                    best_move = checkers_ai.find_best_move(is_max=is_white_to_play)
                    print(best_move)
                    board.apply_move(best_move[0])
                    is_white_to_play = not is_white_to_play

                elif event.key == pygame.K_q:  # Check if 'Q' key is pressed
                    history = board.get_history()
                    last_move, last_board = history[-1]
                    played_move_score, best_value, best_move = checkers_ai.compare_move(
                        last_move, last_board
                    )
                    print(
                        "played move",
                        last_move,
                        "played move score",
                        played_move_score,
                        "best move score",
                        best_value,
                        "best move",
                        best_move,
                    )

                elif event.key == pygame.K_r:
                    analysis_started = True

                elif event.key == pygame.K_s:
                    print(board.pieces_matrix)
                    print(board.every_move_for_player(EColor.white))

                elif event.key == pygame.K_t:  # Check if 'P' key is pressed
                    moves_made = board.get_history()[0]
                    print(checkers_ai.find_best_move(EColor.white, None))
        mouse_on_tile = board.get_tile_at_pixel(mouse_x, mouse_y)
        if mouse_on_tile:
            x, y = mouse_on_tile.get_location()
            mouse_on_pawn = board.pieces_matrix[y][x]
            if mouse_on_pawn and mouse_on_pawn.color == (
                EColor.white if is_white_to_play else EColor.black
            ):
                board.show_avilable_moves(
                    mouse_on_tile.get_location(), hasJumped, screen
                )
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
            board.show_avilable_moves(first_selection, hasJumped, screen)
            x, y = first_selection
            board.tiles[y][x].glow_blue(screen)

        if analysis_started:
            history = board.get_history()
            color = EColor.white
            game_analysis = checkers_ai.analyze_game(history, color)

            display_analysis(screen, game_analysis, history, color)

        pygame.display.update()


if __name__ == "__main__":
    print(pygame.display.Info)
    main()
