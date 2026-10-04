import pygame
import random
import math

from settings import *
from item import Item
from resource_path import resource_path

class Chest(pygame.sprite.Sprite):
    def __init__(self, pos, items):
        super().__init__()
        self.x = pos[0]
        self.y = pos[1]
        self.items = items or []
        self.opened = False
        self.image = pygame.transform.scale(pygame.image.load(resource_path('assets/items/money.png')).convert_alpha(), SKILL_ICON_SIZE)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def is_hovered(self, mouse_pos, offset_x, offset_y):
        screen_x, screen_y = ((self.x - self.y) * TILE_WIDTH // 2 + offset_x, (self.x + self.y) * TILE_HEIGHT // 2 + offset_y)
        hitbox = pygame.Rect(screen_x - 48, screen_y - 64, 96, 88)
        return hitbox.collidepoint(mouse_pos)
    
    def get_dist_from_player(self, player):
        dx, dy = player.x - self.x, player.y - self.y
        return math.hypot(dx, dy)

    def get_tooltip_text(self):
        if self.opened:
            return ["Empty"]
        else:
            return ["Chest", "Left click to open"]

    def collect_items(self, player, map_layers, game_log):
        self.opened = True
        for item in self.items:
            msg = game_log.get_message_for_item(item)
            game_log.add_line(msg)
            if item.type == 'loot':
                player.cash += item.value
            elif item.type == 'potion':
                player.potions[item.name] += 1
            else:
                player.inventory.append(item)
        self.items = []

        for layer in map_layers:
            if layer["name"] == "props-low":
                ox, oy = layer["offset_x"], layer["offset_y"]
                lx, ly = self.x - ox, self.y - oy
                layer["data"][ly][lx] += 1
                break

def generate_chest_content():
    items = []
    num_items = random.randint(2, 4)

    for _ in range(num_items):
        roll = random.random()
        if roll < 0.45:
            item_type, item_name, value, description = 'loot', 'loot', random.randint(50, 80), None
        elif roll < 0.8:
            item_type, item_name, value, description = 'potion', random.choices(['health', 'mana'], weights=[65, 35], k=1)[0], 0, None
        else:
            base_item = random.choice(['helmet', 'armor', 'boots', 'weapon'])
            randint = random.randint(0, 1)
            item_type, item_name, value, description = f"{base_item}_{randint}", ITEMS[base_item][randint]["name"], ITEMS[base_item][randint]["value"], ITEMS[base_item][randint]["desc"]
        items.append(Item(0, 0, item_type, item_name, value, description))

    return items

def draw_chest_modal(screen, chest):
    MODAL_HEIGHT, ITEM_WIDTH, PADDING = 180, 160, 30
    MIN_MODAL_WIDTH, MAX_NAME_WIDTH, LINE_HEIGHT = 300, 140, 20
    num_items = len(chest.items)
    modal_width = max(MIN_MODAL_WIDTH, num_items * ITEM_WIDTH + PADDING * 2)
    MODAL_X, MODAL_Y = (SCREEN_WIDTH - modal_width) // 2, (SCREEN_HEIGHT - MODAL_HEIGHT) // 2

    modal_bg = pygame.Surface((modal_width, MODAL_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(modal_bg, (30, 30, 30, 220), (0, 0, modal_width, MODAL_HEIGHT), border_radius=10)
    pygame.draw.rect(modal_bg, LIGHT, (0, 0, modal_width, MODAL_HEIGHT), 2, border_radius=10)
    screen.blit(modal_bg, (MODAL_X, MODAL_Y))
    title = FONTS["TITLE"].render("You've found", True, EXP)
    screen.blit(title, (MODAL_X + PADDING, MODAL_Y + 10))

    item_x = MODAL_X + PADDING
    item_y = MODAL_Y + 50
    for item in chest.items:
        if hasattr(item, 'image'):
            item_img = pygame.transform.scale(item.image, (30, 30))
            screen.blit(item_img, (item_x, item_y))

            name = item.name
            if FONTS["TITLE"].size(name)[0] > MAX_NAME_WIDTH:
                words = name.split()
                mid = len(words) // 2
                line1, line2 = ' '.join(words[:mid]), ' '.join(words[mid:])
                screen.blit(FONTS["TITLE"].render(line1, True, LIGHT), (item_x + 40, MODAL_Y + 55))
                screen.blit(FONTS["TITLE"].render(line2, True, LIGHT), (item_x + 40, MODAL_Y + 55 + LINE_HEIGHT))
            else:
                screen.blit(FONTS["TITLE"].render(name, True, LIGHT), (item_x + 40, MODAL_Y + 55))
        
        item_x += ITEM_WIDTH

    ok_button = pygame.Rect(MODAL_X + modal_width - 120, MODAL_Y + MODAL_HEIGHT - 40, 100, 30)
    pygame.draw.rect(screen, (50, 50, 50), ok_button, border_radius=5)
    pygame.draw.rect(screen, LIGHT, ok_button, 2, border_radius=5)
    ok_text = FONTS["UI"].render("TAKE", True, EXP)
    screen.blit(ok_text, (ok_button.centerx - ok_text.get_width()//2, ok_button.centery - ok_text.get_height()//2))

    return ok_button
