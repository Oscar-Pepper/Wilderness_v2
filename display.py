import pygame
from collections import deque
from neat_display import Neat_display
from settings import *

class Display():
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.show_display = False
        self.spacer = 10
        # graph setup
        self.graph_font = pygame.font.SysFont('arial', 10)
        self.graph_width = 240
        self.graph_height = 160
        self.graph_x = self.spacer
        self.graph_y = SCREEN_HEIGHT - self.graph_height - self.spacer
        self.graph_colour = 'black'
        self.graph_empty = True
        self.graph_update_count = 1
        self.graph_timescale = 10
        # neat display setup
        self.neat_width = 240
        self.neat_height = 160
        self.neat_x = self.spacer
        self.neat_y = SCREEN_HEIGHT - self.neat_height - self.graph_height - self.spacer * 2
        self.neat_display = Neat_display(self.neat_width, self.neat_height, (self.neat_x, self.neat_y))
        # stats font
        self.stats_font = pygame.font.SysFont('arial', 18)
        self.stats_font_bold = pygame.font.SysFont('arial', 18, bold=True)
        # organism stats setup
        self.org_stats_width = 180
        self.org_stats_height = 175
        self.org_stats_x = self.spacer
        self.org_stats_y = SCREEN_HEIGHT - self.neat_height - self.graph_height - self.org_stats_height - self.spacer * 3
        self.org_window_pos = (self.org_stats_x, self.org_stats_y)
        # global stats setup
        self.global_stats_width = 180
        self.global_stats_height = SCREEN_HEIGHT - self.neat_height - self.graph_height - self.org_stats_height - self.spacer * 5
        self.global_stats_x = self.spacer
        self.global_stats_y = self.spacer
        self.global_window_pos = (self.global_stats_x, self.global_stats_y)
        # select fittest button
        self.select_fittest_width = 120
        self.select_fittest_height = 30

    def global_stats(self, time_elapsed, species, energy_reserve):
        self.num_lines = 0
        draw_rect_alpha(self.display_surface, (255, 255, 255, 50), (self.global_stats_x, self.global_stats_y, self.global_stats_width, self.global_stats_height))
        self.draw_text(self.global_window_pos, 'Global Stats', bold=True)
        time_elapsed = self.format_time(time_elapsed)
        self.draw_text(self.global_window_pos, 'Time Elapsed: ' + str(time_elapsed[0]) + 'h ' + str(time_elapsed[1]) + 'm ' + str(int(time_elapsed[2])) + 's')
        self.draw_text(self.global_window_pos, 'No. of Species: ' + str(len(species)))
        self.draw_text(self.global_window_pos, 'Energy Reserve: ' + str(round(energy_reserve)))

    def organism_stats(self, selected_organism):
        self.num_lines = 0
        draw_rect_alpha(self.display_surface, (255, 255, 255, 50),
                        (self.org_stats_x, self.org_stats_y, self.org_stats_width, self.org_stats_height))
        self.draw_text(self.org_window_pos, 'Organism Stats', bold=True)
        self.draw_text(self.org_window_pos, 'Age: ' + str(int(selected_organism.age)))
        self.draw_text(self.org_window_pos, 'Energy: ' + str(round(selected_organism.energy)))
        self.draw_text(self.org_window_pos, 'Fitness: ' + str("{:.2f}".format(selected_organism.fitness)))
        self.draw_text(self.org_window_pos, 'Adjusted Fitness: ' + str("{:.2f}".format(selected_organism.adj_fitness)))
        self.draw_text(self.org_window_pos, 'Food Count: ' + str(selected_organism.food_count))
        self.draw_text(self.org_window_pos, 'Offspring: ' + str(selected_organism.offspring))
        self.draw_text(self.org_window_pos, 'Size ' + str("{:.2f}".format(selected_organism.size * 50)))

    def draw_text(self, window_pos, string, bold=False):
        if bold:
            text = self.stats_font_bold.render(string, True, 'black')
        else:
            text = self.stats_font.render(string, True, 'black')
        self.display_surface.blit(text, (window_pos[0] + 5, window_pos[1] + 5 + self.num_lines * 20))
        self.num_lines += 1

    def format_time(self, time_elapsed):
        hours = 0
        minutes = 0
        while time_elapsed > 3600:
            hours += 1
            time_elapsed -= 3600
        while time_elapsed > 60:
            minutes += 1
            time_elapsed -= 60
        seconds = time_elapsed
        return hours, minutes, seconds

    def graph(self, inputs):
        if self.graph_empty:
            self.plot_list = deque([])
            self.graph_empty = False
        if self.graph_update_count % self.graph_timescale == 0:
            self.plot_list.append(inputs)
            if len(self.plot_list) > self.graph_width - 50:
                self.plot_list.popleft()
        if self.show_display:
            # draw graph
            draw_rect_alpha(self.display_surface, (255, 255, 255, 50), (self.graph_x, self.graph_y, self.graph_width, self.graph_height))
            # x axis
            pygame.draw.line(self.display_surface, self.graph_colour,
                             (self.graph_x + 22, self.graph_height + self.graph_y - 20),
                             (self.graph_x + self.graph_width - 22, self.graph_height + self.graph_y - 20), 1)
            # y axis - left
            pygame.draw.line(self.display_surface, self.graph_colour,
                             (self.graph_x + 24, self.graph_height + self.graph_y - 20),
                             (self.graph_x + 24, self.graph_y + 20), 1)
            pygame.draw.line(self.display_surface, self.graph_colour,
                             (self.graph_x + 22, self.graph_y + 20),
                             (self.graph_x + 24, self.graph_y + 20), 1)
            pygame.draw.line(self.display_surface, self.graph_colour,
                             (self.graph_x + 22, self.graph_height // 2 + self.graph_y),
                             (self.graph_x + 24, self.graph_height // 2 + self.graph_y), 1)
            text = self.graph_font.render(str(MAX_FOOD), True, 'green')
            self.display_surface.blit(text, (self.graph_x + 5, self.graph_y + 14))
            text = self.graph_font.render(str(MAX_FOOD // 2), True, 'green')
            self.display_surface.blit(text, (self.graph_x + 10, self.graph_height // 2 + self.graph_y - 6))
            text = self.graph_font.render('0', True, 'green')
            self.display_surface.blit(text, (self.graph_x + 15, self.graph_height + self.graph_y - 26))
            text = self.graph_font.render('Food', True, 'green')
            self.display_surface.blit(text, (self.graph_x + self.graph_width // 4, self.graph_y + 3))
            # y axis - right
            pygame.draw.line(self.display_surface, self.graph_colour,
                             (self.graph_x + self.graph_width - 24, self.graph_height + self.graph_y - 20),
                             (self.graph_x + self.graph_width - 24, self.graph_y + 20), 1)
            pygame.draw.line(self.display_surface, self.graph_colour,
                             (self.graph_x + self.graph_width - 24, self.graph_y + 20),
                             (self.graph_x + self.graph_width - 22, self.graph_y + 20), 1)
            pygame.draw.line(self.display_surface, self.graph_colour,
                             (self.graph_x + self.graph_width - 24, self.graph_height // 2 + self.graph_y),
                             (self.graph_x + self.graph_width - 22, self.graph_height // 2 + self.graph_y), 1)
            text = self.graph_font.render(str(MAX_POP_SIZE), True, 'red')
            self.display_surface.blit(text, (self.graph_x + self.graph_width - 19, self.graph_y + 14))
            text = self.graph_font.render(str(MAX_POP_SIZE // 2), True, 'red')
            self.display_surface.blit(text, (self.graph_x + self.graph_width - 19, self.graph_height // 2 + self.graph_y - 6))
            text = self.graph_font.render('0', True, 'red')
            self.display_surface.blit(text, (self.graph_x + self.graph_width - 19, self.graph_height + self.graph_y - 26))
            text = self.graph_font.render('Population', True, 'red')
            self.display_surface.blit(text, (self.graph_x + 3 * self.graph_width // 4 - 30, self.graph_y + 3))
            # plot data
            for i, data_list in enumerate(self.plot_list):
                x = self.graph_x + 25 + i
                for k, data in enumerate(data_list):
                    if k == 0:
                        colour = (255, 0, 0)
                        y = self.graph_height + self.graph_y - 20 - int((data / MAX_POP_SIZE) * (self.graph_height - 40))
                    else:
                        colour = (0, 255, 0)
                        y = self.graph_height + self.graph_y - 20 - int((data / MAX_FOOD) * (self.graph_height - 40))
                    pygame.draw.rect(self.display_surface, colour, pygame.Rect(x, y, 1, 1))
        self.graph_update_count += 1

    def select_fittest(self):
        self.num_lines = 0
        draw_rect_alpha(self.display_surface, (255, 255, 255, 100),
                        (self.org_stats_x, self.org_stats_y, self.select_fittest_width, self.select_fittest_height))
        pygame.draw.rect(self.display_surface, 'white', (self.org_stats_x, self.org_stats_y, self.select_fittest_width, self.select_fittest_height), 1)
        self.draw_text(self.org_window_pos, 'SHOW FITTEST', bold=True)

    def update(self, time_elapsed, selected_organism, num_food, population, species, energy_reserve):
        if selected_organism and self.show_display:
            draw_circle_alpha(self.display_surface, (255, 255, 255, 50), selected_organism.camera_pos, 100 * selected_organism.size, 3)
        self.graph([len(population), num_food])
        if self.show_display:
            self.global_stats(time_elapsed, species, energy_reserve)
            if selected_organism:
                self.organism_stats(selected_organism)
                self.neat_display.update(selected_organism.nnet, 'Species ID: ' + str(selected_organism.species.id))
            else:
                self.select_fittest()

def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)

def draw_circle_alpha(surface, color, pos, radius, width):
    rect = (pos[0] - radius, pos[1] - radius, 2 * radius, 2 * radius)
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.circle(shape_surf, color, shape_surf.get_rect().center, radius, width)
    surface.blit(shape_surf, rect)