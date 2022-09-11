import pygame, math
from support import calc_angle, import_folder
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, groups, pos, food_group):
        super().__init__(groups)
        self.food_group = food_group

        # genome attributes
        self.size = 0.2
        self.max_power = 100
        self.turn_speed = 20

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
        self.direction = pygame.math.Vector2(0, -1)
        self.rotation = 0
        self.vel = 0
        self.accel = 0
        self.mass = math.exp(self.size)

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

    def user_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.force = self.max_power * 1000 / (self.vel + 50)
            self.status = 'move'
        elif keys[pygame.K_s]:
            if self.vel > 0:
                self.force = -0.5 * self.max_power * 1000 / (self.vel + 50)
            self.status = 'idle'
        else:
            self.force = 0
            self.status = 'idle'

        if keys[pygame.K_a]:
            self.rotation = -self.turn_speed * 10
        elif keys[pygame.K_d]:
            self.rotation = self.turn_speed * 10
        else:
            self.rotation = 0

    def move(self, dt):
        self.direction.rotate_ip(self.rotation * dt)
        drag_force = 0.01 * DRAG_COEFFICIENT * self.size * self.vel * self.vel
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

        angle = calc_angle(self.direction)
        self.image = pygame.transform.rotate(self.original_image, -angle)
        self.rect = self.image.get_rect(center=self.pos)
        self.rect.centerx = round(self.pos.x)
        self.rect.centery = round(self.pos.y)
        self.mask = pygame.mask.from_surface(self.image)
        # self.collisions()

    def collisions(self):
        if pygame.sprite.spritecollide(self, self.food_group, True, pygame.sprite.collide_mask):
            pass

    def update(self, dt):
        self.user_input()
        self.animate(dt)
        self.move(dt)