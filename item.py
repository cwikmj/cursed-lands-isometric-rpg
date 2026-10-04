import pygame
import random
import math
import os

from settings import *
from resource_path import resource_path

ITEM_MAP_SCALE = 0.12
FIXED_ITEMS_SCALE = 0.5
Z_V0 = 220     # initial vertical velocity (px/s)
GRAVITY = 900     # (px/s^2)
TOSS_MINMAX = (40, 80)  # horizontal toss speed range (px/s)
FRICTION = 6.0     # horizontal damping (1/s)
BOUNCE = 0.25    # first impact bounce ratio


class Item(pygame.sprite.Sprite):
    LOADED_IMAGES = {}

    @classmethod
    def preload_images(cls):
        base_path = os.path.join("assets", "items")

        helmets = [f'helmet_{i}.png' for i in range(0, 6)]
        armors = [f'armor_{i}.png' for i in range(0, 10)]
        boots = [f'boots_{i}.png' for i in range(0, 6)]
        weapons = [f'weapon_{i}.png' for i in range(0, 9)]
        shields = [f'shield_{i}.png' for i in range(0, 6)]
        all_images = FIXED_IMAGES + helmets + armors + boots + weapons + shields

        for filename in all_images:
            path = os.path.join(base_path, filename)
            try:
                cls.LOADED_IMAGES[filename] = pygame.image.load(resource_path(path)).convert_alpha()
            except Exception:
                s = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.rect(s, (230, 225, 80, 255), (0, 0, 16, 16), border_radius=4)
                cls.LOADED_IMAGES[filename] = s

    def __init__(self, x, y, item_type, item_name, value=None, description=None):
        super().__init__()
        self.x, self.y, self.type, self.name, self.value, self.desc = x, y, item_type, item_name, value, description
        self.base = self.load_image(item_type)
        if f"{item_type}.png" in FIXED_IMAGES:
            self.image = self.scale(self.base, FIXED_ITEMS_SCALE)
        else:
            self.image = self.scale(self.base, ITEM_MAP_SCALE)
        self.rect = self.image.get_rect()
        ang, spd = random.uniform(0, 2 * math.pi), random.uniform(*TOSS_MINMAX)
        self.vx, self.vy, self.vz = math.cos(ang) * spd, math.sin(ang) * spd, Z_V0
        self.dx, self.dy, self.z = 0.0, 0.0, 0.0
        self.spawning = True
        self.bounced = False
        self.label = FONTS["TITLE"].render(self.name, True, LIGHT)
        self.targeted_for_pickup = False

    def scale(self, surf, k):
        return pygame.transform.smoothscale(surf, (max(1, int(surf.get_width() * k)), max(1, int(surf.get_height() * k))))

    def load_image(self, item_type):
        filename = f"{item_type}.png"
        return self.LOADED_IMAGES.get(filename, self.LOADED_IMAGES.get('loot.png'))
        
    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
    def get_dist_from_player(self, player):
        dx, dy = player.x - self.x, player.y - self.y
        return int(math.hypot(dx, dy))

    def update(self, dt):
        if not self.spawning: return
        self.dx += self.vx * dt; self.dy += self.vy * dt
        self.vx *= math.exp(-FRICTION * dt); self.vy *= math.exp(-FRICTION * dt)
        self.z += self.vz * dt; self.vz -= GRAVITY * dt
        if self.z <= 0:
            if not self.bounced:
                self.z, self.vz, self.bounced = 0, -self.vz * BOUNCE, True
                self.vx *= 0.4; self.vy *= 0.4
                if f"{self.type}.png" not in FIXED_IMAGES:
                    self.image = self.scale(self.base, ITEM_MAP_SCALE)
                    self.image = pygame.transform.smoothscale(self.base, (int(self.base.get_width() * ITEM_MAP_SCALE * 1.05), int(self.base.get_height() * ITEM_MAP_SCALE * 0.92)))
            else:
                self.z = 0
                if abs(self.vx) < 5 and abs(self.vy) < 5 and abs(self.dx) < 1 and abs(self.dy) < 1:
                    self.dx = self.dy = 0
                    self.spawning = False
                    if f"{self.type}.png" not in FIXED_IMAGES:
                        self.image = self.scale(self.base, ITEM_MAP_SCALE)

    def draw(self, screen, offset_x, offset_y, mouse_pos):
        from utils import grid_to_isoscreen
        gx, gy = grid_to_isoscreen(self.x, self.y, offset_x, offset_y)
        x = gx + int(self.dx) - self.image.get_width() // 2
        y = gy + int(self.dy) - self.image.get_height() + TILE_HEIGHT // 2 - int(self.z)
        self.rect.topleft = (x, y)

        if self.is_hovered(mouse_pos) and self.bounced:
            border_thickness = 2
            scale_factor = 1.5
            for i in range(12, 0, -1):
                glow_width = self.rect.width + int(i * 4 * scale_factor)
                glow_height = self.rect.height + int(i * 2 * scale_factor)
                glow_surf = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
                glow_rect = glow_surf.get_rect()
                pygame.draw.ellipse(glow_surf, (252, 191, 106, 10), glow_rect.inflate(-border_thickness * i, -border_thickness * i))
                screen.blit(glow_surf, (x - int(i * 2 * scale_factor), y - int(i * 1 * scale_factor)))


        screen.blit(self.image, (x, y))
        if self.z == 0:
            label_x = x + (self.image.get_width() // 2) - (self.label.get_width() // 2)
            label_y = y - self.label.get_height() - 5
            screen.blit(self.label, (label_x, label_y))

    def pick_up(self, player, game_log):
        if self.type in ('loot', 'potion') or len(player.inventory) < INVENTORY_SLOT_LIMIT:
            player.pick_up_item(self)
            msg = game_log.get_message_for_item(self)
            game_log.add_line(msg)
            return True
        else:
            game_log.add_line("I can't carry anymore")
            return False