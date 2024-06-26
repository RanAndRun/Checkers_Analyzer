from Config import *
import pygame
from Enums import Ecolors


class Tile:

    def __init__(self, x, y, x_point, y_point):
        self.row = y
        self.column = x
        self.x_point = x_point
        self.y_point = y_point
        self.tile_rect = pygame.Rect(x_point, y_point, TILE_SIZE, TILE_SIZE)

    def get_tile_rect(self):
        return self.tile_rect

    def set_row(self, row):
        self.row = row

    def set_column(self, column):
        self.column = column

    def set_x_point(self, x_point):
        self.x_point = x_point

    def set_y_point(self, y_point):
        self.y_point = y_point

    def get_row(self):
        return self.row

    def get_column(self):
        return self.column

    def get_x_point(self):
        return self.x_point

    def get_y_point(self):
        return self.y_point

    def get_cordinates(self):
        return self.x_point, self.y_point

    def get_location(self):
        return self.column, self.row

    def get_matrix_location(self):
        return self.row, self.column

    def glow(self, screen, color):

        if color == Ecolors.yellow:
            rgb = (255, 255, 0)
        elif color == Ecolors.blue:
            rgb = (31, 81, 255)
        elif color == Ecolors.green:
            rgb = (0, 165, 80)
        elif color == Ecolors.brown:
            rgb = (165, 42, 42)
        else:
            rgb = (255, 0, 0)

        pygame.draw.rect(screen, rgb, self.tile_rect, 5)

    def glow_best_tile(self, screen, is_best):
        if not is_best:
            pygame.draw.rect(screen, (64, 224, 208, 128), self.tile_rect, 10)
        else:
            pygame.draw.rect(screen, (0, 225, 0, 128), self.tile_rect, 10)

    def glow_best_piece(self, screen):
        pygame.draw.rect(screen, (255, 215, 0, 128), self.tile_rect, 10)

    def __repr__(self):
        return f"Tile(x={self.column}, y={self.row})"

    def __deepcopy__(self, memo):
        return Tile(self.column, self.row, self.x_point, self.y_point)
