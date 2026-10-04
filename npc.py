import pygame
import math
import random
from utils import grid_to_isoscreen
from item import Item
from settings import ITEMS, NPC_DIALOGUES
from resource_path import resource_path

class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, npc_id, name, level, sprite_path):
        super().__init__()
        self.x = x
        self.y = y
        self.npc_id = npc_id
        self.name = name
        self.level = level
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 0.25
        self.frame_timer = 0
        self.dialogue = NPC_DIALOGUES[npc_id]
        self.dialogue_start_time = 0
        self.dialogue_fully_revealed = False
        self.inventory = self.generate_shop_items()
        self.load_images(sprite_path)

    def load_images(self, sprite):
        sheet = pygame.image.load(resource_path(f'assets/maps/{sprite}.png')).convert_alpha()
        for col in range(6):
            rect = pygame.Rect(col * 32, 0, 32, 64)
            frame = sheet.subsurface(rect).copy()
            self.frames.append(frame)
            
        if self.frames:
            self.image = self.frames[0]

    def animate(self, delta_time):
        self.frame_timer += delta_time
        if self.frame_timer >= self.animation_speed:
            self.frame_timer = 0
            self.current_frame += 1
            if self.current_frame >= 6:
                self.current_frame = 0
            self.image = self.frames[self.current_frame]

    def update(self, delta_time):
        self.animate(delta_time)

    def draw(self, screen, offset_x, offset_y):
        screen_x, screen_y = grid_to_isoscreen(self.x, self.y, offset_x, offset_y)
        blit_x = screen_x - (self.image.get_width() // 2)
        blit_y = screen_y - self.image.get_height()
        screen.blit(self.image, (blit_x, blit_y))

    def is_hovered(self, mouse_grid_pos):
        return (self.x, self.y) == mouse_grid_pos

    def get_dist_from_player(self, player):
        dx, dy = player.x - self.x, player.y - self.y
        return math.hypot(dx, dy)

    def get_tooltip_text(self):
        return [self.name, "", "Left click to talk"]

    def generate_shop_items(self):
        shop_items = []
        categories = ['helmet', 'armor', 'weapon', 'shields', 'boots']
        num_items = random.randint(23, 29)
        used_items = {cat: set() for cat in categories}

        for _ in range(num_items):
            category = random.choice(categories)
            items_in_category = ITEMS.get(category, [])
            available_items = [i for i, _ in enumerate(items_in_category) if i not in used_items[category]]

            if not available_items:
                continue

            if random.random() < 0.8:
                available_high = [i for i in available_items if i >= 2]
                index = random.choice(available_high) if available_high else random.choice(available_items)
            else:
                index = random.choice(available_items)
            item_data = items_in_category[index]
            used_items[category].add(index)
            item_type_for_class = item_data["path"].split('.')[0]
            item = Item(0, 0, item_type_for_class, item_data["name"], item_data["value"], item_data["desc"])
            shop_items.append(item)

        for _ in range(random.randint(3, 5)):
            potion_type = random.choice(['health', 'mana'])
            potion = Item(0, 0, potion_type, potion_type, 15, f"Restores {potion_type}")
            shop_items.append(potion)

        return shop_items