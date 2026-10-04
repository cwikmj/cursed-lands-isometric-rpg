import sys
import pygame
import random
import math

from settings import *
from sound_data import *
from map import MapManager, draw_map, check_grid_aligned, get_visible_bounds
from map_data import LEVELS_DATA
from player import Player
from enemy import Enemy, DemonBoss
from projectile import Projectile
from spell import Spell, push_away
from burst import BurstEffect
from item import Item
from npc import NPC
from chest import *
from display import load_skill_icons, prepare_inventory_images, prepare_level_name, draw_ui, draw_tooltip, draw_level_name, draw_cooldown_bar, draw_inventory, draw_skill_tree, draw_teleports_menu, draw_npc_modal, draw_trade_menu, draw_boss_intro_modal, draw_boss_outro_screen, draw_credits_modal
from gamelog import GameLog
from sounds import SoundManager
from teleport import Teleport
from menu import main_menu, pause_menu, game_over, loading_notice
from utils import grid_to_isoscreen, isoscreen_to_grid, get_interaction_destination, create_poi_badge, get_current_map_exists, get_random_spawn_pos, run_level_transition, teleport_to_level, get_exit_at_screen_pos, get_exit_near_grid_pos
from pathfinding import a_star
from resource_path import resource_path

# SETUP
pygame.init()
window_icon = pygame.image.load(str(resource_path("assets/icon.png")))
pygame.display.set_icon(window_icon)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

screen.fill(BACKGROUND)
loading_notice(screen)
pygame.display.flip()
pygame.event.clear(pygame.MOUSEBUTTONDOWN)
pygame.event.clear(pygame.MOUSEBUTTONUP)
pygame.event.clear(pygame.MOUSEMOTION)
game_ready = False

MENU_BACKGROUND = pygame.image.load(resource_path('assets/menu.jpg')).convert()
MENU_BACKGROUND = pygame.transform.smoothscale(MENU_BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

# LOAD
player = Player(0, 0)
sound_manager = SoundManager()
for sound_name, filepath in ACTION_SOUNDS.items():
    sound_manager.load_sound(sound_name, filepath)
for sound_name, filepath in ENEMIES_SOUNDS.items():
    sound_manager.load_sound(sound_name, filepath)
for surface, sound_paths in FOOTSTEP_SOUNDS.items():
    for index, filepath in enumerate(sound_paths, start=1):
        sound_name = f"footstep-{surface}-{index}"
        sound_manager.load_sound(sound_name, filepath)

sound_manager.play_music(LEVEL_MUSIC['moor'], loops=-1, fade_ms=1200)
menu_result = main_menu(screen, clock, sound_manager, MENU_BACKGROUND)
if menu_result == "quit":
    pygame.quit()
    sys.exit()

map_manager = MapManager()
map_manager.load_map('cursed', resource_path('assets/maps/cursed.json'))
map_manager.load_map('icebound', resource_path('assets/maps/icebound.json'))
map_manager.load_map('ruins', resource_path('assets/maps/ruins.json'))
map_manager.load_map('cavern', resource_path('assets/maps/cavern.json'))
map_manager.load_map('moor', resource_path('assets/maps/moor.json'))
map_manager.load_map('cave', resource_path('assets/maps/cave.json'))
map_manager.load_map('ebonwood', resource_path('assets/maps/ebonwood.json'))
map_manager.switch_map('ebonwood', player)
map_data = map_manager.maps[map_manager.current_map]
map_layers = map_data["layers"]

Item.preload_images()
Projectile.preload(("firebolt", "icebolt"))
Spell.preload(SPELLS.keys())
BurstEffect.preload(BURSTS.keys())
prepare_inventory_images(Item.LOADED_IMAGES)
player_path = []
skill_icons = load_skill_icons()
game_log = GameLog()

map_manager.switch_map("ebonwood", player)
map_data = map_manager.maps[map_manager.current_map]
map_layers = map_data["layers"]
prepare_level_name(map_manager.current_map)
starting_map_dict = map_manager.maps[map_manager.current_map]
sound_manager.play_music(LEVEL_MUSIC[map_manager.current_map], loops=-1, fade_ms=1200)

if not starting_map_dict.get("is_initialized"):
    bx, bxx, by, bxy = LEVELS_DATA[map_manager.current_map]["enemies_range"]
    spawned_positions = set()
    for en in LEVELS_DATA[map_manager.current_map].get("enemies", []):
        spawn_pos = get_random_spawn_pos(bx, bxx, by, bxy, starting_map_dict, min_distance=4, existing_positions=spawned_positions)
        starting_map_dict["enemies"].append(Enemy(spawn_pos, en, ENEMY_STATS[en]["STYLE"]))
    for ch in LEVELS_DATA[map_manager.current_map].get("chests", []):
        starting_map_dict["chests"].add(Chest(ch, generate_chest_content()))
    starting_map_dict["is_initialized"] = True

enemies = starting_map_dict["enemies"]
chests = starting_map_dict["chests"]
items = starting_map_dict["items"]
spells = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
bursts = pygame.sprite.Group()
teleports = pygame.sprite.Group()
npcs = pygame.sprite.Group()
npcs.add(NPC(-11, 70, 'trader_1', 'Johan', 'ebonwood', 'npc2'))
npcs.add(NPC(5, 74, 'trader_2', 'Nuka', 'ebonwood', 'npc1'))
npcs.add(NPC(-46, 61, 'trader_3', 'Carth Mago', 'moor', 'npc2'))
POI_BADGE = create_poi_badge()
for level in LEVELS_DATA:
    teleport_pos = LEVELS_DATA[level]["teleport_pos"]
    teleports.add(Teleport(teleport_pos[0], teleport_pos[1], level, LEVELS_DATA[level]["title"], level))

# CAMERA INIT
offset_x = SCREEN_WIDTH // 2 - (player.x - player.y) * TILE_WIDTH // 2
offset_y = SCREEN_HEIGHT // 2 - (player.x + player.y) * TILE_HEIGHT // 2

game_ready = True
pygame.event.clear(pygame.MOUSEBUTTONDOWN)
pygame.event.clear(pygame.MOUSEBUTTONUP)
pygame.event.clear(pygame.MOUSEMOTION)

# GAME LOOP
running = True
draw_ui_screen = True
skill_tree = False
inventory = False
teleport_tree = False
current_tp = None
chest_modal = False
npc_modal = False
trade_modal = False
current_chest = None
pending_chest = None
pending_spell = None
pending_npc = None 
pending_interaction = None
locked_exit_tile = None
boss_intro_modal = False
boss_fight_triggered = False
current_boss = None
boss_outro_pending = False
boss_outro_screen = False
boss_outro_start_time = 0
boss_outro_shown = False
credits_modal = False
last_time = pygame.time.get_ticks()
last_caption_update = 0
last_footstep_time = 0

while running:
    current_time = pygame.time.get_ticks()
    delta_time = (current_time - last_time) / 1000.0
    last_time = current_time
    mx, my = pygame.mouse.get_pos()
    tx, ty = isoscreen_to_grid(mx, my, offset_x, offset_y)

    visible_enemies = [e for e in enemies if e.get_dist_from_player(player) < DISTANCE_TO_RENDER]
    visible_npcs = [npc for npc in npcs if map_manager.current_map == npc.level and npc.get_dist_from_player(player) < DISTANCE_TO_RENDER]

    if pending_spell and not player_path:
        spell, ex, ey, is_player, target = pending_spell
        tx, ty = (player.x, player.y) if is_player else (ex, ey)
        if spell != 'teleport':
            player.attack((ex, ey), 3)
        spells.add(player.cast_spell(spell, (tx, ty), target))
        sound_manager.play_sound(spell)
        pending_spell = None
    if pending_npc is not None and not player_path:
        if pending_npc.get_dist_from_player(player) <= 3:
            current_npc = pending_npc
            current_npc.dialogue_start_time = pygame.time.get_ticks()
            current_npc.dialogue_fully_revealed = False
            npc_modal = True
            if player.health < player.max_health or player.mana < player.max_mana:
                sound_manager.play_sound('drink')
                player.health = player.max_health
                player.mana = player.max_mana
        pending_npc = None
    if pending_chest is not None and not player_path:
        if pending_chest in chests and not pending_chest.opened and pending_chest.get_dist_from_player(player) <= CHEST_INTERACTION_RANGE:
            chest_modal = True
            current_chest = pending_chest
            sound_manager.play_sound('chest')

        pending_chest = None
    if pending_interaction and not player_path:
        interaction_type, target = pending_interaction
        if interaction_type == "exit":
            exit_tile = target
            exit_data = LEVELS_DATA[map_manager.current_map]["exits"][exit_tile]
            map_data, map_layers, enemies, chests, items, offset_x, offset_y = run_level_transition(screen, clock, player, sound_manager, map_manager, exit_data["destination"], Enemy, DemonBoss, enemies, chests, items, spawn_pos=exit_data["spawn_pos"], use_teleport_pos=False)
            player_path = []
            pending_chest = None
            pending_spell = None
            locked_exit_tile = (int(player.x), int(player.y))
        pending_interaction = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if boss_outro_pending or boss_outro_screen:
                    continue
                if skill_tree or inventory or teleport_tree or npc_modal or trade_modal or boss_intro_modal:
                    skill_tree = False
                    inventory = False
                    teleport_tree = False
                    chest_modal = False
                    npc_modal = False
                    trade_modal = False
                    current_chest = None
                    current_npc = None
                    boss_intro_modal = False
                    current_boss = None
                    pending_chest = None
                    pending_interaction = None
                    pending_npc = None
                else:
                    last_screen_surface = screen.copy()
                    player_path = []
                    pending_chest = None
                    pending_interaction = None
                    sound_manager.play_sound('pause')
                    pause_menu(screen, last_screen_surface, sound_manager)
            elif event.key == pygame.K_t and not chest_modal and not npc_modal and not trade_modal and not boss_intro_modal and not boss_outro_screen and not credits_modal:
                skill_tree = not skill_tree
                teleport_tree = False
            elif event.key == pygame.K_i and not chest_modal and not npc_modal and not trade_modal and not boss_intro_modal and not boss_outro_screen and not credits_modal:
                inventory = not inventory
                teleport_tree = False
            elif event.key == pygame.K_h and player.can_drink('health'):
                player.potion_animation('health')
                sound_manager.play_sound('drink')
            elif event.key == pygame.K_m and player.can_drink('mana'):
                player.potion_animation('mana')
                sound_manager.play_sound('drink')

            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7):
                skill_map = {
                    pygame.K_1: 'kick',
                    pygame.K_2: 'clash',
                    pygame.K_3: 'whirlwind',
                    pygame.K_4: 'firebolt',
                    pygame.K_5: 'lightning',
                    pygame.K_6: 'teleport',
                    pygame.K_7: 'forcepush'
                }
                pressed_skill = skill_map.get(event.key)
                if pressed_skill in player.skills:
                    player.current_skill = pressed_skill

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and npc_modal:
            if not current_npc.dialogue_fully_revealed:
                current_npc.dialogue_fully_revealed = True
                sound_manager.play_sound('button')
            else:
                trade_btn, close_btn = draw_npc_modal(screen, current_npc, current_time)
                sound_manager.play_sound('button')
                if trade_btn and trade_btn.collidepoint(event.pos):
                    npc_modal = False
                    trade_modal = True
                elif close_btn and close_btn.collidepoint(event.pos):
                    npc_modal = False
                    current_npc = None
            continue
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and boss_intro_modal:
            if not current_boss.dialogue_fully_revealed:
                current_boss.dialogue_fully_revealed = True
            else:
                boss_intro_modal = False
                current_boss = None
            continue
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and boss_outro_screen:
            quit_button = draw_boss_outro_screen(screen, current_time, boss_outro_start_time)
            if quit_button and quit_button.collidepoint(event.pos):
                boss_outro_screen = False
                boss_outro_pending = False
                credits_modal = True
            continue
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and credits_modal:
            close_button = draw_credits_modal(screen)
            if close_button and close_button.collidepoint(event.pos):
                running = False
            continue
        elif event.type == pygame.MOUSEBUTTONDOWN and game_ready:
            if trade_modal:
                MODAL_WIDTH, MODAL_HEIGHT = 800, 500
                MODAL_X, MODAL_Y = (SCREEN_WIDTH - MODAL_WIDTH) // 2, (SCREEN_HEIGHT - MODAL_HEIGHT) // 2
                trade_rect = pygame.Rect(MODAL_X, MODAL_Y, MODAL_WIDTH, MODAL_HEIGHT)
                if not trade_rect.collidepoint(event.pos):
                    trade_modal = False
                    current_npc = None
                    continue

            if event.button == 1:
                if skill_tree:
                    skill_tree_rect = pygame.Rect(SKILL_INV_X, SKILL_INV_Y, SKILL_INV_WIDTH, SKILL_INV_HEIGHT)
                    if not skill_tree_rect.collidepoint(event.pos):
                        skill_tree = False
                        continue

                elif inventory:
                    inventory_rect = pygame.Rect(INVENTORY_X, SKILL_INV_Y, SKILL_INV_WIDTH, SKILL_INV_HEIGHT)
                    if not inventory_rect.collidepoint(event.pos):
                        inventory = False
                        continue
                
            if skill_tree or inventory or chest_modal or npc_modal or trade_modal:
                continue
            if teleport_tree:
                if mx > SKILL_INV_X + SKILL_INV_WIDTH:
                    teleport_tree = False
                else:
                    continue

            if not skill_tree and not inventory and not teleport_tree and not chest_modal and not npc_modal and not trade_modal and not boss_intro_modal and not boss_outro_screen and not credits_modal:
                chest_clicked = False
                for chest in chests:
                    if event.button != 1:
                        continue
                    if chest.opened:
                        continue
                    if not chest.is_hovered(event.pos, offset_x, offset_y):
                        continue
                    chest_clicked = True
                    distance = chest.get_dist_from_player(player)
                    if distance <= CHEST_INTERACTION_RANGE:
                        player_path = []
                        pending_chest = None
                        chest_modal = True
                        current_chest = chest
                        sound_manager.play_sound('chest')
                    else:
                        destination, path = get_interaction_destination(player, (chest.x, chest.y), map_manager, a_star, 1)
                        if destination is not None:
                            player_path = path[1:] if len(path) > 1 else []
                            pending_chest = chest
                    break
                enemy_clicked = False
                for npc in visible_npcs:
                    if event.button == 1 and npc.is_hovered((tx, ty)):
                        distance = npc.get_dist_from_player(player)
                        if distance <= 3:
                            player_path = []
                            pending_npc = None
                            current_npc = npc
                            current_npc.dialogue_start_time = pygame.time.get_ticks()
                            current_npc.dialogue_fully_revealed = False
                            npc_modal = True
                            if player.health < player.max_health or player.mana < player.max_mana:
                                sound_manager.play_sound('drink')
                                player.health = player.max_health
                                player.mana = player.max_mana
                        else:
                            destination, path = get_interaction_destination(player, (npc.x, npc.y), map_manager, a_star, 2)
                            if destination is not None:
                                player_path = path[1:] if len(path) > 1 else []
                                pending_npc = npc
                                pending_chest = None
                                pending_interaction = None
                        enemy_clicked = True
                        break

                if event.button == 3 and player.can_cast_spell(player.current_skill, game_log):
                    if player.current_skill == 'teleport' and (player.x, player.y) != (tx, ty) and (tx, ty) in map_data['walkable_cells']:
                        player.x, player.y = tx, ty
                        player.start_spell_cooldown(player.current_skill)
                        pending_spell = ('teleport', player.x, player.y, True, player)
                        sound_manager.play_sound(player.current_skill)
                        player_path = []
                        for enemy in visible_enemies:
                            enemy.path = []
                        continue
                    elif player.current_skill == 'whirlwind':
                        player.start_spell_cooldown(player.current_skill)
                        spells.add(player.cast_spell(player.current_skill, (player.x, player.y)))
                        sound_manager.play_sound(player.current_skill)
                        for enemy in visible_enemies:
                            distance = enemy.get_dist_from_player(player)
                            if distance < 4:
                                player.attack((enemy.x, enemy.y), event.button)
                        enemy_clicked = True
                        continue

                for enemy in visible_enemies:
                    if enemy.is_hovered((mx, my), offset_x, offset_y) and not enemy.dead:
                        if event.button == 1 and enemy.get_dist_from_player(player) < ATTACK_RANGE:
                            player.target_enemy = enemy
                            enemy_clicked = True
                            player.attack((enemy.x, enemy.y), event.button)
                            sound_manager.play_sound(f'attack{random.randint(1, 4)}')
                            break
                        elif event.button == 3 and player.can_cast_spell(player.current_skill, game_log):
                            enemy_clicked = True
                            player.start_spell_cooldown(player.current_skill)
                            if player.current_skill == 'lightning':
                                player.attack((enemy.x, enemy.y), event.button)
                                spells.add(player.cast_spell(player.current_skill, (enemy.x, enemy.y), enemy))
                                sound_manager.play_sound(player.current_skill)
                                pending_spell = ('shock', enemy.x, enemy.y, False, enemy)
                                break
                            elif player.current_skill == 'forcepush':
                                spells.add(player.cast_spell(player.current_skill, (player.x, player.y)))
                                for enemy in visible_enemies:
                                    distance = enemy.get_dist_from_player(player)
                                    if distance < 3:
                                        player.attack((enemy.x, enemy.y), event.button)
                                break
                            elif player.current_skill == 'firebolt':
                                check_player_aligned = check_grid_aligned(player, enemy, map_data)
                                if check_player_aligned is True:
                                    player.attack((enemy.x, enemy.y), event.button)
                                    spells.add(player.cast_spell('fireball', (player.x, player.y)))
                                    sound_manager.play_sound('fireball')
                                elif check_player_aligned is not None:
                                    target_x, target_y = check_player_aligned
                                    path = a_star((int(round(player.x)), int(round(player.y))), (target_x, target_y), map_manager)
                                    if path:
                                        player_path = path[1:] if len(path) > 1 else []
                                        pending_spell = ('fireball', enemy.x, enemy.y, True, None)
                                break
                            elif player.current_skill in ('kick', 'clash'):
                                sound_manager.play_sound(player.current_skill)
                                player.target_enemy = enemy
                                enemy_clicked = True
                                player.attack((enemy.x, enemy.y), event.button)
                                break
                        break

            if not enemy_clicked and event.button == 1:
                item_clicked = False
                for item in items:
                    if item.is_hovered((mx, my)) and item.bounced:
                        distance = item.get_dist_from_player(player)
                        if distance < 2:
                            sound_manager.play_sound('item-pick')
                            item.pick_up(player, game_log)
                            items.remove(item)
                        else:
                            item.targeted_for_pickup = True
                            path = a_star((int(round(player.x)), int(round(player.y))), (tx, ty), map_manager)
                            if path:
                                player_path = path[1:] if len(path) > 1 else []
                        item_clicked = True
                        break

            if event.button == 1 and not chest_clicked:
                clicked_exit = get_exit_at_screen_pos(event.pos, map_manager.current_map, offset_x, offset_y)
                if clicked_exit is None:
                    clicked_exit = get_exit_near_grid_pos((tx, ty), map_manager.current_map, radius=1)

                if clicked_exit is not None:
                    destination, path = get_interaction_destination(player, clicked_exit, map_manager, a_star, interaction_range=1)
                    if destination is not None:
                        player_path = path[1:] if len(path) > 1 else []
                        pending_interaction = ("exit", clicked_exit)
                    continue

            if event.button == 1 and not enemy_clicked and not item_clicked and not chest_clicked and not chest_modal and my < SCREEN_HEIGHT - UI_HEIGHT:
                if teleport_tree:
                    continue 
                pending_chest = None
                pending_spell = None
                pending_npc = None
                if (tx, ty) in map_data['walkable_cells']:
                    path = a_star((int(round(player.x)), int(round(player.y))), (tx, ty), map_manager)
                    if path:
                        player_path = path[1:] if len(path) > 1 else []
                    else:
                        player_path = []
                else:
                    player_path = []

                tp_clicked = False
                for tp in teleports:
                    if tp.dest_map == map_manager.current_map and tp.is_hovered((tx, ty)):
                        tp_clicked = True
                        if tp.get_dist_from_player(player) < 3:
                            if not tp.active:
                                tp.active = True
                                sound_manager.play_sound('waypoint')
                                game_log.add_line(f"Waypoint '{tp.name}' activated!")
                                active_waypoints = sum(1 for t in teleports if t.active)
                                if active_waypoints == 7:
                                    player.skill_points += 1
                                    game_log.add_line(f"All waypoints activated!")
                                    game_log.add_line(f"You get 1 Extra Skill Point!")
                            else:
                                teleport_tree = True
                                current_tp = tp
                        else:
                            path = a_star((int(round(player.x)), int(round(player.y))), (tx, ty), map_manager)
                            if path:
                                player_path = path[1:] if len(path) > 1 else []
                        break 
                if tp_clicked:
                    continue

    # CENTER CAMERA
    target_offset_x = SCREEN_WIDTH // 2 - (player.x - player.y) * TILE_WIDTH // 2
    target_offset_y = SCREEN_HEIGHT // 2 - (player.x + player.y) * TILE_HEIGHT // 2
    offset_x += (target_offset_x - offset_x) * PLAYER_SPEED * delta_time
    offset_y += (target_offset_y - offset_y) * PLAYER_SPEED * delta_time

    # DRAW
    screen.fill(BACKGROUND)
    visible_bounds = get_visible_bounds(map_manager, offset_x, offset_y)
    draw_map(map_manager, offset_x, offset_y, screen, map_data["layers_below"], visible_bounds)

    for tp in teleports:
        if tp.dest_map == map_manager.current_map:
            tp.draw(screen, offset_x, offset_y)
            tp.update(delta_time)

    if not boss_intro_modal and not boss_outro_pending and not boss_outro_screen:
        for enemy in visible_enemies:
            if (isinstance(enemy, DemonBoss) and not enemy.dead and not enemy.intro_shown and enemy.get_dist_from_player(player) <= 10):
                enemy.intro_shown = True
                enemy.dialogue_start_time = current_time
                enemy.dialogue_fully_revealed = False
                current_boss = enemy
                boss_intro_modal = True
                boss_fight_triggered = True
                player_path = []
                pending_spell = None
                break

    if not boss_intro_modal and not boss_outro_screen:
        for enemy in visible_enemies:
            enemy.update(delta_time, player, items, map_manager, sound_manager, game_log, visible_enemies)
            enemy.draw(screen, offset_x, offset_y)

            if enemy.projectiles:
                projectiles.add(enemy.check_projectiles_to_fire())
                enemy.projectiles = []

            if isinstance(enemy, DemonBoss):
                for effect_name, ex, ey in enemy.check_pending_effects():
                    if effect_name == "aura":
                        spells.add(player.cast_spell("aura", (ex, ey), enemy))
                enemy.pending_effects = []

    if not boss_outro_shown and not boss_outro_pending and not boss_outro_screen and not credits_modal:
        for enemy in enemies:
            if isinstance(enemy, DemonBoss) and enemy.dead:
                final_death_frame = len(enemy.actions["die"][enemy.current_direction]) - 1
                if enemy.current_action == "die" and enemy.current_frame >= final_death_frame:
                    boss_outro_pending = True
                    boss_outro_start_time = current_time
                    player_path = []
                    pending_spell = None
                    break

    if boss_outro_pending and not credits_modal and current_time - boss_outro_start_time >= 3000:
        boss_outro_pending = False
        boss_outro_screen = True
        boss_outro_start_time = current_time
        player_path = []
        pending_spell = None

    for item in items:
        item_dist = item.get_dist_from_player(player)
        if item_dist < DISTANCE_TO_RENDER:
            item.update(delta_time)
            item.draw(screen, offset_x, offset_y, (mx, my))
            if item_dist < ATTACK_RANGE and item.targeted_for_pickup:
                sound_manager.play_sound('item-pick')
                item.pick_up(player, game_log)
                items.remove(item)

    player.update(delta_time, player_path)
    if player_path:
        if current_time - last_footstep_time >= FOOTSTEP_INTERVAL_MS:
            level_surface = LEVELS_DATA[map_manager.current_map].get("surface", "mesh")
            variation_count = len(FOOTSTEP_SOUNDS.get(level_surface, []))
            if variation_count > 0:
                variation = random.randint(1, variation_count)
                sound_manager.play_sound(f"footstep-{level_surface}-{variation}")
            last_footstep_time = current_time
    else:
        last_footstep_time = 0
    player.draw(screen, offset_x, offset_y)

    for projectile in list(projectiles):
        projectile.update(delta_time, map_data)

        if projectile.wall_hit:
            projectile.hit(bursts, projectile)
            sound_manager.play_sound('icebolt' if projectile.action == 'icebolt' else 'fireball-burst')
            projectiles.remove(projectile)
            continue
        projectile.draw(screen, offset_x, offset_y)
        if projectile.from_player:
            hit_enemies = pygame.sprite.spritecollide(projectile, visible_enemies, False)
            for enemy in hit_enemies:
                if enemy.health > 0:
                    enemy.health -= projectile.damage
                    projectile.hit(bursts, enemy)
                    projectiles.remove(projectile)
                    enemy.triggered = True
                    if enemy.health < 1:
                        enemy.enemy_died(player, items, sound_manager, game_log)
                    sound_manager.play_sound('fireball-burst')
                    break
        else:
            hit_player = pygame.sprite.spritecollide(projectile, [player], False)
            if player in hit_player:
                shot_sound = ('icebolt' if projectile.action == 'icebolt' else 'fireball-burst')
                sound_manager.play_sound(shot_sound)
                player.take_damage(projectile.damage)
                projectile.hit(bursts, player)
                projectiles.remove(projectile)

    for burst in list(bursts):
        burst.update(delta_time)
        burst.draw(screen, offset_x, offset_y)
        if not burst.alive:
            bursts.remove(burst)

    for spell in spells:
        spell.update(delta_time)
        spell.draw(screen, offset_x, offset_y)
        for enemy in visible_enemies:
            if enemy.x == spell.x and enemy.y == spell.y:
                enemy.health -= spell.damage
                enemy.triggered = True
                if enemy.health < 1:
                    enemy.enemy_died(player, items, sound_manager, game_log)
                break
        if not spell.alive:
            if spell.action == 'forcepush':
                spells.add(player.cast_spell("quake", (player.x, player.y)))
                sound_manager.play_sound(spell.action)
                for enemy in visible_enemies:
                    distance = enemy.get_dist_from_player(player)
                    if distance < 3:
                        push_away(enemy, player, map_data)
            if spell.action == 'fireball':
                projectiles.add(player.fire_projectile("firebolt"))
            spells.remove(spell)

    for npc in visible_npcs:
        npc.update(delta_time)
        npc.draw(screen, offset_x, offset_y)
        npc_dist = npc.get_dist_from_player(player)
        if 3 <= npc_dist < 12 and not npc_modal:
            npc_screen_x, npc_screen_y = grid_to_isoscreen(npc.x, npc.y, offset_x, offset_y)
            bounce = math.sin(current_time * 0.005) * 4            
            sprite_h = npc.image.get_height() if hasattr(npc, 'image') else 64
            badge_x = npc_screen_x - (POI_BADGE.get_width() // 2)
            badge_y = (npc_screen_y - sprite_h) - POI_BADGE.get_height() - 4 + bounce            
            screen.blit(POI_BADGE, (badge_x, badge_y))
        if npc.is_hovered((tx, ty)) and not npc_modal:
            npc_screen_x, npc_screen_y = grid_to_isoscreen(npc.x, npc.y, offset_x, offset_y)
            draw_tooltip(screen, npc.get_tooltip_text(), (npc_screen_x, npc_screen_y - 60))

    for chest in chests:
        if chest.is_hovered((mx, my), offset_x, offset_y) and not chest_modal:
            draw_tooltip(screen, chest.get_tooltip_text(), grid_to_isoscreen(chest.x, chest.y, offset_x, offset_y))

    game_log.update()
    draw_map(map_manager, offset_x, offset_y, screen, map_data["layers_above"], visible_bounds)
    draw_cooldown_bar(screen, player)
    if draw_ui_screen:
        draw_ui(screen, player, skill_icons, game_log)
    get_current_map_exists(screen, (mx, my), map_manager.current_map, offset_x, offset_y)

    if inventory:
        draw_inventory(screen, player, Item.LOADED_IMAGES, items, sound_manager)
    if skill_tree:
        draw_skill_tree(screen, player, skill_icons, sound_manager)
    if teleport_tree:
        target_map = draw_teleports_menu(screen, current_tp, teleports, mx, my)
        if target_map:
            teleport_tree = False
            map_data, map_layers, enemies, chests, items, offset_x, offset_y = teleport_to_level(screen, clock, player, sound_manager, map_manager, target_map, Enemy, DemonBoss, enemies, chests, items)
            player_path = []
            pending_spell = None
            pending_chest = None
            pending_interaction = None
            pending_npc = None
            locked_exit_tile = None
    else:
        draw_level_name(screen, map_manager.current_map)

    if npc_modal:
        trade_btn, close_btn = draw_npc_modal(screen, current_npc, current_time)
    if trade_modal:
        should_close = draw_trade_menu(screen, player, current_npc, Item.LOADED_IMAGES, sound_manager)
        if should_close:
            sound_manager.play_sound('button')
            trade_modal = False
            current_npc = None
    if chest_modal:
        ok_button = draw_chest_modal(screen, current_chest)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and ok_button.collidepoint(event.pos):
            opened_chest = current_chest
            sound_manager.play_sound('item-pick')
            opened_chest.collect_items(player, map_layers, game_log)
            chests.remove(opened_chest)
            current_chest = None
            chest_modal = False
    if boss_fight_triggered:
        sound_manager.play_sound('demon0')
    if boss_intro_modal:
        boss_fight_triggered = False
        draw_boss_intro_modal(screen, current_boss, current_time)
    if boss_outro_screen:
        draw_boss_outro_screen(screen, current_time, boss_outro_start_time)
    if credits_modal:
        draw_ui_screen = False
        draw_credits_modal(screen)

    pygame.display.flip()
    clock.tick(FPS)

    if current_time - last_caption_update >= 1000:
        pygame.display.set_caption(f'CURSED LANDS - a cwikmj RPG game -- {clock.get_fps():.1f}')
        last_caption_update = current_time

    if player.health < 1 and player.death_animation_done:
        last_screen_surface = screen.copy()
        sound_manager.stop_music()
        sound_manager.play_sound('die')
        sound_manager.play_sound('death')
        result = game_over(screen, last_screen_surface, enemies)
        if result == "restart":
            player.respawn()
            player_path = []
            pending_spell = None
            map_data, map_layers, enemies, chests, items, offset_x, offset_y = teleport_to_level(screen, clock, player, sound_manager, map_manager, "ebonwood", Enemy, DemonBoss, enemies, chests, items)
        else:
            running = False
            pygame.quit()
            sys.exit()

pygame.quit()
sys.exit()