import pygame
import math
from .. import settings

class Player():

    def __init__(self, pos=(0, 0)):
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2(pos)
        self.rect.topleft = self.pos
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.health = settings.PLAYER_STARTING_HEALTH

    def update(self):
        keys = pygame.key.get_pressed()
        if not settings.PLAYER_PHYSICS:
            self.vel = pygame.math.Vector2(0, 0)
            if keys[pygame.K_a]:
                self.vel.x -= settings.PLAYER_MAX_SPEED
            if keys[pygame.K_d]:
                self.vel.x += settings.PLAYER_MAX_SPEED
            if keys[pygame.K_s]:
                self.vel.y += settings.PLAYER_MAX_SPEED
            if keys[pygame.K_w]:
                self.vel.y -= settings.PLAYER_MAX_SPEED
            if self.vel.length() > settings.PLAYER_MAX_SPEED:
                self.vel.scale_to_length(settings.PLAYER_MAX_SPEED)
            self.pos += self.vel
        else:
            self.acc = pygame.math.Vector2(0, settings.PLAYER_GRAVITY)
            if keys[pygame.K_a]:
                self.acc.x -= settings.PLAYER_ACCELERATION
            if keys[pygame.K_d]:
                self.acc.x += settings.PLAYER_ACCELERATION
            if keys[pygame.K_s]:
                self.acc.y += settings.PLAYER_ACCELERATION
            if keys[pygame.K_w]:
                self.acc.y -= settings.PLAYER_ACCELERATION
            self.acc.x -= math.copysign(min(settings.PLAYER_FRICTION, abs(self.vel.x)), self.vel.x)
            self.acc.y -= math.copysign(min(settings.PLAYER_FRICTION, abs(self.vel.y)), self.vel.y)
            self.vel += self.acc
            if self.vel.length() > settings.PLAYER_MAX_SPEED:
                self.vel.scale_to_length(settings.PLAYER_MAX_SPEED)
            if self.acc.length() > settings.PLAYER_MAX_ACCELERATION:
                self.acc.scale_to_length(settings.PLAYER_MAX_ACCELERATION)
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
        if self.rect.colliderect(other.rect):
            self.health -= 1
            if self.health <= 0:
                self.health = 0
                print("Player has died.")