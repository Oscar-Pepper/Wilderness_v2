import pygame
import pygame.gfxdraw
from support import calc_mag, calc_diff
from settings import *

class Particle(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)
        self.groups = groups

        # # sprite setup
        self.image = pygame.Surface([2, 2])
        self.image.fill('red')
        self.rect = self.image.get_rect(center=pos)

        # movement attributes
        self.pos = pygame.math.Vector2(self.rect.center)
        self.vel = pygame.math.Vector2()

class Food(Particle):
    def __init__(self, groups, pos, radius):
        Particle.__init__(self, groups, pos)
        self.radius = radius
        self.energy = radius**2 * 2

        # sprite setup
        diameter = radius * 2
        food_surf = pygame.Surface((diameter + 1, diameter + 1), pygame.SRCALPHA)
        pygame.draw.circle(food_surf, (0, 255, 50), (radius, radius), radius)
        pygame.gfxdraw.aacircle(food_surf, radius, radius, radius, (0, 255, 50))
        self.image = food_surf
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

def move_particles(group1, group2, g, dt):
    if group1 and group2:
        for particle1 in group1:
            force = pygame.math.Vector2()
            for particle2 in group2:
                d = calc_diff(particle1.pos, particle2.pos)
                r = calc_mag(d)
                if r and r < MAP_WIDTH:
                    direction = pygame.math.Vector2.normalize(d)
                    force += (g * 1 / (r + 100)) * direction
            particle1.vel = (particle1.vel + force * dt * 5) * 0.2
            particle1.pos += particle1.vel * dt * 5
            if particle1.pos.x > MAP_WIDTH:
                particle1.pos.x -= MAP_WIDTH
            elif particle1.pos.x < 0:
                particle1.pos.x += MAP_WIDTH
            if particle1.pos.y > MAP_HEIGHT:
                particle1.pos.y -= MAP_HEIGHT
            elif particle1.pos.y < 0:
                particle1.pos.y += MAP_HEIGHT
            particle1.rect.centerx = round(particle1.pos.x)
            particle1.rect.centery = round(particle1.pos.y)
