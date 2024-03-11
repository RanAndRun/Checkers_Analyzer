import pygame, sys
import os
from Board import *
from time import sleep
from Enums import EColor
from BoardNode import BoardNode
from Network import Network
import math
import threading

from CheckersAI import CheckersAI
from config import window_width, window_height, board_size

move_lock = threading.Lock()

FPS = 30
fps_clock = pygame.time.Clock()

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

pygame.init()

screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Checkers_Analyzer")


game_online = False  # Set to True to play online

if game_online:
    network = Network()

is_white_to_play = True

move_lock = threading.Lock()


def handle_mouse_click(
    board: Board,
    clicked_tile: Tile,
    first_selection,
    is_white_to_play,
    hasJumped,
    before_move,
):
    x, y = clicked_tile.get_location()
    if first_selection is None:
        # Select a piece if it belongs to the current player
        if board.pieces_matrix[y][x] and board.pieces_matrix[y][x].color == (
            EColor.white if is_white_to_play else EColor.black
        ):
            first_selection = (x, y)
    else:
        # Attempt to move the selected piece
        piece = board.get_piece_at_tile(first_selection)
        move_exists = False
        if piece:
            moves_possible, jumps_possible = board.every_move_possible_for_piece(
                piece, hasJumped
            )
            possible_moves = jumps_possible if jumps_possible else moves_possible

            for move in possible_moves:
                if move.to_tile == (x, y):
                    move_exists = True
                    break

            if move_exists:
                move, hasJumped = board.move(first_selection, (x, y), hasJumped, screen)

                if before_move:
                    last_node = before_move
                    while last_node.children:
                        last_node = last_node.children[
                            0
                        ]  # Get to the end of the sequence
                    last_node.add_child(move)  # Append the new move to the sequence
                else:
                    before_move = move

                if not hasJumped or not board.has_more_jumps((x, y)):
                    is_white_to_play = not is_white_to_play
                    board.switch_player()
                    board.add_move_to_history(before_move)
                    if game_online:
                        simplified_move_node = Board.serialize_move_node(before_move)
                        network.send(simplified_move_node)
                    hasJumped = None
                    before_move = None

        first_selection = None

    return first_selection, is_white_to_play, hasJumped, before_move


def display_analysis(screen, game_analysis, history, analysis_color):

    def handle_key_events():
        nonlocal move_index, display_state
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_index = max(-1, move_index - 1)
                    if len(history) > move_index:
                        analysis_board.undo_move()
                        analysis_board.undo_move()

                    display_state = "start"
                elif event.key == pygame.K_RIGHT:

                    if (
                        move_index < len(history) - 1
                    ):  # Checks that we don't go beyond the last move
                        move_index += 1
                        display_state = "start"
        return True

    running = True
    analysis_board = Board(screen)  # Assuming this is your custom Board class
    move_index = -1

    display_state = "start"  # Can be 'start', 'played_move', 'best_move'
    last_update_time = pygame.time.get_ticks()
    screen.fill((255, 255, 255))
    analysis_board.draw(screen)
    pygame.display.update()

    while running:
        if not handle_key_events():
            break

        if move_index == -1:
            print("move index is -1")
            analysis_board.draw(screen)
        if 0 <= move_index < len(history):
            current_move, _ = history[move_index]

            if display_state == "start":
                if current_move.piece.color == analysis_color:
                    is_played_move_best_move = False
                    played_move, move_score, best_move_score, best_move = game_analysis[
                        int(move_index / 2)
                    ]
                    analysis_board.apply_move(played_move)
                    if best_move.__eq__(played_move):
                        is_played_move_best_move = True

                    best_move = best_move
                    display_state = "best_move"
                    analysis_board.draw(screen)
                else:
                    best_move = None
                    analysis_board.apply_move(current_move)
                    display_state = "played_move"
                    analysis_board.draw(screen)
            print("best move", best_move)
            if best_move is not None:
                analysis_board.show_better_move(
                    best_move, screen, is_played_move_best_move
                )

        pygame.display.update()


def receive_moves_forever(board, network):
    global is_white_to_play
    global move_lock
    while True:  # Continuous loop
        try:
            msg = network.receive()
            if msg:
                move = board.unserialize_move_node(msg)
                print(f"Received move: {msg}")
                board.apply_move(move)
                with move_lock:  # Ensure thread-safe access to is_white_to_play
                    is_white_to_play = not is_white_to_play
                pygame.display.update()
                print("board color", board.current_player)
                print("is white to play", is_white_to_play)
                print("color player", player_color)
        except Exception as e:
            print(f"Error receiving move: {e}")


def main():
    global is_white_to_play
    global game_online
    global move_lock
    global network
    global player_color
    receive_thread = None

    first_selection = None
    second_selection = None
    if game_online:
        player_color = network.connect()

    player_color = EColor.black
    # Declare global to modify the global variable
    print(is_white_to_play)
    hasJumped = None
    run = True

    mouse_x = 0  # store x cordinate of mouse event
    mouse_y = 0  # y cordinate
    board = Board(screen)
    checkers_ai = CheckersAI(board)

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
                    print(board.move_history)
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

        # Start the thread when initializing your game
        if game_online:
            receive_thread = threading.Thread(
                target=receive_moves_forever, args=(board, network)
            )
            receive_thread.daemon = (
                True  # The thread will close when the main program exits
            )
            receive_thread.start()

        if game_online and is_white_to_play == player_color:
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
                        is_white_to_play,
                        hasJumped,
                        before_move,
                    ) = handle_mouse_click(
                        board,
                        mouse_on_tile,
                        first_selection,
                        is_white_to_play,
                        hasJumped,
                        before_move,
                    )

                elif mouse_clicked:
                    (
                        first_selection,
                        is_white_to_play,
                        hasJumped,
                        before_move,
                    ) = handle_mouse_click(
                        board,
                        mouse_on_tile,
                        first_selection,
                        is_white_to_play,
                        hasJumped,
                        before_move,
                    )

            if first_selection:
                board.show_avilable_moves(first_selection, hasJumped, screen)
                x, y = first_selection
                board.tiles[y][x].glow_blue(screen)

        if not game_online:
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
                        is_white_to_play,
                        hasJumped,
                        before_move,
                    ) = handle_mouse_click(
                        board,
                        mouse_on_tile,
                        first_selection,
                        is_white_to_play,
                        hasJumped,
                        before_move,
                    )

                elif mouse_clicked:
                    (
                        first_selection,
                        is_white_to_play,
                        hasJumped,
                        before_move,
                    ) = handle_mouse_click(
                        board,
                        mouse_on_tile,
                        first_selection,
                        is_white_to_play,
                        hasJumped,
                        before_move,
                    )

            if first_selection:
                board.show_avilable_moves(first_selection, hasJumped, screen)
                x, y = first_selection
                board.tiles[y][x].glow_blue(screen)
        # Assuming you have a lock defined somewhere in your code

        if analysis_started:
            history = board.get_history()
            color = player_color
            game_analysis = checkers_ai.analyze_game(history, color)

            display_analysis(screen, game_analysis, history, color)

        pygame.display.update()


if __name__ == "__main__":
    print(pygame.display.Info)
    main()
