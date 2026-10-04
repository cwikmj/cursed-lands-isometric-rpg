import pygame
import os
from utils import grid_to_isoscreen
from resource_path import resource_path

class Teleport(pygame.sprite.Sprite):
    def __init__(self, x, y, tp_id, name, dest_map):
        super().__init__()
        self.x = x
        self.y = y
        self.tp_id = tp_id
        self.name = name
        self.dest_map = dest_map
        self.active = False
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 0.10 # seconds per frame
        self.frame_timer = 0
        self.load_images()
        
    def load_images(self):
        sheet_path = os.path.join("assets/maps/", "teleport.png")
        sheet = pygame.image.load(resource_path(sheet_path)).convert()
        sheet.set_colorkey((0, 0, 0))
        frame_width = 128
        frame_height = 64
        
        for row in range(5):
            rect = pygame.Rect(0, row * frame_height, frame_width, frame_height)
            frame = sheet.subsurface(rect).copy()
            self.frames.append(frame)
        self.image = self.frames[0]

    def animate(self, delta_time):
        self.frame_timer += delta_time
        if self.frame_timer >= self.animation_speed:
            self.frame_timer = 0
            self.current_frame += 1
            if self.current_frame > 4:
                self.current_frame = 1
            self.image = self.frames[self.current_frame]

    def update(self, delta_time):
        if self.active:
            self.animate(delta_time)
        else:
            self.image = self.frames[0]

    def draw(self, screen, offset_x, offset_y):
        screen_x, screen_y = grid_to_isoscreen(self.x, self.y, offset_x, offset_y)
        blit_x = screen_x - (self.image.get_width() // 2)
        blit_y = screen_y - (self.image.get_height() // 2) 
        screen.blit(self.image, (blit_x, blit_y))

    def is_hovered(self, mouse_grid_pos):
        return (self.x, self.y) == mouse_grid_pos
        
    def get_dist_from_player(self, player):
        return max(abs(self.x - player.x), abs(self.y - player.y))