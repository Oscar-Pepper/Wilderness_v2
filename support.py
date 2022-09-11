import math, pygame
from os import walk
from settings import *

def calc_mag(vector):
    return math.sqrt(vector.x * vector.x + vector.y * vector.y)

def calc_angle(vector):
    phi = math.atan2(vector.y, vector.x)
    output = phi * 180 / math.pi
    return output

def calc_diff(vector1, vector2):
    diff = vector2 - vector1
    if diff.x > MAP_WIDTH // 2:
        diff.x -= MAP_WIDTH
    elif diff.x < -MAP_WIDTH // 2:
        diff.x += MAP_WIDTH
    if diff.y > MAP_HEIGHT // 2:
        diff.y -= MAP_HEIGHT
    elif diff.y < -MAP_HEIGHT // 2:
        diff.y += MAP_HEIGHT
    return diff

def import_folder(path):
    surface_list = []
    for _, __, image_files in walk(path):
        for image in image_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
    return surface_list
