import pygame, sys
from Board import *
from time import sleep
from Enums import Eplayers, Ecolors
from BoardNode import BoardNode
from Network import Network
import threading
from DBManager import DBManager
import os

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
player_color = True
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
            Eplayers.white if is_white_to_play else Eplayers.black
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
        global running
        for event in pygame.event.get():
            if (
                event.type == pygame.QUIT
                or event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):
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
                    analysis_board.show_move_made(played_move, screen)
                else:
                    best_move = None
                    analysis_board.apply_move(current_move)
                    display_state = "played_move"
                    analysis_board.draw(screen)
                    analysis_board.show_move_made(current_move, screen, False)
            print("best move", best_move)
            if best_move is not None:
                print("best move children", best_move.children)
            if is_played_move_best_move:
                # show the played move in yellow
                analysis_board.show_move_made(current_move, screen, True)
            elif best_move is not None:
                analysis_board.show_better_move(best_move, screen)

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


import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import io


def show_win_rate_graph(game_results):
    global screen
    if not isinstance(game_results, list) or not game_results:
        print("game_results must be a non-empty list.")
        return

    if not all(
        isinstance(record, (list, tuple)) and len(record) == 3
        for record in game_results
    ):
        print(
            "Each element of game_results must be a tuple or list with three elements."
        )
        return

    # Dictionary to keep track of each player's wins, games, and cumulative win rate
    players_data = {}

    for name, game_index, win in game_results:
        if name not in players_data:
            players_data[name] = {"wins": 0, "games": 0, "win_rates": []}

        players_data[name]["games"] += 1
        if win:
            players_data[name]["wins"] += 1

        current_win_rate = players_data[name]["wins"] / players_data[name]["games"]
        players_data[name]["win_rates"].append(current_win_rate)

    # Plotting
    fig, ax = plt.subplots()

    for name, data in players_data.items():
        ax.plot(range(1, len(data["win_rates"]) + 1), data["win_rates"], label=name)

    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylim(0, 1.2)  # Set the limits for the y-axis
    ax.set_xlabel("Game Number")
    ax.set_ylabel("Win Rate")
    ax.set_title("Win Rate Over Time")
    plt.legend()
    # plt.show()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    plt.close(fig)  # Close the figure to free memory
    buffer.seek(0)  # Rewind the buffer to the beginning

    # Load the image into Pygame and blit it to the screen
    plot_image = pygame.image.load(buffer)
    plot_rect = plot_image.get_rect()

    # Resize the image to fit the pygame screen
    plot_image = pygame.transform.scale(plot_image, (window_width, window_height))
    screen.blit(plot_image, plot_rect)
    pygame.display.flip()  # Update the screen

    # Clear the buffer
    buffer.close()


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

    # Declare global to modify the global variable
    print(player_color)
    hasJumped = None
    run = True
    text = ""
    mouse_x = 0  # store x cordinate of mouse event
    mouse_y = 0  # y cordinate
    board = Board(screen)
    checkers_ai = CheckersAI(board)

    current_directory = os.getcwd()
    db_path = os.path.join(current_directory, "checkers.db")
    DBM = DBManager(db_path)
    timer = 0
    before_move = None
    analysis_started = False
    ask_for_name = False
    showing_graph = False

    while run:

        timer += fps_clock.tick_busy_loop(
            30
        )  # Adjust the frame rate as needed (30 frames per second in this example)

        board.draw(screen)
        mouse_clicked = False

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

                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:

                    if not ask_for_name and not showing_graph:
                        ask_for_name = True

                    elif not analysis_started and not showing_graph:
                        winner = board.is_game_over()
                        if winner == Eplayers.white:
                            DBM.add_player(text, True if player_color else False)
                        elif winner == Eplayers.black:
                            DBM.add_player(text, False if player_color else True)
                        analysis_started = True
                        ask_for_name = False
                elif event.key == pygame.K_k:
                    board.undo_move()
                    board.switch_player()
                    is_white_to_play = not is_white_to_play
                else:
                    text += event.unicode if ask_for_name else ""
        mouse_on_tile = board.get_tile_at_pixel(mouse_x, mouse_y)

        if game_online:
            receive_thread = threading.Thread(
                target=receive_moves_forever, args=(board, network)
            )
            receive_thread.daemon = (
                True  # The thread will close when the main program exits
            )
            receive_thread.start()

        if game_online and is_white_to_play == player_color:
            if len(board.get_history()) > 0:
                last_move = board.get_history()[-1]
                last_move_from_tile_x, last_move_from_tile_y = last_move[0].from_tile
                last_move_to_tile_x, last_move_to_tile_y = last_move[0].to_tile
                board.tiles[last_move_from_tile_y][last_move_from_tile_x].glow(
                    screen, Ecolors.green
                )
                board.tiles[last_move_to_tile_y][last_move_to_tile_x].glow(
                    screen, Ecolors.green
                )
            if mouse_on_tile:
                x, y = mouse_on_tile.get_location()
                mouse_on_pawn = board.pieces_matrix[y][x]
                if mouse_on_pawn and mouse_on_pawn.color == (
                    Eplayers.white if is_white_to_play else Eplayers.black
                ):
                    board.show_avilable_moves(
                        mouse_on_tile.get_location(), hasJumped, screen
                    )
                if (
                    mouse_clicked
                    and mouse_on_pawn
                    and mouse_on_pawn.color
                    == (Eplayers.white if is_white_to_play else Eplayers.black)
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
                board.tiles[y][x].glow(screen, Ecolors.blue)

        if not game_online:
            if len(board.get_history()) > 0:
                last_move = board.get_history()[-1]
                last_move_from_tile_x, last_move_from_tile_y = last_move[0].from_tile
                last_move_to_tile_x, last_move_to_tile_y = last_move[0].to_tile
                board.tiles[last_move_from_tile_y][last_move_from_tile_x].glow(
                    screen, Ecolors.green
                )
                board.tiles[last_move_to_tile_y][last_move_to_tile_x].glow(
                    screen, Ecolors.green
                )
            if mouse_on_tile:
                x, y = mouse_on_tile.get_location()
                mouse_on_pawn = board.pieces_matrix[y][x]
                if mouse_on_pawn and mouse_on_pawn.color == (
                    Eplayers.white if is_white_to_play else Eplayers.black
                ):
                    board.show_avilable_moves(
                        mouse_on_tile.get_location(), hasJumped, screen
                    )
                if (
                    mouse_clicked
                    and mouse_on_pawn
                    and mouse_on_pawn.color
                    == (Eplayers.white if is_white_to_play else Eplayers.black)
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
                board.tiles[y][x].glow(screen, Ecolors.blue)
        # Assuming you have a lock defined somewhere in your code

        if ask_for_name:
            color_inactive = pygame.Color("lightskyblue3")
            color_active = pygame.Color("dodgerblue2")
            color = color_inactive
            active = False

            font = pygame.font.Font(None, 36)
            input_box = pygame.Rect(100, 75, 140, 32)
            screen.fill((255, 255, 255))
            input_box = pygame.Rect(100, 75, 140, 32)
            txt_surface = font.render(text, True, color)
            input_box.w = window_width
            screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(screen, color, input_box, 2)
            pygame.display.flip()

        if analysis_started:
            history = board.get_history()
            if player_color is not None:
                color = Eplayers.white if player_color else Eplayers.black
            else:
                print("player color is None")
                color = Eplayers.white

            print("analyzing with player color", color)
            game_analysis = checkers_ai.analyze_game(history, color)

            display_analysis(screen, game_analysis, history, color)
            analysis_started = False
            showing_graph = True

        if showing_graph:
            matches = DBM.get_matches_for_name(text)
            show_win_rate_graph(matches)

        pygame.display.update()


if __name__ == "__main__":
    main()
