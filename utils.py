import math
import random
import pygame
from settings import *
from sound_data import *
from map_data import *
from display import prepare_level_name, draw_tooltip
from menu import loading_notice
from chest import Chest, generate_chest_content

def grid_to_isoscreen(x, y, offset_x, offset_y):
    screen_x = (x - y) * TILE_WIDTH // 2 + offset_x
    screen_y = (x + y) * TILE_HEIGHT // 2 + offset_y
    return screen_x, screen_y

def isoscreen_to_grid(sx, sy, offset_x, offset_y):
    sx -= offset_x
    sy -= offset_y
    half_tile_w = TILE_WIDTH / 2
    half_tile_h = TILE_HEIGHT / 2

    x = (sx / half_tile_w + sy / half_tile_h) / 2
    y = (sy / half_tile_h - sx / half_tile_w) / 2
    return int(round(x)), int(round(y))

def update_rect(self):
    screen_x, screen_y = grid_to_isoscreen(self.x, self.y, 0, 0)
    self.rect.topleft = (screen_x, screen_y)

def projectile_path(start, goal, map_manager):
    walkable_tiles = map_manager.maps[map_manager.current_map]['walkable_tiles']
    water_tiles = map_manager.maps[map_manager.current_map].get('water_tiles', set())
    projectile_passable = walkable_tiles.union(water_tiles)

    path = []
    x, y = start
    gx, gy = goal
    if start == goal:
        return [start]
    
    dx = gx - x
    dy = gy - y
    steps = max(abs(dx), abs(dy))

    for i in range(int(steps) + 1):
        nx = x + round(dx * i / steps)
        ny = y + round(dy * i / steps)
        if (nx, ny) not in projectile_passable:
            return []  # Path blocked
        path.append((nx, ny))

    return path

def get_interaction_destination(player, target_pos, map_manager, a_star_func, interaction_range=1):
    """
    Return (destination_tile, path) for a player who wants to interact with
    target_pos. The destination is the closest reachable walkable tile within
    interaction_range tiles of the target.

    Returns (None, []) if no valid interaction tile can be reached.
    """
    px, py = int(round(player.x)), int(round(player.y))
    tx, ty = target_pos
    map_data = map_manager.maps[map_manager.current_map]
    walkable_cells = map_data["walkable_cells"]
    candidates = []

    for y in range(ty - interaction_range, ty + interaction_range + 1):
        for x in range(tx - interaction_range, tx + interaction_range + 1):
            candidate = (x, y)

            if candidate not in walkable_cells:
                continue

            if max(abs(x - tx), abs(y - ty)) > interaction_range:
                continue

            path = a_star_func((px, py), candidate, map_manager)
            if path:
                candidates.append((len(path), candidate, path))
    if not candidates:
        return None, []

    _, destination, path = min(candidates, key=lambda result: result[0])
    return destination, path

def create_poi_badge():
    w, h = 48, 56
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2

    for r in range(18, 4, -3):
        alpha = int(25 * (1.0 - (r / 18.0)))
        pygame.draw.circle(surf, (240, 180, 50, alpha), (cx, cy), r)
    glyph_gold_bright = FONTS['POI'].render("!", True, (255, 230, 110))
    glyph_gold_mid    = FONTS['POI'].render("!", True, (215, 155, 35))
    glyph_dark_rim    = FONTS['POI'].render("!", True, (30, 20, 10))

    gw, gh = glyph_gold_bright.get_size()
    tx, ty = cx - (gw // 2), cy - (gh // 2)
    for ox in (-2, -1, 0, 1, 2):
        for oy in (-2, -1, 0, 1, 2):
            if ox != 0 or oy != 0:
                surf.blit(glyph_dark_rim, (tx + ox, ty + oy + 1))
    surf.blit(glyph_gold_mid, (tx, ty + 1))
    surf.blit(glyph_gold_bright, (tx, ty))

    return surf

def get_random_spawn_pos(min_x, max_x, min_y, max_y, map_data, min_distance=4, existing_positions=None):
    """
    Finds a random spawn position within the specified bounding box.
    Ensures the position is actually walkable and not too close to other enemies.
    """
    if existing_positions is None:
        existing_positions = set()
        
    walkable_cells = map_data.get("walkable_cells", [])
    valid_cells_in_bounds = [
        (x, y) for (x, y) in walkable_cells 
        if min_x <= x <= max_x and min_y <= y <= max_y
    ]
    
    if not valid_cells_in_bounds:
        valid_cells_in_bounds = list(walkable_cells)

    random.shuffle(valid_cells_in_bounds)

    for (x, y) in valid_cells_in_bounds:
        too_close = False
        for (ex, ey) in existing_positions:
            if math.hypot(x - ex, y - ey) < min_distance:
                too_close = True
                break
                
        if not too_close:
            existing_positions.add((x, y))
            return (x, y)

    best_fallback = valid_cells_in_bounds[0]
    existing_positions.add(best_fallback)
    return best_fallback

def get_current_map_exists(screen, mouse_pos, map_name, offset_x, offset_y):
    exit_tile = get_exit_at_screen_pos(mouse_pos, map_name, offset_x, offset_y)
    if exit_tile is None:
        return

    exit_data = LEVELS_DATA[map_name]["exits"][exit_tile]
    destination = exit_data["destination"]
    destination_title = LEVELS_DATA[destination]["title"]
    lines = ["Passage leading to", "", destination_title]
    draw_tooltip(screen, lines, mouse_pos)

def get_exit_at_screen_pos(mouse_pos, map_name, offset_x, offset_y, hitbox_width=160, hitbox_height=120):
    """
    Return the logical exit tile whose screen-space visual area contains
    mouse_pos. Exits are represented by map coordinates in LEVELS_DATA.
    """
    exits = LEVELS_DATA[map_name].get("exits", {})
    for exit_tile in exits:
        ex, ey = exit_tile
        screen_x, screen_y = grid_to_isoscreen(ex, ey, offset_x, offset_y)
        hitbox = pygame.Rect(screen_x - hitbox_width // 2, screen_y - hitbox_height + TILE_HEIGHT // 2, hitbox_width, hitbox_height)
        if hitbox.collidepoint(mouse_pos):
            return exit_tile
    return None


def get_exit_near_grid_pos(mouse_grid_pos, map_name, radius=1):
    """
    Fallback for exits without a custom screen hitbox or for map tiles
    around the visible entrance.
    """
    mx, my = mouse_grid_pos
    exits = LEVELS_DATA[map_name].get("exits", {})
    candidates = [exit_tile for exit_tile in exits if max(abs(exit_tile[0] - mx), abs(exit_tile[1] - my)) <= radius]
    if not candidates:
        return None
    return min(candidates, key=lambda tile: abs(tile[0] - mx) + abs(tile[1] - my))

def get_camera_center_offset(player):
    offset_x = SCREEN_WIDTH // 2 - (player.x - player.y) * TILE_WIDTH // 2
    offset_y = SCREEN_HEIGHT // 2 - (player.x + player.y) * TILE_HEIGHT // 2
    return offset_x, offset_y

def fade_transition(screen, clock, fade_in=False, duration=250):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill((0, 0, 0))

    steps = max(1, int(duration / (1000 / FPS)))
    for i in range(steps + 1):
        progress = i / steps
        alpha = int((1 - progress) * 255) if fade_in else int(progress * 255)
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.event.pump()
        clock.tick(FPS)

def get_spell_cooldown(player, spell):
    base_cooldown = player.spell_cooldown.get(spell, 1000)
    willpower = player.stats.get("willpower", 0)
    reduction_multiplier = 50.0 / (50.0 + max(0, willpower))
    reduced_cooldown = max(200, int(base_cooldown * max(0.40, reduction_multiplier)))
    return reduced_cooldown

def run_level_transition(screen, clock, player, sound_manager, map_manager, destination, Enemy, DemonBoss, enemies, chests, items, spawn_pos=None, use_teleport_pos=False):
    map_manager.maps[map_manager.current_map]["enemies"] = enemies
    map_manager.maps[map_manager.current_map]["chests"] = chests
    map_manager.maps[map_manager.current_map]["items"] = items
    player.path = []
    fade_transition(screen, clock, fade_in=False, duration=180)

    screen.fill(BACKGROUND)
    loading_notice(screen)
    pygame.display.flip()
    pygame.time.delay(350)
    map_data = map_manager.switch_map(destination, player)
    map_layers = map_data["layers"]
    prepare_level_name(destination)

    if use_teleport_pos:
        player.x, player.y = LEVELS_DATA[destination]["teleport_pos"]
    elif spawn_pos is not None:
        player.x, player.y = spawn_pos
    else:
        player.x, player.y = LEVELS_DATA[destination]["start_pos"]
    dest_map_dict = map_manager.maps[destination]

    if not dest_map_dict.get("is_initialized"):
        mx, mxx, my, mxy = LEVELS_DATA[destination]["enemies_range"]
        for en in LEVELS_DATA[destination].get("enemies", []):
            enemy_spawn_pos = get_random_spawn_pos(mx, mxx, my, mxy, map_data)
            if destination == "cursed" and en == "Demon":
                x_lo, x_hi = min(mx, mxx), max(mx, mxx)
                y_lo, y_hi = min(my, mxy), max(my, mxy)
                demon_spawn_pos = (random.randint(x_lo + 1, x_hi - 1), random.randint(y_lo + 1, y_hi - 1))
                dest_map_dict["enemies"].append(DemonBoss(demon_spawn_pos))
            else:
                dest_map_dict["enemies"].append(Enemy(enemy_spawn_pos, en, ENEMY_STATS[en]["STYLE"]))

        for chest_pos in LEVELS_DATA[destination].get("chests", []):
            dest_map_dict["chests"].add(Chest(chest_pos, generate_chest_content()))
        dest_map_dict["is_initialized"] = True

    enemies = dest_map_dict["enemies"]
    chests = dest_map_dict["chests"]
    items = dest_map_dict["items"]
    offset_x, offset_y = get_camera_center_offset(player)

    screen.fill(BACKGROUND)
    loading_notice(screen)
    pygame.display.flip()
    pygame.time.delay(100)
    fade_transition(screen, clock, fade_in=True, duration=120)
    sound_manager.play_music(LEVEL_MUSIC[destination], loops=-1, fade_ms=1200)

    return map_data, map_layers, enemies, chests, items, offset_x, offset_y

def check_for_level_switch(screen, clock, player, sound_manager, map_manager, map_data, map_layers, Enemy, DemonBoss, enemies, chests, items, locked_exit_tile):
    player_position = (int(player.x), int(player.y))
    if locked_exit_tile is not None and player_position != locked_exit_tile:
        locked_exit_tile = None
    exits = LEVELS_DATA[map_manager.current_map].get("exits", {})
    exit_data = exits.get(player_position)

    if exit_data is None or player_position == locked_exit_tile:
        return (map_data, map_layers, enemies, chests, items, None, None, False, locked_exit_tile)
    destination = exit_data["destination"]
    spawn_pos = exit_data["spawn_pos"]
    map_data, map_layers, enemies, chests, items, offset_x, offset_y = run_level_transition(screen, clock, player, sound_manager, map_manager, destination, Enemy, DemonBoss, enemies, chests, items, spawn_pos=spawn_pos, use_teleport_pos=False)
    locked_exit_tile = (int(player.x), int(player.y))
    return map_data, map_layers, enemies, chests, items, offset_x, offset_y, True, locked_exit_tile


def teleport_to_level(screen, clock, player, sound_manager, map_manager, destination, Enemy, DemonBoss, enemies, chests, items):
    map_data, map_layers, enemies, chests, items, offset_x, offset_y = run_level_transition(screen, clock, player, sound_manager, map_manager, destination, Enemy, DemonBoss, enemies, chests, items, use_teleport_pos=True)
    return map_data, map_layers, enemies, chests, items, offset_x, offset_y