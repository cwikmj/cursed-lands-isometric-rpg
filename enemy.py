import pygame
import os
import math
import random

from settings import *
from sound_data import *
from item import Item
from utils import grid_to_isoscreen, update_rect, projectile_path
from projectile import Projectile
from pathfinding import a_star
from map import check_grid_aligned
from resource_path import resource_path

class Enemy(pygame.sprite.Sprite):
    _ANIMATION_CACHE = {}
    _NAME_SURFACES = {}

    def __init__(self, pos, type, style):
        super().__init__()
        self.x = pos[0]
        self.y = pos[1]
        self.type = type
        self.style = style
        self.actions = {}
        self.current_direction = 0
        self.current_frame = 0
        self.animation_speed = 0.08  # secs per frame
        self.frame_timer = 0
        self.path = []
        self.last_player_pos = [self.x, self.y]
        self.last_path_time = 0
        self.path_recalc_interval = 1200
        self.last_idle_decision = 0
        self.projectiles = []
        self.triggered = False
        self.hit = False
        self.got_hit = False
        self.dead = False
        self.current_action = 'idle'
        self.max_health = ENEMY_STATS[self.type]["MAX_HEALTH"]
        self.health = self.max_health
        self.load_images()
        self.rect = pygame.Rect(0, 0, TILE_WIDTH, TILE_HEIGHT)

        if self.type not in Enemy._NAME_SURFACES:
            font = pygame.font.Font(ORBITRON, 15)
            Enemy._NAME_SURFACES[self.type] = font.render(self.type, True, (255, 255, 255))
        self.name_surface = Enemy._NAME_SURFACES[self.type]

    def load_images(self):
        if self.type in Enemy._ANIMATION_CACHE:
            self.actions = Enemy._ANIMATION_CACHE[self.type]
            return

        sheet = pygame.image.load(resource_path(os.path.join("assets/enemies/", f'{self.type}.png'))).convert_alpha()
        width = sheet.get_width() // ENEMY_STATS[self.type]["COLS"]
        height = sheet.get_height() // ENEMY_STATS[self.type]["ROWS"]

        actions_dict = {}
        for action, (start_col, end_col) in ENEMY_STATS[self.type]["ACTION_FRAMES"].items():
            frames_for_action = []
            for row in range(ENEMY_STATS[self.type]["ROWS"]):
                frames = []
                for col in range(start_col, end_col):
                    rect = pygame.Rect(col * width, row * height, width, height)
                    frames.append(sheet.subsurface(rect).copy())
                frames_for_action.append(frames)
            actions_dict[action] = frames_for_action

        Enemy._ANIMATION_CACHE[self.type] = actions_dict
        self.actions = actions_dict

    def animate(self, delta_time):
        self.frame_timer += delta_time
        if self.frame_timer < self.animation_speed:
            return

        self.frame_timer = 0
        frame_count = len(self.actions[self.current_action][self.current_direction])

        if self.current_action in ("idle", "run"):
            self.current_frame = (self.current_frame + 1) % frame_count
        else:
            self.current_frame = min(self.current_frame + 1, frame_count - 1)

    def draw(self, screen, offset_x, offset_y):
        screen_x, screen_y = grid_to_isoscreen(*(self.x, self.y), offset_x, offset_y)
        frame = self.actions[self.current_action][self.current_direction][self.current_frame]
        screen.blit(frame, (screen_x - frame.get_width() // 2, screen_y - frame.get_height() + TILE_HEIGHT // 2))

        if not self.dead:
            bar_width = 50
            bar_height = 6
            health_ratio = max(0.0, min(1.0, self.health / float(self.max_health)))
            fill = health_ratio * bar_width
            bar_x = screen_x - bar_width // 2
            bar_y = screen_y - frame.get_height() + TILE_HEIGHT // 2 - 2

            pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height), 0, 2)
            if fill > 0:
                pygame.draw.rect(screen, (200, 35, 35), (bar_x, bar_y, int(fill), bar_height), 0, 2)
            pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1, 2)

            name_x = screen_x - self.name_surface.get_width() // 2
            name_y = bar_y - 18
            screen.blit(self.name_surface, (name_x, name_y))

    def update(self, delta_time, player, items, map_manager, sound_manager, game_log, enemies):
        def set_action(a):
            if self.current_action != a:
                self.current_action = a
                self.current_frame = 0
                self.frame_timer = 0

        if self.dead:
            set_action('die')
            if self.current_frame < len(self.actions['die'][self.current_direction]) - 1:
                self.animate(delta_time)
            return

        if player.dead:
            set_action('idle')
            self.animate(delta_time)
            self.path = []
            return

        distance = self.get_dist_from_player(player)
        dx, dy = player.x - self.x, player.y - self.y
        now = pygame.time.get_ticks()

        # Finish attack animation if already attacking
        if self.current_action == "attack":
            self.animate(delta_time)
            if self.current_frame == len(self.actions['attack'][self.current_direction]) - 1:
                set_action('idle')

        # Melee damage intake
        if distance < ATTACK_RANGE and player.hit and not self.got_hit:
            if player.target_enemy == self:
                self.health -= player.get_melee_damage()
                self.got_hit = True
                self.triggered = True
                if self.health < 1:
                    self.enemy_died(player, items, sound_manager, game_log)

        # AoE damage intake
        if distance < 2 * ATTACK_RANGE and player.hit and not self.got_hit and player.current_action in ('forcepush', 'whirlwind'):
            if player.current_action == 'whirlwind':
                self.health -= int(player.get_melee_damage() * 1.5)
            else:
                self.health -= int(player.get_melee_damage() * 2.5)
            self.got_hit = True
            self.triggered = True
            if self.health < 1:
                self.enemy_died(player, items, sound_manager, game_log)

        if not player.hit:
            self.got_hit = False

        # If player escaped far away (leash), drop agro completely
        if distance >= 12:
            self.triggered = False
            self.path = []
            set_action('idle')

        # --- MELEE COMBAT & PATHFINDING ---
        if self.style == 'melee':
            if distance < 7 or self.triggered:
                # Attack if in range
                if distance <= 1.5 and not player.dead:
                    self.path = []
                    self.turn_forwards(dy, dx)
                    if self.current_action in ('idle', 'attack'):
                        if now - self.last_idle_decision > 700:
                            self.last_idle_decision = now
                            if random.random() < 0.75:
                                set_action('attack')
                                player.take_damage(ENEMY_STATS[self.type]["DAMAGE"])
                                sound_manager.play_sound(f'{self.type.replace(" ","").lower()}{random.randint(1, 2)}')
                            else:
                                set_action('idle')
                        self.animate(delta_time)
                        return
                    set_action(random.choice(('attack', 'idle')))
                    self.last_idle_decision = now
                    self.animate(delta_time)
                    return

                # Follow player
                player_moved = (self.last_player_pos[0] is None or abs(player.x - self.last_player_pos[0]) > 0.5 or abs(player.y - self.last_player_pos[1]) > 0.5)
                if ((now - self.last_path_time > self.path_recalc_interval and player_moved) or not self.path):
                    self.path = self.follow_player(player, map_manager, enemies)
                    self.last_path_time = now
                    self.last_player_pos = (player.x, player.y)

                if self.path:
                    set_action('run')
                    self.move(delta_time, enemies)
                    if not self.path:
                        set_action('idle')
                else:
                    set_action('idle')
                    self.path = []
            else:
                set_action('idle')
                self.path = []

        # --- RANGED / SPELLCASTER ENEMY ---
        else:
            CAST_RANGE = 5.0
            if distance < 10 or self.triggered:
                player_moved = (self.last_player_pos[0] is None or abs(player.x - self.last_player_pos[0]) > 0.8 or abs(player.y - self.last_player_pos[1]) > 0.8)

                # Reposition if out of cast range or obstructed
                if distance > CAST_RANGE:
                    if (now - self.last_path_time > self.path_recalc_interval and player_moved) or not self.path:
                        path_to_shot = check_grid_aligned(player, self, map_manager.maps[map_manager.current_map])
                        if path_to_shot is True:
                            self.path = []
                        elif path_to_shot is not None:
                            self.path = a_star((int(round(self.x)), int(round(self.y))), path_to_shot, map_manager)
                        self.last_path_time = now
                        self.last_player_pos = (player.x, player.y)

                    if self.path:
                        set_action('run')
                        self.move(delta_time, enemies)
                        if not self.path:
                            set_action('idle')
                    else:
                        set_action('idle')
                        self.path = []
                else:
                    # In cast range: stand ground, face player, and shoot
                    self.path = []
                    self.turn_forwards(dy, dx)
                    if now - self.last_idle_decision > 1500:
                        set_action('attack')
                        shot_direction = round((math.degrees(math.atan2(dy, dx)) + 45) / 45) % 8
                        self.projectiles.append(Projectile(self.x, self.y, False, shot_direction, self.style, SPELLS[self.style]["damage"]))
                        self.last_idle_decision = now
                        shot_sound = 'icebolt' if self.style == 'icebolt' else 'fireball'
                        sound_manager.play_sound(shot_sound)
                    else:
                        if self.current_action != 'attack':
                            set_action('idle')
            else:
                set_action('idle')
                self.path = []
        update_rect(self)
        self.animate(delta_time)

    def check_projectiles_to_fire(self):
        return self.projectiles if self.projectiles != [] else []

    def move(self, delta_time, enemies):
        if not self.path:
            return

        target_x, target_y = self.path[0]
        for e in enemies:
            if e != self and not e.dead:
                if int(round(e.x)) == target_x and int(round(e.y)) == target_y:
                    self.path = []
                    return

        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            self.turn_forwards(dy, dx)
        else:
            self.current_direction = 0

        move_speed = ENEMY_STATS[self.type]["SPEED"] * delta_time
        if distance <= move_speed:
            self.x, self.y = target_x, target_y
            self.path.pop(0)
        else:
            self.x += (dx / distance) * move_speed
            self.y += (dy / distance) * move_speed

    def get_dist_from_player(self, player):
        dx, dy = player.x - self.x, player.y - self.y
        return math.hypot(dx, dy)

    def follow_player(self, player, map_manager, enemies):
        start = (int(round(self.x)), int(round(self.y)))
        player_pos = (int(round(player.x)), int(round(player.y)))

        if abs(start[0] - player_pos[0]) <= 1 and abs(start[1] - player_pos[1]) <= 1:
            return []

        occupied_positions = set()
        claimed_destinations = set()

        for e in enemies:
            if e != self and not e.dead:
                occupied_positions.add((int(round(e.x)), int(round(e.y))))
                if e.path:
                    claimed_destinations.add(e.path[-1])
                    occupied_positions.add(e.path[0])

        walkable_cells = map_manager.maps[map_manager.current_map]['walkable_cells']
        valid_attack_spots = []

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            spot = (player_pos[0] + dx, player_pos[1] + dy)
            if spot in walkable_cells:
                if spot not in occupied_positions and spot not in claimed_destinations:
                    valid_attack_spots.append(spot)

        if valid_attack_spots:
            valid_attack_spots.sort(key=lambda spot: abs(start[0] - spot[0]) + abs(start[1] - spot[1]))
            target = valid_attack_spots[0]
        else:
            target = player_pos

        return a_star(start, target, map_manager, occupied_positions)

    def turn_forwards(self, dy, dx):
        angle = math.degrees(math.atan2(dy, dx)) + 45 + 180
        self.current_direction = round(angle / 45) % 8
        return

    def is_hovered(self, mouse_pos, offset_x, offset_y):
        screen_x, screen_y = grid_to_isoscreen(*(self.x, self.y), offset_x, offset_y)
        frame = self.actions[self.current_action][self.current_direction][self.current_frame]
        enemy_rect = pygame.Rect(screen_x - frame.get_width() // 2, screen_y - frame.get_height() + TILE_HEIGHT // 2, frame.get_width(), frame.get_height())
        return enemy_rect.collidepoint(mouse_pos)

    def enemy_died(self, player, items, sound_manager, game_log):
        if self.dead:
            return
        self.dead = True
        player.exp += ENEMY_STATS[self.type]["EXP"]
        sound_manager.play_sound(f'{self.type.replace(' ','').lower()}die')
        if player.exp >= EXP_LEVELS[player.level]:
            player.level += 1
            player.skill_points += 1
            player.max_health += 10
            player.max_mana += 10
            game_log.add_line(f"YOU'RE NOW LEVEL {player.level}!")
        if not self.type == "Demon":
            sound_manager.play_sound('item-drop')
            self.drop_item(items)
        else:
            sound_manager.play_music(LEVEL_MUSIC['ebonwood'], loops=-1, fade_ms=1200)

    def drop_item(self, items):
        roll = random.random()
        if roll < 0.45:
            item_type, item_name, value, description = 'loot', 'loot', random.randint(50, 80), None
        elif roll < 0.8:
            item_type, item_name, value, description = 'potion', random.choices(['health', 'mana'], weights=[68, 32], k=1)[0], 0, None
        else:
            base_item = random.choice(['helmet', 'armor', 'boots', 'weapon'])
            randint = random.randint(0, 2)
            item_type, item_name, value, description = f"{base_item}_{randint}", ITEMS[base_item][randint]["name"], ITEMS[base_item][randint]["value"], ITEMS[base_item][randint]["desc"]
        item = Item(self.x, self.y, item_type, item_name, value, description)
        items.add(item)
        return item


class DemonBoss(Enemy):
    def __init__(self, pos):
        super().__init__(pos, "Demon", "firebolt")
        self.pending_effects = []
        self.intro_shown = False
        self.dialogue_start_time = 0
        self.dialogue_fully_revealed = False
        self.health_regen_percent_per_second = 0.01
        self.voice_sound_count = 5
        self.voice_channel = pygame.mixer.find_channel()
        now = pygame.time.get_ticks()
        self.next_voice_time = now + random.randint(4000, 8000)
        self.min_voice_delay_ms = 7000
        self.max_voice_delay_ms = 15000

    def draw(self, screen, offset_x, offset_y):
        screen_x, screen_y = grid_to_isoscreen(*(self.x, self.y), offset_x, offset_y)
        frame = self.actions[self.current_action][self.current_direction][self.current_frame]
        screen.blit(frame, (screen_x - frame.get_width() // 2, screen_y - frame.get_height() + TILE_HEIGHT // 2))

        if not self.dead:
            bar_width = 80
            bar_height = 8
            health_ratio = max(0.0, min(1.0, self.health / float(self.max_health)))
            fill = health_ratio * bar_width
            bar_x = screen_x - bar_width // 2
            bar_y = screen_y - frame.get_height() + TILE_HEIGHT // 2 - 4
            pygame.draw.rect(screen, (30, 20, 20), (bar_x, bar_y, bar_width, bar_height), 0, 2)
            if fill > 0:
                pygame.draw.rect(screen, (220, 20, 20), (bar_x, bar_y, int(fill), bar_height), 0, 2)
            pygame.draw.rect(screen, (255, 215, 0), (bar_x, bar_y, bar_width, bar_height), 1, 2)

            name_x = screen_x - self.name_surface.get_width() // 2
            name_y = bar_y - 20
            screen.blit(self.name_surface, (name_x, name_y))

    def update(self, delta_time, player, items, map_manager, sound_manager, game_log, enemies):
        def set_action(a):
            if self.current_action != a:
                self.current_action = a
                self.current_frame = 0
                self.frame_timer = 0

        if self.dead:
            set_action('die')
            if self.current_frame < len(self.actions['die'][self.current_direction]) - 1:
                self.animate(delta_time)
            return

        now = pygame.time.get_ticks()
        if self.health < self.max_health:
            regen_amount = self.max_health * self.health_regen_percent_per_second * delta_time
            self.health = min(self.max_health, self.health + regen_amount)
        self.update_voice(sound_manager, now)

        if player.dead:
            set_action('idle')
            self.animate(delta_time)
            self.path = []
            return

        distance = self.get_dist_from_player(player)
        dx, dy = player.x - self.x, player.y - self.y

        if self.current_action == "cast":
            self.animate(delta_time)
            if self.current_frame == len(self.actions['cast'][self.current_direction]) - 1:
                set_action('idle')

        if distance < ATTACK_RANGE and player.hit and not self.got_hit:
            if getattr(player, 'target_enemy', None) == self:
                self.health -= player.get_melee_damage()
                self.got_hit = True
                self.triggered = True
                if self.health < 1:
                    self.enemy_died(player, items, sound_manager, game_log)

        if distance < 2 * ATTACK_RANGE and player.hit and not self.got_hit and player.current_action in ('forcepush', 'whirlwind'):
            if player.current_action == 'whirlwind':
                self.health -= player.get_melee_damage()
            else:
                self.health -= player.get_spell_damage('forcepush')
            self.got_hit = True
            self.triggered = True
            if self.health < 1:
                self.enemy_died(player, items, sound_manager, game_log)

        if not player.hit:
            self.got_hit = False

        if self.triggered or distance < 12:
            if now - self.last_idle_decision > 1000:
                self.last_idle_decision = now
                action_roll = random.random()

                if action_roll <= 0.68:
                    self.path = []
                    path_to_shot = check_grid_aligned(player, self, map_manager.maps[map_manager.current_map])

                    if path_to_shot is True:
                        self.turn_forwards(dy, dx)
                        set_action('cast')
                        shot_direction = round((math.degrees(math.atan2(dy, dx)) + 45) / 45) % 8
                        self.projectiles.append(Projectile(self.x, self.y, False, shot_direction, self.style, SPELLS[self.style]["damage"]))
                        sound_manager.play_sound('fireball')
                    elif path_to_shot is not None:
                        self.path = a_star((int(round(self.x)), int(round(self.y))), path_to_shot, map_manager)
                        if self.path:
                            set_action('run')
                    else:
                        set_action('idle')

                else:
                    valid_tiles = []
                    walkable_cells = map_manager.maps[map_manager.current_map]['walkable_cells']
                    player_grid_x = int(round(player.x))
                    player_grid_y = int(round(player.y))

                    for ox in range(-4, 5):
                        for oy in range(-4, 5):
                            if ox == 0 and oy == 0:
                                continue
                            dist_to_tile = abs(ox) + abs(oy)
                            if 2 <= dist_to_tile <= 4:
                                check_pos = (player_grid_x + ox, player_grid_y + oy)
                                if check_pos in walkable_cells:
                                    valid_tiles.append(check_pos)

                    if valid_tiles:
                        old_x, old_y = self.x, self.y
                        target_tile = random.choice(valid_tiles)
                        sound_manager.play_sound('demon-teleport')
                        self.pending_effects.append(('teleport', old_x, old_y))
                        self.x, self.y = target_tile
                        self.pending_effects.append(('aura', self.x, self.y))
                        self.path = []
                        set_action('idle')
                        new_dx, new_dy = player.x - self.x, player.y - self.y
                        self.turn_forwards(new_dy, new_dx)

            if self.path:
                set_action('run')
                self.move(delta_time, enemies)
                if not self.path:
                    set_action('idle')
            elif self.current_action != 'cast':
                set_action('idle')
        else:
            set_action('idle')
            self.path = []

        update_rect(self)
        self.animate(delta_time)

    def update_voice(self, sound_manager, current_time):
        if self.dead:
            return

        if self.voice_channel.get_busy():
            return

        if current_time < self.next_voice_time:
            return

        voice_index = random.randint(1, self.voice_sound_count)
        voice_name = f"demon{voice_index}"
        voice_sound = sound_manager.sounds.get(voice_name)
        if voice_sound:
            self.voice_channel.play(voice_sound)

        self.next_voice_time = current_time + random.randint(self.min_voice_delay_ms, self.max_voice_delay_ms)

    def enemy_died(self, player, items, sound_manager, game_log):
        if self.dead:
            return

        self.voice_channel.stop()
        super().enemy_died(player, items, sound_manager, game_log)
        
    def check_pending_effects(self):
        return self.pending_effects if self.pending_effects else []