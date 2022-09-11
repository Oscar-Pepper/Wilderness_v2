import pygame, sys, time
from environment import Environment
from settings import *

class Simulation():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Wilderness')
        # pygame.mixer.music.load('sounds/background.mp3')
        # pygame.mixer.music.play(-1)
        self.clock = pygame.time.Clock()
        self.prev_time = time.time()
        self.environment = Environment()
        self.sim_active = True
        self.speed = 1

    def run(self):
        while self.sim_active:
            dt = (time.time() - self.prev_time) * self.speed
            self.prev_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.sim_active = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.environment.display.show_display = not self.environment.display.show_display
                if event.type == pygame.MOUSEBUTTONUP:
                    self.environment.select_organism(pygame.mouse.get_pos())

            self.environment.run(dt)
            pygame.display.update()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    simulation = Simulation()
    simulation.run()
