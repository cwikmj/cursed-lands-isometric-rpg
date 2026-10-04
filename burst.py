import pygame
import os

from settings import *
from utils import grid_to_isoscreen
from resource_path import resource_path


class BurstEffect(pygame.sprite.Sprite):
    FRAME_CACHE = {}
    @classmethod
    def preload(cls, actions):
        for action in actions:
            if action in cls.FRAME_CACHE:
                continue

            sheet = pygame.image.load(resource_path(os.path.join("assets/spells", f"burst_{action}.png"))).convert_alpha()

            cols = BURSTS[action]["cols"]
            rows = BURSTS[action]["rows"]
            width = sheet.get_width() // cols
            height = sheet.get_height() // rows

            frames = []
            for row in range(rows):
                for col in range(cols):
                    rect = pygame.Rect(col * width, row * height, width, height)
                    frames.append(sheet.subsurface(rect).copy())

            cls.FRAME_CACHE[action] = tuple(frames)
    
    def __init__(self, x, y, action):
        super().__init__()
        self.x = x
        self.y = y
        self.action = action
        self.images = {action: [frame.copy() for frame in self.FRAME_CACHE[action]]}
        self.current_frame = 0
        self.duration = BURSTS[self.action]['duration']
        self.animation_speed = BURSTS[self.action]['speed']
        self.alive = True
        self.frame_timer = 0
        self.elapsed_time = 0
        self.rect = pygame.Rect(0, 0, 64, 64)

    def animate(self, delta_time):
        self.frame_timer += delta_time
        if self.frame_timer >= self.animation_speed:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.images[self.action])
            if self.current_frame == len(self.images[self.action]) - 1:
                self.alive = False

    def update(self, delta_time):
        if not self.alive:
            return
        self.animate(delta_time)
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.duration:
            self.alive = False

    def update(self, delta_time):
        if not self.alive:
            return
        self.animate(delta_time)
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.duration:
            self.alive = False

    def draw(self, screen, offset_x, offset_y):
        if not self.alive:
            return
        screen_x, screen_y = grid_to_isoscreen(self.x, self.y, offset_x, offset_y)
        frame = self.images[self.action][self.current_frame]
        alpha = max(0, 255 * (1 - (self.elapsed_time / self.duration)))
        frame.set_alpha(alpha)
        screen.blit(frame, (screen_x - frame.get_height() + BURSTS[self.action]['offset_x'], screen_y - frame.get_height() + BURSTS[self.action]['offset_y']))