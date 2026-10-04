LEVELS_DATA = {
    'ebonwood': {
        "title": 'Ebonwood Wilds',
        "start_pos": (2, 85),
        "teleport_pos": (-7, 64),
        "exits": {
            (-36, 28): { "destination": "cave", "spawn_pos": (-37, -57) },
        },
        "walkable_tiles": set(range(1, 4306)) - {228} - set(range(259, 262)) - set(range(275, 280)) - set(range(291, 296)) - set(range(307, 310)) - set(range(353, 368)) - set(range(385, 400)) - set(range(417, 432)) - set(range(587, 3257)),
        "water_tiles": set(),
        "surface": 'grass',
        "enemies": [
            'Goblin', 'Goblin', 'Goblin', 'Goblin', 'Goblin', 'Goblin',
            'Skeleton', 'Skeleton', 'Skeleton', 'Skeleton',
            'Skeleton Knight', 'Skeleton Knight'
        ],
        "enemies_range": [-33, 15, 22, 56],
        "chests": [(-12, 26), (-34, 54), (-2, 69), (-1, 80), (-8, 69), (-9, 68), (-15, 72), (15, 28), (14, 56), (15, 26)]
    },
    'cave': {
        "title": 'Cold Cave',
        "start_pos": (-37, -57),
        "teleport_pos": (-35, 1),
        "exits": {
            (-37, -57): { "destination": "ebonwood", "spawn_pos": (-36, 28) },
            (9, 4): { "destination": "moor", "spawn_pos": (-92, 46) },
        },
        "walkable_tiles": set(range(1, 41)),
        "water_tiles": set(range(416, 480)),
        "surface": 'concrete',
        "enemies": [
            'Spider', 'Spider', 'Spider', 'Spider', 'Spider',
            'Zombie', 'Zombie', 'Zombie', 'Zombie', 'Zombie',
            'Skeleton Knight', 'Skeleton Knight', 'Skeleton Knight'
        ],
        "enemies_range": [-35, 8, -56, 5],
        "chests": []
    },
    'moor': {
        "title": 'Dark Moor',
        "start_pos": (-92, 46),
        "teleport_pos": (-92, 27),
        "exits": {
            (-92, 46): { "destination": "cave", "spawn_pos": (9, 4) },
            (-15, 36): { "destination": "cavern", "spawn_pos": (20, -33) },
        },
        "walkable_tiles": set(range(4307, 4414)),
        "water_tiles": set(),
        "surface": 'grass',
        "enemies": [
            'Goblin', 'Goblin', 'Goblin', 'Goblin',
            'Goblin Shaman', 'Goblin Shaman', 'Goblin Shaman',
            'Skeleton Occultist', 'Skeleton Occultist',
            'Werewolf', 'Werewolf', 'Werewolf',
            'Dark Zombie', 'Dark Zombie'
        ],
        "enemies_range": [-77, 9, -50, 48],
        "chests": [(-93, 49), (-90, 24), (-45, 61), (-15, 32), (-15, 29), (-56, -8), (-79, -7)]
    },
    'cavern': {
        "title": 'Forgotten Cavern',
        "start_pos": (20, -33),
        "teleport_pos": (-13, 7),
        "exits": {
            (20, -33): { "destination": "moor", "spawn_pos": (-15, 36) },
            (24, -5): { "destination": "ruins", "spawn_pos": (-44, -26) },
        },
        "walkable_tiles": set(range(1, 41)),
        "water_tiles": set(range(416, 480)),
        "surface": 'concrete',
        "enemies": [
            'Antilion', 'Antilion', 'Antilion', 'Antilion', 'Antilion',
            'Dark Zombie', 'Dark Zombie', 'Dark Zombie', 'Dark Zombie',
            'Werebear', 'Werebear',
            'Skeleton Occultist', 'Skeleton Occultist'
        ],
        "enemies_range": [-30, 12, -40, 6],
        "chests": []
    },
    'ruins': {
        "title": 'Old Ruins',
        "start_pos": (-44, -26),
        "teleport_pos": (-62, 2),
        "exits": {
            (-44, -26): { "destination": "cavern", "spawn_pos": (24, -5) },
            (-42, -62): { "destination": "icebound", "spawn_pos": (-15, 4) },
        },
        "walkable_tiles": set(range(1100, 1390)),
        "water_tiles": set(),
        "surface": 'concrete',
        "enemies": [
            'Cursed Knight', 'Cursed Knight', 'Cursed Knight', 'Cursed Knight',
            'Minotaur', 'Minotaur', 'Minotaur',
            'Golem', 'Golem',
            'Wyvern', 'Wyvern'
        ],
        "enemies_range": [-77, -34, -52, 16],
        "chests": [(-37, -30), (-36, -25), (-65, -15), (-64, -19), (-71, -52)]
    },
    'icebound': {
        "title": 'Icebound Path',
        "start_pos": (-15, 4),
        "teleport_pos": (32, -12),
        "exits": {
            (-15, 4): { "destination": "ruins", "spawn_pos": (-42, -62) },
            (-16, -39): { "destination": "cursed", "spawn_pos": (-7, -2) },
        },
        "walkable_tiles": set(range(640, 940)),
        "water_tiles": set(),
        "surface": 'snow',
        "enemies": [
            'Ice Wyvern', 'Ice Wyvern',
            'Golem', 'Golem',
            'Werebear', 'Werebear', 'Werebear',
            'Skeleton Occultist', 'Skeleton Occultist', 'Skeleton Occultist',
            'Minotaur', 'Minotaur'
        ],
        "enemies_range": [-6, 30, -45, 35],
        "chests": []
    },
    'cursed': {
        "title": 'Cursed Den',
        "start_pos": (-7, -2),
        "teleport_pos": (20, 10),
        "exits": {
            (-7, -2): { "destination": "icebound", "spawn_pos": (-16, -39)  }
        },
        "walkable_tiles": set(range(1, 41)),
        "water_tiles": set(range(416, 480)),
        "surface": 'concrete',
        "enemies": ['Demon'],
        "enemies_range": [2, 29, -26, -44],
        "chests": []
    }
}