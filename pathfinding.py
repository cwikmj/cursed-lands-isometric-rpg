import heapq
from settings import *


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(pos, walkable_cells, bounds):
    x, y = pos
    min_x, min_y, max_x, max_y = bounds
    neighbors = []

    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if min_x <= nx < max_x and min_y <= ny < max_y:
            if (nx, ny) in walkable_cells:
                neighbors.append((nx, ny))

    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        nx, ny = x + dx, y + dy
        if min_x <= nx < max_x and min_y <= ny < max_y:
            # Check if both adjacent tiles are walkable
            ax1, ay1 = x + dx, y  # adjacent in x direction
            ax2, ay2 = x, y + dy  # adjacent in y direction
            if ((ax1, ay1) in walkable_cells and (ax2, ay2) in walkable_cells and (nx, ny) in walkable_cells):
                neighbors.append((nx, ny))

    return neighbors

def a_star(start, goal, map_manager, occupied_tiles=None):
    if occupied_tiles is None:
        occupied_tiles = set()

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    node_cost = {start: 0}
    open_set_hash = {start}
    map_data = map_manager.maps[map_manager.current_map]
    walkable_cells = map_data['walkable_cells']
    bounds = map_data['bounds']

    while open_set:
        _, current = heapq.heappop(open_set)
        open_set_hash.remove(current)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            for x, y in path:
                if not (x, y) in walkable_cells:
                    return []
            return path

        for neighbor in get_neighbors(current, walkable_cells, bounds):
            cost_multiplier = 10 if neighbor in occupied_tiles else 1
            temp_cost = node_cost[current] + cost_multiplier
            if neighbor not in node_cost or temp_cost < node_cost[neighbor]:
                came_from[neighbor] = current
                node_cost[neighbor] = temp_cost
                lowest_cost = temp_cost + heuristic(neighbor, goal)
                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (lowest_cost, neighbor))
                    open_set_hash.add(neighbor)

    return []
