import pygame
import os
import re
import math
import random

from settings import *
from spell import *
from projectile import Projectile
from utils import grid_to_isoscreen, update_rect, get_spell_cooldown
from resource_path import resource_path

SHEET_COLS, SHEET_ROWS = 15, 8

class Player(pygame.sprite.Sprite):
    _STAT_REGEX = re.compile(r"\+(\d+)\s+to\s+(\w+)")

    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.actions = {}
        self.current_direction = 0
        self.current_frame = 0
        self.animation_speed = 0.05  # secs per frame
        self.frame_timer = 0
        self.last_regeneration_time = pygame.time.get_ticks()
        self.health = 100
        self.max_health = 100
        self.mana = 100
        self.max_mana = 100
        self.level = 1
        self.exp = 0
        self.skill_points = 0
        self.skills = ['attack']
        self.cash = 0
        self.potions = { 'health': 0, 'mana': 0 }
        self._potion_animations = []
        self.inventory = []
        self.gear = { "helmet": None, "armor": None, "boots": None, "weapon": None, "shield": None }
        self.stats = { "attack": 0, "defence": 0, "willpower": 0, "speed": 0 }
        self.active_cooldown = None
        self.spell_cast_time = 0
        self.spell_cooldown = { 'kick': 500, 'clash': 800, 'whirlwind': 3000, 'firebolt': 2000, 'lightning': 2000, 'teleport': 3000, 'forcepush': 3000 }
        for action in ['attack1', 'attack2', 'clash', 'damage', 'die', 'forcepush', 'teleport', 'idle', 'kick', 'lightning', 'run', 'firebolt', 'whirlwind']:
            self.actions[action] = self.load_images(action)
        self.current_action = 'idle'
        self.current_skill = 'attack1'
        self.target_enemy = None
        self.hit = False
        self.dead = False
        self.death_animation_done = False
        self.death_animation_timer = 0
        self.rect = pygame.Rect(0, 0, TILE_WIDTH, TILE_HEIGHT)

    def load_images(self, action):
        sheet = pygame.image.load(resource_path(os.path.join("assets/actions", f'{action}.png'))).convert_alpha()
        width = sheet.get_width() // SHEET_COLS
        height = sheet.get_height() // SHEET_ROWS

        animations = []
        for row in range(SHEET_ROWS):
            frames = []
            for col in range(SHEET_COLS):
                rect = pygame.Rect(col * width, row * height, width, height)
                frames.append(sheet.subsurface(rect).copy())
            animations.append(frames)
        return animations

    def animate(self, delta_time):
        self.frame_timer += delta_time
        anim_speed = 0.11 if self.current_action in ('clash', 'teleport', 'firebolt', 'lightning', 'forcepush') else 0.05
        if self.frame_timer >= anim_speed:
            self.frame_timer = 0
            if not self.death_animation_done:
                self.current_frame = (self.current_frame + 1) % len(self.actions[self.current_action][self.current_direction])

    def update(self, delta_time, path):
        now = pygame.time.get_ticks()
        if now - self.last_regeneration_time >= REGENERATION_RATE and not self.dead:
            self.health = min(self.health + 1, self.max_health)
            self.last_regeneration_time = now

        if self.health <= 0:
            self.current_action = 'die'
            self.dead = True
            self.animate(delta_time)
            if self.current_frame >= len(self.actions['die'][self.current_direction]) - 1:
                self.death_animation_done = True
                self.death_animation_timer = pygame.time.get_ticks()
            return

        if self.current_action not in ('idle', 'run', 'die'):
            self.animate(delta_time)
            current_anim_len = len(self.actions[self.current_action][self.current_direction])
            
            if self.current_action in DELAYED_DAMAGE_SKILLS:
                self.hit = self.current_frame == current_anim_len - 5
            else:
                self.hit = self.current_frame == 1
                
            if self.current_frame == current_anim_len - 1:
                self.current_action = 'idle'
                self.current_frame = 0
                self.frame_timer = 0
        elif path:
            self.move(delta_time, path)
        else:
            if self.current_action != 'idle':
                self.current_action = 'idle'
                self.current_frame = 0
                self.frame_timer = 0
                self.hit = False
                
        update_rect(self)
        self.update_cooldown_bar(now)
        self.animate(delta_time)
        self.update_potion_animation(delta_time)

    def draw(self, screen, offset_x, offset_y):
        screen_x, screen_y = grid_to_isoscreen(*(self.x, self.y), offset_x, offset_y)
        frame = self.actions[self.current_action][self.current_direction][self.current_frame]
        screen.blit(frame, (screen_x - frame.get_width() // 2, screen_y - frame.get_height() + TILE_HEIGHT // 2))

    def move(self, delta_time, path):
        if not path:
            return

        target_x, target_y = path[0]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            self.turn_forwards(dy, dx)
        else:
            self.current_direction = 0
        self.current_action = 'run'

        if distance < (PLAYER_SPEED + self.stats.get("speed", 0)) * delta_time:
            self.x, self.y = target_x, target_y
            path.pop(0)
        else:
            self.x += (dx / distance) * (PLAYER_SPEED + self.stats.get("speed", 0)) * delta_time
            self.y += (dy / distance) * (PLAYER_SPEED + self.stats.get("speed", 0)) * delta_time
        self.animate(delta_time)
    
    def attack(self, goal, button):
        dx = goal[0] - self.x
        dy = goal[1] - self.y
        self.turn_forwards(dy, dx)
        if self.current_action in ('idle', 'run'):
            if button == 1:
                choice = random.choice([1, 2])
                self.current_action = f'attack{choice}'
            else:
                self.current_action = self.current_skill
            self.current_frame = 0
            self.frame_timer = 0
        
    def can_cast_spell(self, spell, game_log):
        if spell.startswith('attack'):
            return
        if self.mana < SPELLS[spell]["mana_cost"]:
            game_log.add_line("Not enough MANA")
            return
        current_time = pygame.time.get_ticks()
        return (current_time - self.spell_cast_time) >= get_spell_cooldown(self, spell)
    
    def start_spell_cooldown(self, spell):
        self.spell_cast_time = pygame.time.get_ticks()
        actual_cooldown = get_spell_cooldown(self, spell)
        self.active_cooldown = (spell, actual_cooldown)

    def update_cooldown_bar(self, current_time):
        if self.active_cooldown:
            spell, cooldown = self.active_cooldown
            if (current_time - self.spell_cast_time) >= cooldown:
                self.active_cooldown = None

    def cast_spell(self, action, location, target=None):
        self.mana -= SPELLS[action]["mana_cost"]
        if self.mana < 0:
            self.mana = 0
        return Spell(location[0], location[1], action, SPELLS[action]["damage"], target)
    
    def fire_projectile(self, action):
        return Projectile(self.x, self.y, True, self.current_direction, action, SPELLS[action]["damage"])
    
    def turn_forwards(self, dy, dx):
        angle = math.degrees(math.atan2(dy, dx)) + 45
        self.current_direction = round(angle / 45) % 8
        return
    
    def pick_up_item(self, item):
        if item.type == "loot":
            self.cash += item.value
        elif item.type == "potion":
            self.potions[item.name] += 1
        else: 
            self.inventory.append(item)
        return

    def get_melee_damage(self):
        base_dmg = 15 + self.stats.get("attack", 0) + int(self.level * 1.5)
        if self.current_action == 'kick' or self.current_skill == 'kick':
            base_dmg = int(base_dmg * 1.25)
        elif self.current_action == 'clash' or self.current_skill == 'clash':
            base_dmg = int(base_dmg * 1.75)
        elif self.current_action == 'whirlwind' or self.current_skill == 'whirlwind':
            base_dmg = int(base_dmg * 1.40)
        return max(1, base_dmg)

    def get_spell_damage(self, spell_name):
        base_dmg = SPELLS.get(spell_name, {}).get("damage", 0)
        willpower_bonus = self.stats.get("willpower", 0)
        return max(1, int(base_dmg + willpower_bonus * 1.2))

    def take_damage(self, raw_damage):
        defence = self.stats.get("defence", 0)
        mitigation_factor = defence / (defence + 50)
        actual_dmg = max(1, int(round(raw_damage * (1.0 - mitigation_factor))))
        self.health = max(0, self.health - actual_dmg)
        return actual_dmg

    def can_drink(self, type):
        if self.potions[type] > 0 and getattr(self, type) < getattr(self, f'max_{type}'):
            self.potions[type] -= 1
            return True
        return False

    def potion_animation(self, type):
        value_attr = 'health' if type == 'health' else 'mana'
        self._potion_animations.append({
            'active': True,
            'type': value_attr,
            'start_value': getattr(self, value_attr),
            'end_value': getattr(self, f'max_{value_attr}'),
            'progress': 0.0,
            'duration': 5.0
        })

    def update_potion_animation(self, delta_time):
        if not self._potion_animations:
            return

        for anim in self._potion_animations[:]:
            if anim['active']:
                anim['progress'] = min(anim['progress'] + delta_time / anim['duration'], 1.0)
                start, end = anim['start_value'], anim['end_value']
                setattr(self, anim['type'], start + (end - start) * anim['progress'])
                if anim['progress'] >= 1.0:
                    anim['active'] = False
                    self._potion_animations.remove(anim)
    
    def update_stats(self):
        self.stats = { "attack": 0, "defence": 0, "willpower": 0, "speed": 0 }
        for gear_item in self.gear.values():
            if gear_item is not None:
                matches = Player._STAT_REGEX.findall(gear_item.desc)
                for value, metric in matches:
                    self.stats[metric] += int(value)

    def respawn(self):
        self.health = self.max_health
        self.mana = self.max_mana
        self.dead = False
        self.death_animation_done = False
        self.current_action = "idle"
        self.current_frame = 0
        self.frame_timer = 0