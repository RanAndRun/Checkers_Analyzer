from Main import window_width, window_height, board_size
import pygame
from Main import screen
import os


class Tile:
    tile_width, tile_height = window_width // board_size, window_height // board_size

    def __init__ (self, x, y, x_point, y_point):
        self.row = y
        self.column = x
        self.x_point = x_point
        self.y_point = y_point
        self.tile_rect = pygame.Rect(x_point, y_point, self.tile_width, self.tile_height)


    def get_location (self):
        return self.column, self.row

    def glow_yellow(self):
        pygame.draw.rect(screen, (255, 255, 0), self.tile_rect, 5)
        #TODO make it glow for the whole time the first selection is no None

    def glow_blue(self):
        pygame.draw.rect(screen, (31, 81, 255), self.tile_rect, 5)
