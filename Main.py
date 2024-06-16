import pygame, sys
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import io
import threading

from Board import Board
from DBManager import DBManager
from Enums import Eplayers, Ecolors
from Network import Network
from CheckersAI import CheckersAI
from Config import *


MOVE_LOCK = threading.Lock()
FPS_CLOCK = pygame.time.Clock()

is_white_to_play = True
player_color = True

if GAME_ONLINE:
    network = Network()

game_over = False

pygame.init()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Checkers_Analyzer")


def handle_mouse_click(
    board: Board,
    clicked_tile,
    first_selection,
    is_white_to_play,
    has_jumped,
    before_move,
):
    x, y = clicked_tile.get_location()
    if first_selection is None:
        # Select a piece if it belongs to the current player
        if board.get_piece_at_tile((x, y)) and board.get_piece_at_tile(
            (x, y)
        ).get_color() == (Eplayers.white if is_white_to_play else Eplayers.black):
            first_selection = (x, y)
    else:
        # Attempt to move the selected piece
        piece = board.get_piece_at_tile(first_selection)
        move_exists = False
        if piece:
            moves_possible, jumps_possible = board.every_move_possible_for_piece(
                piece, has_jumped
            )
            possible_moves = jumps_possible if jumps_possible else moves_possible

            for move in possible_moves:
                if move.get_to_tile() == (x, y):
                    move_exists = True
                    break

            if move_exists:
                move, has_jumped = board.move(first_selection, (x, y), has_jumped)

                if before_move:
                    last_node = before_move
                    while last_node.get_children():
                        last_node = last_node.get_children()[
                            0
                        ]  # Get to the end of the sequence
                    last_node.add_child(move)  # Append the new move to the sequence
                else:
                    before_move = move

                if not has_jumped or not board._has_more_jumps((x, y)):
                    print("has jumped", has_jumped)
                    print("has more jumps", board._has_more_jumps((x, y)))
                    is_white_to_play = not is_white_to_play
                    board.switch_player()

                    board.add_move_to_history(before_move)
                    if GAME_ONLINE:
                        print("sending move", before_move)
                        simplified_move_node = Board.serialize_move_node(before_move)
                        network.send(simplified_move_node)

                    has_jumped = None
                    before_move = None

        first_selection = None

    return first_selection, is_white_to_play, has_jumped, before_move


def display_analysis(screen, game_analysis, history, analysis_color):
    def handle_key_events():
        nonlocal move_index, display_state, analysis_board, show_explanation, sequence_index
        nonlocal is_add_to_sequence, move_to_show, best_move, current_move, is_played_move_best

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # If the user closes the window, the program will close
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # If the user presses escape, the analyze screen will close
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    # If the user presses the left arrow key, the game will go back one move
                    if -1 <= move_index < len(history):
                        if not (
                            display_state == "show_played_move_sequence"
                            or display_state == "show_best_move_sequence"
                        ):
                            move_index = max(-1, move_index - 1)
                            analysis_board.undo_move()
                            analysis_board.undo_move()
                            display_state = "start"

                elif event.key == pygame.K_RIGHT:
                    # If the user presses the right arrow key, the game will go forward one move
                    if (
                        -1 <= move_index < len(history) - 1
                    ):  # Checks that we don't go beyond the last move

                        # if the user watches sequenses, dont change the move index
                        if not (
                            display_state == "show_best_move_sequence"
                            or display_state == "show_played_move_sequence"
                        ):
                            move_index += 1

                        if display_state == "show_played_move_sequence":
                            sequence_index += 1

                        display_state = "start"

                elif event.key == pygame.K_p or event.key == pygame.K_o:
                    # If the user presses P or O key, the game will show the played move sequence

                    # Show the sequence only if the current move is the analysis color

                    if (
                        display_state != "show_best_move_sequence"
                        and move_index != -1
                        and current_move.get_piece().get_color() == analysis_color
                        and not display_state == "played_move_best"
                    ):
                        best_move = None
                        if display_state == "played_move_best":
                            is_played_move_best = True

                        # If the user presses the P key, the game will show the next move in the played move sequence
                        if event.key == pygame.K_p:
                            sequence_index += 1
                            is_add_to_sequence = True
                        # If the user presses the O key, the game will show the previus move in the played move sequence
                        else:
                            if sequence_index == 0:
                                analysis_board.undo_move()
                                display_state = "start"
                                continue
                            elif sequence_index == 1:
                                analysis_board.undo_move()
                                analysis_board.undo_move()
                                display_state = "start"
                                continue
                            sequence_index -= 1
                            is_add_to_sequence = False

                        display_state = "show_played_move_sequence"

                elif event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                    # If the user presses the UP or DOWN key, the game will show the best move sequence

                    # Show the sequence only if the current move is the analysis color
                    if (
                        display_state != "show_played_move_sequence"
                        and move_index != -1
                        and current_move.get_piece().get_color() == analysis_color
                    ):
                        move_to_show = None
                        if display_state == "played_move_best":
                            is_played_move_best = True

                        if event.key == pygame.K_UP:
                            # If the user presses the UP key, the game will show the next move in the best move sequence
                            if display_state != "show_best_move_sequence":
                                analysis_board.undo_move()

                            sequence_index += 1
                            is_add_to_sequence = True
                        else:
                            # If the user presses the DOWN key, the game will show the the previus move in the best move sequence
                            if sequence_index == 0:
                                analysis_board.undo_move()
                                display_state = "start"
                                continue
                            elif sequence_index == 1:
                                # analysis_board.undo_move()
                                display_state = "start"
                                continue
                            sequence_index -= 1
                            is_add_to_sequence = False
                        display_state = "show_best_move_sequence"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the click is within the rect of the question mark icon
                if question_mark_rect.collidepoint(event.pos):
                    show_explanation = not show_explanation
        return True

    running = True
    analysis_board = Board(screen)  # Assuming this is your custom Board class
    move_index = -1
    sequence_index = 0
    is_add_to_sequence = None
    mouse_clicked, mouse_x, mouse_y, show_explanation = False, 0, 0, False

    question_mark_rect = QUESTION_MARK.get_rect()

    display_state = "start"  # Can be 'start', 'played_move', 'best_move'

    screen.fill((255, 255, 255))
    analysis_board.draw(screen)

    screen.blit(QUESTION_MARK, question_mark_rect)
    pygame.display.update()

    move_to_show = None
    is_played_move_best = False
    best_move = None

    while running:
        print(sequence_index)
        screen.fill((255, 255, 255))
        analysis_board.draw(screen)
        if not handle_key_events():
            running = False
            break

        if move_index == -1:
            analysis_board.draw(screen)
        elif 0 <= move_index < len(history):
            current_move, _ = history[move_index]

            if display_state == "start":

                # if sequence_index > 0, undo the moves to the start of the sequence
                if sequence_index > 0:
                    for i in range(sequence_index):
                        analysis_board.undo_move()

                sequence_index = 0

                is_played_move_best = False
                # If the current move is the analysis color, show the best move
                if current_move.get_piece().get_color() == analysis_color:
                    (
                        played_move,
                        move_score,
                        best_move_score,
                        best_sequence,
                        played_sequence,
                    ) = game_analysis[int(move_index / 2)]

                    best_move = best_sequence[0]

                    analysis_board.apply_move(played_move, True)
                    analysis_board.draw(screen)

                    display_state = "best_move"

                    if best_sequence[0].__eq__(played_move):
                        display_state = "played_move_best"

                    move_to_show = played_move
                # Current move is not the analysis color, show the move made
                else:
                    best_move = None
                    analysis_board.apply_move(current_move, True)
                    analysis_board.draw(screen)
                    display_state = "played_move"
                    move_to_show = current_move

            elif display_state == "show_played_move_sequence":
                if sequence_index == len(played_sequence):
                    # If the sequence is over, go back to the start
                    display_state = "start"
                    is_add_to_sequence = None
                    continue

                move_to_show = played_sequence[sequence_index]

                if is_add_to_sequence is True:
                    analysis_board.apply_move(move_to_show, True)
                    is_add_to_sequence = None

                elif is_add_to_sequence is False and sequence_index > 0:
                    if sequence_index != 0:
                        is_add_to_sequence = None
                        analysis_board.undo_move()

                analysis_board.draw(screen)

            elif display_state == "show_best_move_sequence":

                if sequence_index == len(played_sequence) + 1:
                    display_state = "start"
                    sequence_index -= 1
                    continue

                if is_played_move_best:
                    move = played_sequence[sequence_index - 1]
                else:
                    move = best_sequence[sequence_index - 1]

                best_move = move

                if is_add_to_sequence is True:
                    analysis_board.apply_move(move, True)
                    is_add_to_sequence = None

                elif is_add_to_sequence is False and sequence_index > 0:
                    is_add_to_sequence = None
                    analysis_board.undo_move()

                analysis_board.draw(screen)

            # Show the move that was made
            if display_state != "start" and move_to_show is not None:

                analysis_board.show_move(
                    move_to_show,
                    screen,
                    move_to_show.get_piece().get_color() == analysis_color,
                    "played_move",
                )
            # Show the best move if it is available
            if best_move is not None and display_state != "start":
                analysis_board.show_move(
                    best_move,
                    screen,
                    True,
                    display_state,
                )

        # Show the explanation if the user has clicked the question mark icon
        if show_explanation:
            screen.blit(EXPLAIN, (0, 0))

        # update the screen
        screen.blit(QUESTION_MARK, question_mark_rect)
        pygame.display.update()
        FPS_CLOCK.tick(FPS)


def receive_moves_forever(board, network):
    global player_color
    global is_white_to_play
    global MOVE_LOCK
    global game_over
    with MOVE_LOCK:
        while not game_over:
            try:
                msg = network.receive()

                if msg:
                    print("received move", player_color)
                    if msg == DISCONNECT_MSG:
                        print("Opponent has disconnected.")
                        if board.is_game_over() is None:
                            print(not player_color, "resigns.")
                            color = Eplayers.black if player_color else Eplayers.white
                            board.resign(color)  # Opponent resigns
                        print("ther WINNER is ", board.get_winner())

                        game_over = True
                        network.send(DISCONNECT_ACK_MSG)  # Acknowledge disconnect
                        network.shutdown()
                        break
                    # Process normal moves
                    move = board.unserialize_move_node(msg)
                    board.apply_move(move, True)
                    if board.is_game_over() is not None:
                        game_over = True
                    is_white_to_play = not is_white_to_play
            except Exception as e:
                print(f"Error receiving move: {e}")


def get_graphs(matches, screen):
    # create graphs for the win rate and game score

    player_data = {
        "wins": 0,
        "games": 0,
        "win_rates": [],
        "game_scores": [],
    }
    print("matches", matches)
    # update the player data with the matches
    for name, game_index, win, game_score in matches:
        player_data["games"] += 1
        if win:
            player_data["wins"] += 1

        current_win_rate = player_data["wins"] / player_data["games"]
        player_data["win_rates"].append(current_win_rate)
        player_data["game_scores"].append(game_score)

    def plot_graph(data_key, y_label, title):
        # plot the graph
        fig, ax = plt.subplots()
        ax.plot(range(1, player_data["games"] + 1), player_data[data_key])
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xlabel("Game Number")
        ax.set_ylabel(y_label)
        ax.set_title(title)
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        plt.close(fig)
        buffer.seek(0)
        return buffer

    # get the buffers for the graphs
    win_rate_buffer = plot_graph("win_rates", "Win Rate", "Win Rate Over Time")
    game_score_buffer = plot_graph("game_scores", "Game Score", "Game Score Over Time")

    def load_pygame_image(buffer):
        # load the image to pygame
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
    global game_over

    receive_thread = None
    first_selection = None

    if GAME_ONLINE:
        player_color = True if network.connect() == "True" else False

    has_jumped = None
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

    if GAME_ONLINE:
        # Start the thread to receive moves
        receive_thread = threading.Thread(
            target=receive_moves_forever, args=(board, network)
        )
        receive_thread.daemon = True
        receive_thread.start()

    while run:
        board.draw(screen)
        mouse_clicked = False

        # Check for events- user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # If the user closes the window, the game will end
                game_over = True
                if GAME_ONLINE:
                    network.close()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                # Get the x and y cordinate of the mouse event
                mouse_x, mouse_y = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                # Get the x and y cordinate of the mouse event
                mouse_x, mouse_y = event.pos
                mouse_clicked = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    best_move = checkers_ai.find_best_move(board)
                if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                    # If the user presses enter or escape

                    if not ask_for_name and not showing_graph:
                        # if the the user in the game and presses enter close the game. if the game is not over, resign
                        ask_for_name = True
                        if not game_over:
                            board.resign(
                                Eplayers.white if player_color else Eplayers.black
                            )
                            print("resigned")
                        game_over = True
                        if GAME_ONLINE:
                            network.close()
                            print("network closed")
                    elif ask_for_name and text != "":
                        # submit the name and start the analysis
                        analysis_started = True
                        ask_for_name = False
                elif event.key == pygame.K_RIGHT and showing_graph:
                    # show the second graph
                    show_first = True
                elif event.key == pygame.K_LEFT and showing_graph:
                    # show the first graph
                    show_first = False
                elif event.key == pygame.K_BACKSPACE and ask_for_name:
                    # remove the last character from the name
                    text = text[:-1]
                elif ask_for_name:
                    text += event.unicode

        mouse_on_tile = board.get_tile_at_pixel(mouse_x, mouse_y)

        if (
            GAME_ONLINE
            and is_white_to_play == player_color
            and not game_over
            or not GAME_ONLINE
            and not game_over
        ):
            # showing the last move with green glow
            if len(board.get_history()) > 0:
                last_move = board.get_history()[-1]
                board.show_move(last_move[0], screen, True, "played_move")

            # if the player's mouse if on a tile
            if mouse_on_tile:
                x, y = mouse_on_tile.get_location()
                mouse_on_pawn = board.get_piece_at_tile((x, y))
                if mouse_on_pawn and mouse_on_pawn.get_color() == (
                    Eplayers.white if is_white_to_play else Eplayers.black
                ):
                    # if the player's mouse is on a pawn, show the available moves
                    board.show_available_moves(
                        mouse_on_tile.get_location(), has_jumped, screen
                    )

                if mouse_clicked:
                    (
                        first_selection,
                        is_white_to_play,
                        has_jumped,
                        before_move,
                    ) = handle_mouse_click(
                        board,
                        mouse_on_tile,
                        first_selection,
                        is_white_to_play,
                        has_jumped,
                        before_move,
                    )

                # show the available moves for the selected pawn
                if first_selection:
                    board.show_available_moves(first_selection, has_jumped, screen)
                    x, y = first_selection
                    board.get_tile_from_location(x, y).glow(screen, Ecolors.blue)

                # if the game is over, close the game
                if board.is_game_over() is not None:
                    pygame.display.update()
                    game_over = True
                    if GAME_ONLINE:
                        network.close()

        if game_over and not ask_for_name and not showing_graph:
            # If the game is over and the user has not entered a name, show the game result
            color = Eplayers.white if player_color else Eplayers.black
            if board.get_winner() == color:
                screen.blit(
                    YOU_WIN,
                    (
                        WINDOW_SIZE / 2 - YOU_WIN.get_width() / 2,
                        WINDOW_SIZE / 2 - YOU_WIN.get_height() / 2,
                    ),
                )
            elif board.get_winner() != color:
                screen.blit(
                    YOU_LOSE,
                    (
                        WINDOW_SIZE / 2 - YOU_LOSE.get_width() / 2,
                        WINDOW_SIZE / 2 - YOU_LOSE.get_height() / 2,
                    ),
                )

        if ask_for_name:
            screen.blit(BACKROUND, (0, 0))
            font = pygame.font.Font(None, WINDOW_SIZE // 20)

            txt_surface = font.render(text, True, GREY)

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

            color = Eplayers.white if player_color else Eplayers.black

            screen.blit(BACKROUND, (0, 0))
            please_wait_text = font.render("Analyzing... Please wait", True, BLACK)
            please_wait_text_y = int(WINDOW_SIZE * 0.07)
            screen.blit(
                please_wait_text,
                ((WINDOW_SIZE - please_wait_text.get_width()) // 2, please_wait_text_y),
            )

            pygame.display.flip()
            pygame.display.update()

            winner = board.get_winner()
            print("winner1", winner)

            game_analysis, average_score = checkers_ai.analyze_game(history, color)
            print("average score", average_score)

            if winner == Eplayers.white:
                DBM.add_game(text, True if player_color else False, average_score)
            elif winner == Eplayers.black:
                DBM.add_game(text, False if player_color else True, average_score)
            elif winner == "draw":
                DBM.add_game(text, None, average_score)

            display_analysis(screen, game_analysis, history, color)
            analysis_started = False
            showing_graph = True

        if showing_graph:
            if not graph_created:
                print("getting matches for ", text)
                matches = DBM.get_matches_for_name(text)
                print("matches \n", matches)
                graphs = get_graphs(matches, screen)
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
