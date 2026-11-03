
import random

import pygame
from . import settings
from .sprites.player import Player
from .sprites.enemy import Enemy

class Game:
    def __init__(self):
        random.seed(0)
        pygame.init()
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption(settings.CAPTION)
        self.clock = pygame.time.Clock()
        self.running = True
        self.player = Player(pos=(100, 100))
        self.enemies = []
        for i in range(10):
            self.enemies.append(Enemy(pos=(random.random() * (settings.SCREEN_WIDTH-settings.ENEMY_SIZE[0]), random.random() * (settings.SCREEN_HEIGHT-settings.ENEMY_SIZE[1])),
                                      vel=(random.random() * 2 * settings.ENEMY_MAX_SPEED - settings.ENEMY_MAX_SPEED, random.random() * 2 * settings.ENEMY_MAX_SPEED - settings.ENEMY_MAX_SPEED)))
    def run(self):
        while self.running:
            self.clock.tick(settings.FPS)
            self.events()
            self.update()
            self.draw()
        pygame.quit()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.player.update()
        for enemy in self.enemies:
            enemy.update()
            enemy.collision(self.player)
            self.player.collision(enemy)

    def draw(self):
        self.screen.fill(settings.BACKGROUND_COLOR)
        for enemy in self.enemies:
            self.screen.blit(enemy.image, enemy.rect)
        self.screen.blit(self.player.image, self.player.rect)
        pygame.display.flip()
