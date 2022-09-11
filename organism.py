import numpy as np
import pygame, math, neat
from random import uniform
from support import calc_diff, calc_mag, calc_angle, import_folder
from settings import *

class Organism(pygame.sprite.Sprite):
    def __init__(self, genome, groups, pos, food_group):
        super().__init__(groups)
        # setup neural network
        self.genome = genome
        self.nnet = neat.Neural_network(genome)
        self.food_group = food_group
        self.fitness = 0
        self.adj_fitness = 0
        self.adj_fitness_norm = 0

        # genome attributes
        self.size = genome.size
        self.strength = genome.strength
        self.agility = genome.agility

        # animation setup
        self.import_images()
        self.status = 'idle'
        self.frame_index = 0

        # sprite setup
        self.image = self.animations[self.status][self.frame_index]
        self.image = pygame.transform.rotozoom(self.image, -90, self.size)
        self.original_image = self.image
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

        # movement attributes
        self.pos = pygame.math.Vector2(self.rect.center)
        self.camera_pos = pygame.math.Vector2()
        self.direction = pygame.math.Vector2(uniform(-1, 1), uniform(-1, 1))
        pygame.math.Vector2.normalize_ip(self.direction)
        self.rotation = 0
        self.vel = 0
        self.accel = 0
        self.mass = math.exp(self.size)
        self.force = 0

        # attributes
        self.energy = 10
        self.energy_loss = 0
        self.age = 0
        self.food_count = 0
        self.offspring = 0
        self.selected = False
        self.alive = True

    def fitness_function(self):
        r0 = (1 - self.target[0] / R_NORM)**2
        self.fitness = math.sqrt(self.food_count) + r0

    def import_images(self):
        self.animations = {'idle': [], 'move': []}
        for animation in self.animations.keys():
            full_path = 'graphics/organism/' + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
        if self.status == 'idle':
            self.frame_index += 4 * dt
        elif self.status == 'move':
            self.frame_index += abs(self.force) * 0.03 * dt

        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.original_image = self.animations[self.status][int(self.frame_index)]
        self.original_image = pygame.transform.rotozoom(self.original_image, -90, self.size)

    def action(self, nnet_outputs):
        if nnet_outputs[0] > 0.5 and nnet_outputs[1] < 0.5:
            self.force = self.strength * 5000 * (nnet_outputs[0] - 0.5) * 2 / (self.vel + 50)
            self.status = 'move'
        elif nnet_outputs[0] < 0.5 and nnet_outputs[1] > 0.5:
            if self.vel > 0:
                self.force = -0.5 * self.strength * 5000 / (self.vel + 50)
            else:
                self.force = 0
            self.status = 'idle'
        else:
            self.force = 0
            self.status = 'idle'

        if nnet_outputs[2] > 0.5 and nnet_outputs[3] < 0.5:
            self.rotation = -self.agility * 10 * nnet_outputs[2]
        elif nnet_outputs[2] < 0.5 and nnet_outputs[3] > 0.5:
            self.rotation = self.agility * 10 * nnet_outputs[3]
        else:
            self.rotation = 0

    def move(self, dt):
        # update position
        self.direction.rotate_ip(self.rotation * dt)
        drag_force = 0.01 * DRAG_COEFFICIENT * self.size * self.vel**2
        self.accel = (self.force - drag_force) / self.mass
        self.vel += self.accel * dt
        if self.vel < 0:
            self.vel = 0
        self.pos += self.direction * self.vel * dt
        if self.pos.x > MAP_WIDTH:
            self.pos.x -= MAP_WIDTH
        elif self.pos.x < 0:
            self.pos.x += MAP_WIDTH
        if self.pos.y > MAP_HEIGHT:
            self.pos.y -= MAP_HEIGHT
        elif self.pos.y < 0:
            self.pos.y += MAP_HEIGHT

        # update image
        angle = calc_angle(self.direction)
        self.image = pygame.transform.rotate(self.original_image, -angle)
        self.rect = self.image.get_rect(center=self.pos)
        self.rect.centerx = round(self.pos.x)
        self.rect.centery = round(self.pos.y)
        self.mask = pygame.mask.from_surface(self.image)
        self.collisions()

    def collisions(self):
        collisions = pygame.sprite.spritecollide(self, self.food_group, False, pygame.sprite.collide_mask)
        if collisions:
            for food in collisions:
                if food.radius <= self.size * 8:
                    if self.energy < 50 * self.size:
                        self.energy += food.energy
                        self.food_count += 1
                        food.kill()

    def seek(self, food_group):
        r0 = R_NORM + 1
        d0 = pygame.math.Vector2()
        for food in food_group:
            if food.radius <= self.size * 8:
                d = calc_diff(self.pos, food.pos)
                r = calc_mag(d)
                if r < r0:
                    d0 = d
                    r0 = r
        phi = pygame.math.Vector2(self.direction).angle_to((d0.x, d0.y))
        if phi > 180:
            phi -= 360
        elif phi < -180:
            phi += 360
        return r0, phi

    def update_energy(self):
        if self.energy < self.energy_loss:
            self.energy_loss = self.energy
        self.energy -= self.energy_loss
        output = self.energy_loss
        self.energy_loss = 0
        return output

    def update(self, dt):
        self.energy_loss += (1 + self.force / 1000) * dt
        self.age += dt
        self.target = self.seek(self.food_group)
        nnet_inputs = np.array([self.target[0], self.target[1]])
        nnet_outputs = self.nnet.get_outputs(nnet_inputs)
        self.action(nnet_outputs)
        self.animate(dt)
        self.move(dt)
