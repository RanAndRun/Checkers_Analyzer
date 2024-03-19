import pygame, sys
from Board import *
from time import sleep
from Enums import Eplayers, Ecolors
from BoardNode import BoardNode
from Network import Network
import threading
from DBManager import DBManager
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import io
from CheckersAI import CheckersAI
from config import *


MOVE_LOCK = threading.Lock()

FPS = 30
FPS_CLOCK = pygame.time.Clock()

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

is_white_to_play = True
player_color = True

if GAME_ONLINE:
    network = Network()


pygame.init()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Checkers_Analyzer")

explain = os.path.join("assets", "scroll.png")
explain = pygame.image.load(explain)
explain = pygame.transform.scale(explain, SIZE)

question_mark = os.path.join("assets", "questionMark.png")
question_mark = pygame.image.load(question_mark)
question_mark = pygame.transform.scale(question_mark, (TILE_SIZE, TILE_SIZE))

backround = os.path.join("assets", "backround.jpg")
backround = pygame.image.load(backround)
backround = pygame.transform.scale(backround, SIZE)


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
                    if GAME_ONLINE:
                        simplified_move_node = Board.serialize_move_node(before_move)
                        network.send(simplified_move_node)
                    hasJumped = None
                    before_move = None

        first_selection = None

    return first_selection, is_white_to_play, hasJumped, before_move


def display_analysis(screen, game_analysis, history, analysis_color):
    def handle_key_events():
        nonlocal move_index, display_state, mouse_clicked, mouse_x, mouse_y, analysis_board, show_explanation
        global running
        global explain
        global question_mark
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the click is within the rect of the question mark icon
                if question_mark_rect.collidepoint(event.pos):
                    show_explanation = not show_explanation
        return True

    running = True
    analysis_board = Board(screen)  # Assuming this is your custom Board class
    move_index = -1
    mouse_clicked, mouse_x, mouse_y, show_explanation = False, 0, 0, False

    question_mark_rect = question_mark.get_rect()

    display_state = "start"  # Can be 'start', 'played_move', 'best_move'

    screen.fill((255, 255, 255))
    analysis_board.draw(screen)

    screen.blit(question_mark, question_mark_rect)
    pygame.display.update()

    move_to_show = None
    is_played_move_best_move = False
    best_move = None

    while running:
        screen.fill((255, 255, 255))
        analysis_board.draw(screen)
        if not handle_key_events():
            break

        if move_index == -1:
            analysis_board.draw(screen)
        elif 0 <= move_index < len(history):
            current_move, _ = history[move_index]

            if display_state == "start":

                is_played_move_best_move = False

                if current_move.piece.color == analysis_color:
                    played_move, move_score, best_move_score, best_move = game_analysis[
                        int(move_index / 2)
                    ]
                    analysis_board.apply_move(played_move, True)
                    analysis_board.draw(screen)

                    if best_move.__eq__(played_move):
                        is_played_move_best_move = True

                    best_move = best_move
                    display_state = "best_move"

                    move_to_show = played_move
                else:
                    best_move = None
                    analysis_board.apply_move(current_move, True)
                    analysis_board.draw(screen)
                    display_state = "played_move"
                    move_to_show = current_move

        if show_explanation:
            screen.blit(explain, (0, 0))
        else:
            if move_to_show:
                analysis_board.show_move_made(
                    move_to_show,
                    screen,
                    current_move.piece.color == analysis_color,
                    is_played_move_best_move,
                )
            if is_played_move_best_move:
                # show the played move in yellow
                analysis_board.show_move_made(
                    current_move, screen, True, is_played_move_best_move
                )
            elif best_move is not None:
                analysis_board.show_better_move(best_move, screen)

        screen.blit(question_mark, question_mark_rect)
        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def receive_moves_forever(board, network):
    global is_white_to_play
    global MOVE_LOCK
    while True:  # Continuous loop
        try:
            msg = network.receive()
            if msg:
                if msg == DISCONNECT_MSG:
                    print("Opponent has disconnected.")
                    break
                print(f"Received move: {msg}")
                move = board.unserialize_move_node(msg)
                print(f"Received move: {msg}")
                board.apply_move(move, True)
                with MOVE_LOCK:  # Ensure thread-safe access to is_white_to_play
                    is_white_to_play = not is_white_to_play
                pygame.display.update()
        except Exception as e:
            print(f"Error receiving move: {e}")


def get_graphs(game_results):
    global screen
    if not isinstance(game_results, list) or not game_results:
        pygame.quit()
        sys.exit()

    # Dictionary to keep track of each player's wins, games, and cumulative win rate
    players_data = {}

    for name, game_index, win, game_score in game_results:
        if name not in players_data:
            players_data[name] = {
                "wins": 0,
                "games": 0,
                "win_rates": [],
                "game_scores": [],
            }

        players_data[name]["games"] += 1
        if win:
            players_data[name]["wins"] += 1

        current_win_rate = players_data[name]["wins"] / players_data[name]["games"]
        players_data[name]["win_rates"].append(current_win_rate)
        players_data[name]["game_scores"].append(game_score)

    def plot_graph(data_key, y_label, title):
        fig, ax = plt.subplots()
        for name, data in players_data.items():
            ax.plot(range(1, len(data[data_key]) + 1), data[data_key], label=name)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xlabel("Game Number")
        ax.set_ylabel(y_label)
        ax.set_title(title)
        plt.legend()
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        plt.close(fig)
        buffer.seek(0)
        return buffer

    win_rate_buffer = plot_graph("win_rates", "Win Rate", "Win Rate Over Time")
    game_score_buffer = plot_graph("game_scores", "Game Score", "Game Score Over Time")

    def load_pygame_image(buffer):
        image = pygame.image.load(buffer)
        rect = image.get_rect()
        image = pygame.transform.scale(image, SIZE)
        return image, rect

    return load_pygame_image(win_rate_buffer), load_pygame_image(game_score_buffer)


def main():
    global is_white_to_play
    global GAME_ONLINE
    global MOVE_LOCK
    global network
    global player_color

    receive_thread = None
    first_selection = None
    second_selection = None

    if GAME_ONLINE:
        player_color = True if network.connect() == "True" else False

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

    before_move = None
    analysis_started = False
    ask_for_name = False
    showing_graph = False
    graph_created = False
    show_first = True

    while run:

        board.draw(screen)
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if GAME_ONLINE:
                    network.close()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_x, mouse_y = event.pos
                mouse_clicked = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:

                    if ask_for_name and text == "":
                        continue
                    if not ask_for_name and not showing_graph:
                        ask_for_name = True

                    elif not analysis_started and not showing_graph:

                        analysis_started = True
                        ask_for_name = False
                elif event.key == pygame.K_RIGHT:
                    show_first = True
                elif event.key == pygame.K_LEFT:
                    show_first = False
                else:
                    text += event.unicode if ask_for_name else ""

        mouse_on_tile = board.get_tile_at_pixel(mouse_x, mouse_y)

        if GAME_ONLINE:
            # Check if the thread is None or not alive
            if receive_thread is None or not receive_thread.is_alive() and network.id:
                receive_thread = threading.Thread(
                    target=receive_moves_forever, args=(board, network)
                )
                receive_thread.daemon = True
                receive_thread.start()

        if GAME_ONLINE and is_white_to_play == player_color:
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

        if not GAME_ONLINE:
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
            if GAME_ONLINE:
                network.close()
            color = (100, 100, 100)
            screen.blit(backround, (0, 0))
            font = pygame.font.Font(None, WINDOW_SIZE // 20)

            txt_surface = font.render(text, True, color)

            input_box_width = int(WINDOW_SIZE * 0.35)
            input_box_x = (WINDOW_SIZE - input_box_width) // 2
            input_box_y = int(WINDOW_SIZE * 0.1)

            input_box = pygame.Rect(input_box_x, input_box_y, input_box_width, 32)

            input_box.w = max(200, txt_surface.get_width() + 10)
            screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

            txt_surface = font.render(
                "Enter your name. One character minimum.", True, BLUE
            )
            prompt_position_y = int(WINDOW_SIZE * 0.05)
            screen.blit(
                txt_surface,
                ((WINDOW_SIZE - txt_surface.get_width()) // 2, prompt_position_y),
            )

            pygame.display.flip()

        if analysis_started:

            history = board.get_history()
            if player_color is not None:
                color = Eplayers.white if player_color else Eplayers.black
            else:
                print("player color is None")
                color = Eplayers.white

            print("analyzing with player color", color)
            screen.blit(backround, (0, 0))
            please_wait_text = font.render("Analyzing... Please wait", True, BLACK)
            please_wait_text_y = int(WINDOW_SIZE * 0.07)
            screen.blit(
                please_wait_text,
                ((WINDOW_SIZE - please_wait_text.get_width()) // 2, please_wait_text_y),
            )

            pygame.display.flip()
            pygame.display.update()

            game_analysis, average_score = checkers_ai.analyze_game(history, color)
            print("average score", average_score)

            winner = board.is_game_over()
            if winner == Eplayers.white:
                DBM.add_player(text, True if player_color else False, average_score)
            elif winner == Eplayers.black:
                DBM.add_player(text, False if player_color else True, average_score)

            display_analysis(screen, game_analysis, history, color)
            analysis_started = False
            showing_graph = True

        if showing_graph:
            if not graph_created:
                matches = DBM.get_matches_for_name(text)
                print("matches \n", matches)
                graphs = get_graphs(matches)
                graph_created = True
            if show_first:
                screen.blit(graphs[0][0], graphs[0][1])
                pygame.display.flip()
            else:
                screen.blit(graphs[1][0], graphs[1][1])
                pygame.display.flip()

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


if __name__ == "__main__":
    main()
