import pygame
import json
import os
from settings import *
from map_data import LEVELS_DATA
from utils import isoscreen_to_grid, grid_to_isoscreen
from resource_path import resource_path


class MapManager:
    def __init__(self):
        self.maps = {}
        self.current_map = None
        self.TILE_CACHES = {}
        self._viewport_cache = {}

    def load_map(self, map_name, path):
        if map_name in self.maps:
            return
        
        self.TILE_CACHES[map_name] = {}
        with open(path, "r") as f:
            map_data = json.load(f)

        tilesets = map_data["tilesets"]
        layers = []

        for ts in tilesets:
            firstgid = ts["firstgid"]
            filename = os.path.basename(ts["source"])
            image = pygame.image.load(resource_path(os.path.join("assets/maps/", filename))).convert_alpha()
            if filename in ['rock-walls.png', 'ruins.png', 'snow.png']:
                image.set_colorkey((0, 0, 0))

            tiles_x = image.get_width() // TILE_WIDTH
            tiles_y = image.get_height() // TILE_HEIGHT

            for i in range(tiles_y * tiles_x):
                gid = firstgid + i
                x = (i % tiles_x) * TILE_WIDTH
                y = (i // tiles_x) * TILE_HEIGHT
                rect = pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)
                self.TILE_CACHES[map_name][gid] = image.subsurface(rect).copy()

        for layer in map_data["layers"]:
            chunks = layer["chunks"]
            min_x = min(chunk["x"] for chunk in chunks)
            min_y = min(chunk["y"] for chunk in chunks)
            max_x = max(chunk["x"] + chunk["width"] for chunk in chunks)
            max_y = max(chunk["y"] + chunk["height"] for chunk in chunks)
            width = max_x - min_x
            height = max_y - min_y
            grid = [[0 for _ in range(width)] for _ in range(height)]

            for chunk in chunks:
                cx = chunk["x"] - min_x
                cy = chunk["y"] - min_y
                for row in range(chunk["height"]):
                    for col in range(chunk["width"]):
                        idx = row * chunk["width"] + col
                        gid = chunk["data"][idx]
                        grid[cy + row][cx + col] = gid

            layers.append({
                "data": grid,
                "offset_x": min_x,
                "offset_y": min_y,
                "width": width,
                "height": height,
                "name": layer["name"]
            })

        layers_below = [l for l in layers if l["name"] != "props-high"]
        layers_above = [l for l in layers if l["name"] == "props-high"]

        if map_name not in self.maps:
            self.maps[map_name] = {
                "layers": layers,
                "layers_below": layers_below,
                "layers_above": layers_above,
                "bounds": self.get_map_bounds(layers),
                "walkable_tiles": LEVELS_DATA[map_name]["walkable_tiles"],
                "walkable_cells": [],
                "enemies": [],
                "items": pygame.sprite.Group(),
                "chests": pygame.sprite.Group(),
                "is_initialized": False
            }
        else:
            self.maps[map_name]["layers"] = layers
            self.maps[map_name]["layers_below"] = layers_below
            self.maps[map_name]["layers_above"] = layers_above
            self.maps[map_name]["bounds"] = self.get_map_bounds(layers)
            self.maps[map_name]["walkable_tiles"] = LEVELS_DATA[map_name]["walkable_tiles"]

        self.maps[map_name]["walkable_cells"] = self.get_walkable_positions(map_name)

    def switch_map(self, map_name, player):
        self.current_map = map_name
        map_data = self.maps[map_name]
        player.x = LEVELS_DATA[map_name]["start_pos"][0]
        player.y = LEVELS_DATA[map_name]["start_pos"][1]
        self._viewport_cache.pop(map_name, None)
        return map_data

    def get_map_bounds(self, layers):
        min_x = min(layer["offset_x"] for layer in layers)
        min_y = min(layer["offset_y"] for layer in layers)
        max_x = max(layer["offset_x"] + layer["width"] for layer in layers)
        max_y = max(layer["offset_y"] + layer["height"] for layer in layers)
        return min_x, min_y, max_x, max_y

    def get_walkable_positions(self, map_name):
        map_data = self.maps[map_name]
        x1, y1, x2, y2 = self.get_map_bounds(map_data["layers"])
        wt = set(map_data["walkable_tiles"]) | {0}
        walkable = set()

        for y in range(y1, y2):
            for x in range(x1, x2):
                valid = True
                has_tile = False
                for l in map_data["layers"]:
                    if l["name"] != 'props-high':
                        ly, lx = y - l["offset_y"], x - l["offset_x"]
                        if 0 <= ly < l["height"] and 0 <= lx < l["width"]:
                            val = l["data"][ly][lx]
                            if val != 0:
                                has_tile = True
                            if val not in wt:
                                valid = False
                                break
                if has_tile and valid:
                    walkable.add((x, y))
        return walkable


def get_visible_bounds(map_manager, offset_x, offset_y, margin_tiles=2):
    """
    Compute the visible grid-tile range ONCE per frame, shared across both
    draw_map() calls (below-layer pass and above-layer/props-high pass).

    Caches on rounded camera offset so during the smooth camera lerp -
    which moves the camera by a fraction of a pixel most frames - we reuse
    the previous frame's bounds instead of recomputing 4x isoscreen_to_grid
    calls + min/max every single frame.
    """
    map_name = map_manager.current_map
    key = (round(offset_x / 4) * 4, round(offset_y / 4) * 4)

    cached = map_manager._viewport_cache.get(map_name)
    if cached is not None and cached["key"] == key:
        return cached["bounds"]

    c1 = isoscreen_to_grid(0, 0, offset_x, offset_y)
    c2 = isoscreen_to_grid(SCREEN_WIDTH, 0, offset_x, offset_y)
    c3 = isoscreen_to_grid(0, SCREEN_HEIGHT, offset_x, offset_y)
    c4 = isoscreen_to_grid(SCREEN_WIDTH, SCREEN_HEIGHT, offset_x, offset_y)

    xs = (c1[0], c2[0], c3[0], c4[0])
    ys = (c1[1], c2[1], c3[1], c4[1])

    min_gx, max_gx = min(xs) - margin_tiles, max(xs) + margin_tiles
    min_gy, max_gy = min(ys) - margin_tiles, max(ys) + margin_tiles

    bounds = (min_gx, max_gx, min_gy, max_gy)
    map_manager._viewport_cache[map_name] = {"key": key, "bounds": bounds}
    return bounds


def draw_map(map_manager, offset_x, offset_y, screen, layers_to_draw, visible_bounds=None):
    """
    `visible_bounds` should be computed ONCE per frame via get_visible_bounds()
    and passed to both the below-layers call and the above-layers call.
    Falls back to computing it internally if not provided (keeps this
    function usable standalone, e.g. in fade_transition/menu contexts).
    """
    if visible_bounds is None:
        visible_bounds = get_visible_bounds(map_manager, offset_x, offset_y)

    min_gx, max_gx, min_gy, max_gy = visible_bounds

    blit = screen.blit
    cache = map_manager.TILE_CACHES[map_manager.current_map]
    tw2 = TILE_WIDTH // 2

    for layer in layers_to_draw:
        data = layer["data"]
        ox, oy = layer["offset_x"], layer["offset_y"]

        start_y = max(0, int(min_gy - oy))
        end_y = min(len(data), int(max_gy - oy + 1))
        start_x = max(0, int(min_gx - ox))
        end_x = min(len(data[0]), int(max_gx - ox + 1))

        for y in range(start_y, end_y):
            row_data = data[y]
            real_y = y + oy

            for x in range(start_x, end_x):
                gid = row_data[x]
                if gid == 0:
                    continue

                surf = cache.get(gid)
                if surf:
                    sx, sy = grid_to_isoscreen(x + ox, real_y, offset_x, offset_y)
                    blit(surf, (sx - tw2, sy))

def check_grid_aligned(player, enemy, map_data):
    px, py = int(round(player.x)), int(round(player.y))
    ex, ey = int(round(enemy.x)), int(round(enemy.y))

    if px == ex or py == ey or abs(px - ex) == abs(py - ey):
        return True

    max_radius = max(abs(px - ex), abs(py - ey)) + 3
    aligned_tiles = []

    for dx in range(-max_radius, max_radius + 1):
        for dy in range(-max_radius, max_radius + 1):
            cx, cy = px + dx, py + dy
            if (cx, cy) in map_data['walkable_cells']:
                if cx == ex or cy == ey or abs(cx - ex) == abs(cy - ey):
                    dist_sq = (cx - px) ** 2 + (cy - py) ** 2
                    aligned_tiles.append((cx, cy, dist_sq))
    if not aligned_tiles:
        return None

    best_tile = min(aligned_tiles, key=lambda tile: tile[2])
    return (best_tile[0], best_tile[1])


def get_gid_at(map_manager, x, y):
    for layer in reversed(map_manager.maps[map_manager.current_map]["layers"]):
        data = layer["data"]
        ox, oy = layer["offset_x"], layer["offset_y"]

        lx = x - ox
        ly = y - oy

        if 0 <= ly < len(data) and 0 <= lx < len(data[0]):
            gid = data[ly][lx]
            if gid != 0:
                return gid
    return 0