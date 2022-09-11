import pygame, neat
from random import randint, uniform, random, choice
from particles import Particle, Food, move_particles
from organism import Organism
from player import Player
from display import Display
from support import calc_mag, calc_diff
from settings import *

class Environment:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.neat = neat.Neat()
        self.display = Display()
        self.population = []
        self.time_elapsed = 0
        self.food_timer = 0
        self.reprod_timer = 0
        self.energy_reserve = INIT_ENERGY_RESERVE
        self.selected_organism = None
        self.show_dark_matter = True

        # sprite group setup
        self.sprite_group = CameraGroup()
        self.player_group = pygame.sprite.Group()
        self.organisms_group = pygame.sprite.Group()
        self.food_group = pygame.sprite.Group()
        self.dark_matter_group = pygame.sprite.Group()

        # create food
        for i in range(INIT_NUM_FOOD):
            if self.create_food((randint(0, MAP_WIDTH), randint(0, MAP_HEIGHT)), 1) == False:
                break

        # create dark matter
        for i in range(NUM_DARK_MATTER):
            new_dark_matter = Particle([self.dark_matter_group], (randint(0, MAP_WIDTH), randint(0, MAP_HEIGHT)))
            if self.show_dark_matter:
                self.sprite_group.add(new_dark_matter)

        # create player
        self.player = Player([self.sprite_group, self.player_group], (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), self.food_group)

        # create population
        for _ in range(INIT_POP_SIZE):
            new_genome = self.neat.create_genome()
            new_genome.size = INIT_ORGANISM_SIZE
            new_genome.strength = INIT_ORGANISM_STRENGTH
            new_genome.agility = INIT_ORGANISM_AGILITY
            if self.create_organism(new_genome, (randint(0, MAP_WIDTH), randint(0, MAP_HEIGHT))) == False:
                break

    def run(self, dt):
        # draw
        self.display_surface.fill([0, 10, 50])
        self.sprite_group.custom_draw(self.player)
        self.display.update(self.time_elapsed, self.selected_organism, len(self.food_group), self.population,
                            self.neat.species, self.energy_reserve)
        # update
        self.update_particles(dt)
        self.sprite_group.update(dt)
        for organism in self.organisms_group:
            self.energy_reserve += organism.update_energy()
        self.kill_organisms()
        self.reproduce_organisms()
        self.reproduce_food()
        self.time_elapsed += dt
        # deselect
        if self.selected_organism:
            if self.selected_organism.alive == False:
                self.selected_organism = None

    def update_particles(self, dt):
        # food movement
        move_particles(self.food_group, self.food_group, -1000, dt) # -1000
        move_particles(self.food_group, self.dark_matter_group, 1000, dt) # 1000
        # dark matter movement
        move_particles(self.dark_matter_group, self.dark_matter_group, 10000, dt) # 10000
        move_particles(self.dark_matter_group, self.food_group, 10000, dt) # 10000
        # merge food into larger food
        if self.merge_food():
            # reset dark matter
            for dark_matter in self.dark_matter_group:
                dark_matter.kill()
            for i in range(NUM_DARK_MATTER):
                new_dark_matter = Particle([self.dark_matter_group], (randint(0, MAP_WIDTH), randint(0, MAP_HEIGHT)))
                if self.show_dark_matter:
                    self.sprite_group.add(new_dark_matter)

    def create_organism(self, genome, pos):
        new_organism = Organism(genome, [self.sprite_group, self.organisms_group], pos, self.food_group)
        if self.energy_reserve >= new_organism.energy:
            self.neat.determine_species(new_organism)
            self.population.append(new_organism)
            self.energy_reserve -= new_organism.energy
            return new_organism
        else:
            new_organism.kill()
        return False

    def kill_organisms(self):
        for organism in self.organisms_group:
            if organism.energy <= 0:
                organism.alive = False
                self.neat.kill(organism)
                organism.kill()
                self.population.remove(organism)

    def reproduce_organisms(self):
        if self.time_elapsed - self.reprod_timer > 1 and len(self.population) >= 2:
            self.reprod_timer = self.time_elapsed
            if len(self.population) < MAX_POP_SIZE:
                sum_adj_fitness = 0
                breeding_pool = []
                for organism in self.organisms_group:
                    self.neat.calculate_fitness(organism)
                    sum_adj_fitness += organism.adj_fitness
                for organism in self.organisms_group:
                    organism.adj_fitness_norm = organism.adj_fitness * 100 / sum_adj_fitness
                    for _ in range(int(organism.adj_fitness_norm)):
                        breeding_pool.append(organism)
                parent1 = choice(breeding_pool)
                parent1_removed = False
                while parent1_removed == False:
                    if parent1 in breeding_pool:
                        breeding_pool.remove(parent1)
                    else:
                        parent1_removed = True
                parent2 = choice(breeding_pool)
                for _ in range(2):
                    new_genome = self.neat.crossover(parent1, parent2)
                    if new_genome:
                        new_genome.size = parent1.size + uniform(-0.05, 0.05)
                        if new_genome.size < MIN_ORGANISM_SIZE:
                            new_genome.size = MIN_ORGANISM_SIZE
                        elif new_genome.size > MAX_ORGANISM_SIZE:
                            new_genome.size = MAX_ORGANISM_SIZE
                        if self.create_organism(new_genome, (parent1.pos.x + uniform(-10, 10), parent1.pos.y + uniform(-10, 10))):
                            parent1.offspring += 1
                            parent2.offspring += 1

    def create_food(self, pos, radius):
        new_food = Food([self.sprite_group, self.food_group], pos, radius)
        if self.energy_reserve >= new_food.energy:
            self.energy_reserve -= new_food.energy
            return new_food
        else:
            new_food.kill()
        return False

    def reproduce_food(self):
        if self.time_elapsed - self.food_timer > 1:
            self.food_timer = self.time_elapsed
            for _ in range(50):
                if len(self.food_group) >= MAX_FOOD:
                    break
                if random() < self.energy_reserve / INIT_ENERGY_RESERVE:
                    if self.create_food((randint(0, MAP_WIDTH), randint(0, MAP_HEIGHT)), 1) == False:
                        break

    def merge_food(self):
        for food1 in self.food_group:
            if food1.radius == 8:
                continue
            cluster = []
            for food2 in self.food_group:
                if food1.radius == food2.radius:
                    d = calc_diff(food1.pos, food2.pos)
                    r = calc_mag(d)
                    if r < food1.radius * 2 + 2:
                        cluster.append(food2)
                    if len(cluster) == 4:
                        self.create_food(food1.pos, food1.radius * 2)
                        for food in cluster:
                            self.energy_reserve += food.energy
                            food.kill()
                        return True
                    # debug
                    elif len(cluster) > 4:
                        print('merge greater than 4')
        return False

    def select_organism(self, mouse_pos):
        if mouse_pos[0] > self.display.org_stats_x
        selected = False
        x = mouse_pos[0] + self.sprite_group.offset.x
        y = mouse_pos[1] + self.sprite_group.offset.y
        for organism in self.organisms_group:
            if organism.rect.collidepoint(x, y):
                self.selected_organism = organism
                organism.selected = True
                selected = True
            else:
                organism.selected = False
        if selected == False:
            self.selected_organism = None

            # max_fitness = 0
            # fittest_organism = None
            # for organism in self.organisms_group:
            #     if organism.fitness > max_fitness:
            #         max_fitness = organism.fitness
            #         fittest_organism = organism
            # if fittest_organism:
            #     self.selected_organism = fittest_organism
            #     fittest_organism.selected = True
            # else:
            #     self.selected_organism = None

    def calc_total_energy(self):
        total_energy = self.energy_reserve
        for organism in self.organisms_group:
            total_energy += organism.energy
        for food in self.food_group:
            total_energy += food.energy
        return total_energy

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for sprite in self.sprites():
            offset_rect = sprite.rect.copy()
            if offset_rect.centerx - player.rect.centerx > MAP_WIDTH / 2:
                offset_rect.centerx -= MAP_WIDTH
            elif offset_rect.centerx - player.rect.centerx < -MAP_WIDTH / 2:
                offset_rect.centerx += MAP_WIDTH
            if offset_rect.centery - player.rect.centery > MAP_HEIGHT / 2:
                offset_rect.centery -= MAP_HEIGHT
            elif offset_rect.centery - player.rect.centery < -MAP_HEIGHT / 2:
                offset_rect.centery += MAP_HEIGHT
            offset_rect.center -= self.offset
            sprite.camera_pos = offset_rect.center
            self.display_surface.blit(sprite.image, offset_rect)


