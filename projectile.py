import math
import os
import pygame

from utils import grid_to_isoscreen, update_rect
from burst import BurstEffect
from resource_path import resource_path

class Projectile(pygame.sprite.Sprite):
    FRAME_CACHE = {}
    @classmethod
    def preload(cls, actions):
        for action in actions:
            if action in cls.FRAME_CACHE:
                continue

            sheet = pygame.image.load(resource_path(os.path.join("assets/spells", f"{action}.png"))).convert_alpha()
            width = sheet.get_width() // 8
            height = sheet.get_height() // 8
            rows = []
            for row in range(8):
                frames = []
                for col in range(8):
                    rect = pygame.Rect(col * width, row * height, width, height)
                    frame = sheet.subsurface(rect).copy()
                    frames.append(pygame.transform.flip(frame, True, True))
                rows.append(tuple(frames))
            cls.FRAME_CACHE[action] = tuple(rows)

    def __init__(self, x, y, from_player, direction, action, damage, speed=10):
        super().__init__()
        self.x = x
        self.y = y
        self.direction = direction
        self.action = action
        self.from_player = from_player
        self.speed = speed
        self.damage = damage
        self.images = {action: self.FRAME_CACHE[action]}
        self.current_frame = 0
        self.animation_speed = 0.05  # seconds per frame
        self.frame_timer = 0
        self.alive = True
        self.wall_hit = False
        self.rect = pygame.Rect(0, 0, 64, 64)
        update_rect(self)

    def animate(self, delta_time):
        self.frame_timer += delta_time
        if self.frame_timer >= self.animation_speed:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.images[self.action][self.direction])

    def update(self, delta_time, map_data):
        if not self.alive:
            return

        angle_rad = math.radians(self.direction * 45 - 45)
        dx = self.speed * delta_time * math.cos(angle_rad)
        dy = self.speed * delta_time * math.sin(angle_rad)
        passable = map_data['walkable_cells']
        steps = max(1, math.ceil(max(abs(dx), abs(dy)) * 4))
        start_x, start_y = self.x, self.y
        for step in range(1, steps + 1):
            next_x = start_x + dx * step / steps
            next_y = start_y + dy * step / steps
            if (int(next_x), int(next_y)) not in passable:
                self.alive = False
                self.wall_hit = True
                update_rect(self)
                return
            self.x, self.y = next_x, next_y

        self.animate(delta_time)
        update_rect(self)

    def draw(self, screen, offset_x, offset_y):
        if not self.alive:
            return
        screen_x, screen_y = grid_to_isoscreen(self.x, self.y, offset_x, offset_y)
        frame = self.images[self.action][self.direction][self.current_frame]
        if self.direction == 0:
            screen_x += frame.get_width() // 3
            screen_y -= frame.get_width() // 3
        if self.direction == 4:
            screen_x -= frame.get_width()
            screen_y -= frame.get_width() // 2
        if self.direction == 5:
            screen_x -= frame.get_width() // 3
            screen_y -= frame.get_width() // 3
        if self.direction == 6:
            screen_y -= frame.get_width()
        screen.blit(frame, (screen_x - frame.get_width() // 2, screen_y - frame.get_height() // 2))

    def hit(self, bursts_group, target):
        self.alive = False
        burst = BurstEffect(target.x, target.y, self.action)
        bursts_group.add(burst)