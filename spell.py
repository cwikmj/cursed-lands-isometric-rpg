import pygame
import os

from settings import *
from utils import grid_to_isoscreen
from resource_path import resource_path


class Spell(pygame.sprite.Sprite):
    FRAME_CACHE = {}
    @classmethod
    def preload(cls, actions):
        actions = list(actions)
        for action in actions[:-2]:
            if action in cls.FRAME_CACHE:
                continue

            sheet = pygame.image.load(resource_path(os.path.join("assets/spells", f"{action}.png"))).convert_alpha()
            cols = SPELLS[action]["cols"]
            rows = SPELLS[action]["rows"]
            width = sheet.get_width() // cols
            height = sheet.get_height() // rows
            frames = []
            for row in range(rows):
                for col in range(cols):
                    rect = pygame.Rect(col * width, row * height, width, height)
                    frames.append(sheet.subsurface(rect).copy())
            cls.FRAME_CACHE[action] = tuple(frames)
    
    def __init__(self, x, y, action, damage, target=None):
        super().__init__()
        self.x = x
        self.y = y
        self.action = action
        self.target = target
        self.duration = SPELLS[self.action]['duration']
        self.damage = damage
        self.images = {action: self.FRAME_CACHE[action]}
        self.current_frame = 0
        self.animation_speed = SPELLS[self.action]['speed']     # secs per frame
        self.alive = True
        self.frame_timer = 0
        self.elapsed_time = 0
        self.rect = pygame.Rect(0, 0, SPELLS[self.action]['rect_x'], SPELLS[self.action]['rect_y'])

    def animate(self, delta_time):
        if self.target:
            self.x, self.y = self.target.x, self.target.y
        self.frame_timer += delta_time
        if self.frame_timer >= self.animation_speed:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.images[self.action])

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
        screen.blit(frame, (screen_x - frame.get_height() + SPELLS[self.action]['offset_x'], screen_y - frame.get_height() + SPELLS[self.action]['offset_y']))

    def hit(self):
        self.alive = False

def push_away(enemy, player, map_data):
    dx, dy = enemy.x - player.x, enemy.y - player.y
    
    if abs(dx) > abs(dy):  # Horizontal priority (E/W)
        push_x = 1.5 if dx > 0 else -1.5
        push_y = 0
    else:  # Vertical priority (N/S)  
        push_x = 0
        push_y = 1.5 if dy > 0 else -1.5
        
    tx, ty = enemy.x + push_x, enemy.y + push_y
    
    if (int(tx), int(ty)) in map_data['walkable_cells']:
        enemy.x, enemy.y = tx, ty
    return
