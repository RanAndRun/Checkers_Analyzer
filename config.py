# config.py
import pygame


window_width = 1200
window_height = 1200
board_size = 8
game_online = True


# def get_optimal_window_size(original_width, original_height):
#     screen_info = pygame.display.Info()
#     screen_width, screen_height = screen_info.current_w, screen_info.current_h

#     # Maintain aspect ratio
#     aspect_ratio = original_width / original_height
#     optimal_width = screen_width
#     optimal_height = int(optimal_width / aspect_ratio)

#     if optimal_height > screen_height:
#         optimal_height = screen_height
#         optimal_width = int(optimal_height * aspect_ratio)

#     return optimal_width, optimal_height


# window_width, window_height = get_optimal_window_size(window_width, window_height)
