import pygame
import math
from .. import settings

class Enemy():

    def __init__(self, pos=(0, 0), vel=(0, 0), acc=(0, 0)):
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(pos)
        self.vel = pygame.math.Vector2(vel)
        self.acc = pygame.math.Vector2(acc)
        self.rect.topleft = self.pos
    
    def update(self):
        if not settings.ENEMY_PHYSICS:
            if self.vel.length() > settings.ENEMY_MAX_SPEED:
                self.vel.scale_to_length(settings.ENEMY_MAX_SPEED)
            self.pos += self.vel
        else:
            self.vel += self.acc
            if self.vel.length() > settings.ENEMY_MAX_SPEED:
                self.vel.scale_to_length(settings.ENEMY_MAX_SPEED)
            if self.acc.length() > settings.ENEMY_MAX_ACCELERATION:
                self.acc.scale_to_length(settings.ENEMY_MAX_ACCELERATION)
            self.pos += self.vel

            max_x = settings.SCREEN_WIDTH - self.rect.width
            max_y = settings.SCREEN_HEIGHT - self.rect.height
            if self.pos.x < 0 and self.vel.x < 0:
                self.pos.x = -self.pos.x * settings.BOUNCE_DAMPING
                self.vel.x = -self.vel.x * settings.BOUNCE_DAMPING
            if self.pos.x > max_x and self.vel.x > 0:
                self.pos.x = max_x - (self.pos.x - max_x) * settings.BOUNCE_DAMPING
                self.vel.x = -self.vel.x * settings.BOUNCE_DAMPING
            if self.pos.y < 0 and self.vel.y < 0:
                self.pos.y = -self.pos.y * settings.BOUNCE_DAMPING
                self.vel.y = -self.vel.y * settings.BOUNCE_DAMPING
            if self.pos.y > max_y and self.vel.y > 0:
                self.pos.y = max_y - (self.pos.y - max_y) * settings.BOUNCE_DAMPING
                self.vel.y = -self.vel.y * settings.BOUNCE_DAMPING
        self.pos.x = pygame.math.clamp(self.pos.x, 0, settings.SCREEN_WIDTH - self.rect.width)
        self.pos.y = pygame.math.clamp(self.pos.y, 0, settings.SCREEN_HEIGHT - self.rect.height)
        self.rect.topleft = self.pos

    def collision(self, other):
        #Eventually handle collision with other enemies
        pass