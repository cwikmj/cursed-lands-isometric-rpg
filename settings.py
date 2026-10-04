import os
import pygame
from resource_path import resource_path

TILE_WIDTH = 128
TILE_HEIGHT = 64
MAP_WIDTH = 100
MAP_HEIGHT = 100
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
DISTANCE_TO_RENDER = 12.0
CAMERA_FOLLOW_SPEED = 12.0

ACLONICA = resource_path('assets/fonts/aclonica.ttf')
MEDIEVAL = resource_path('assets/fonts/medieval.ttf')
ORBITRON = resource_path('assets/fonts/orbitron.ttf')
FIREBREATH = resource_path('assets/fonts/firebreath.ttf')

pygame.font.init()
FONTS = {
    "BASE": pygame.font.Font(MEDIEVAL, 85),
    "UI": pygame.font.Font(MEDIEVAL, 20),
    "LOG": pygame.font.Font(ORBITRON, 14),
    "TITLE": pygame.font.Font(MEDIEVAL, 18),
    "LARGE": pygame.font.Font(MEDIEVAL, 35),
    "TOOLTIP": pygame.font.Font(MEDIEVAL, 22),
    "POI": pygame.font.Font(MEDIEVAL, 24),
    "GEAR": pygame.font.Font(MEDIEVAL, 16),
    "PAUSE": pygame.font.Font(ACLONICA, 32),
    "DEBUG": pygame.font.Font(ACLONICA, 10),
}

BACKGROUND = (0, 0, 0)
TEXT = (100, 100, 100)
LIGHT = (150, 150, 150)
EXP = (252, 191, 106)

PLAYER_SPEED = 6
ATTACK_RANGE = 1.5
REGENERATION_RATE = 10000
FOOTSTEP_INTERVAL_MS = 260

UI_HEIGHT = 100
UI_BACKGROUND = (20, 20, 20, 160)
INVENTORY_SLOT_LIMIT = 16
SKILL_INV_WIDTH = SCREEN_WIDTH // 2 - 25
SKILL_INV_HEIGHT = int(SCREEN_HEIGHT * 0.8)
SKILL_INV_X = 20
INVENTORY_X = SCREEN_WIDTH - SKILL_INV_WIDTH - SKILL_INV_X
SKILL_INV_Y = (SCREEN_HEIGHT - SKILL_INV_HEIGHT) // 2 - 40
SKILL_INV_BG = UI_BACKGROUND
SKILL_INV_BORDER = TEXT
SKILL_ICON_SIZE = (64, 64)
SKILL_TREE_NODE_RADIUS = 35
SKILL_TREE_GAP = 115

SKILL_BAR_WIDTH = 155
SKILL_BAR_HEIGHT = UI_HEIGHT - 20
SKILL_BAR_X = SCREEN_WIDTH - SKILL_BAR_WIDTH - 20
SKILL_BAR_Y = SCREEN_HEIGHT - UI_HEIGHT + 10
SKILL_BAR_ICON_SIZE = (32, 32)
SKILL_BAR_ICON_PADDING = 5

LOG_WIDTH = 350
LOG_HEIGHT = SKILL_BAR_HEIGHT
LOG_X = SCREEN_WIDTH - LOG_WIDTH - SKILL_BAR_WIDTH - 30
LOG_Y = SCREEN_HEIGHT - UI_HEIGHT + 10
LOG_MAX_LINES = 4
LOG_MAX_DURATION = 10.0

POI_SURF = FONTS['POI'].render("!", True, (255, 215, 0))
POI_SHADOW = FONTS['POI'].render("!", True, (20, 20, 20))

EXP_LEVELS = [0, 700, 1800, 3500, 5600, 7900, 9500, 12000, 15400, 19100, 22500, 25400, 28900, 32600, 35300, 39200, 45000, 52000, 60000, 70000, 82000, 95000]
SKILLS = ['attack', 'kick', 'clash', 'whirlwind', 'firebolt', 'lightning', 'teleport', 'forcepush']
SKILL_LEVEL_REQ = {
    'kick': 3,
    'clash': 5,
    'whirlwind': 7,
    'firebolt': 4,
    'lightning': 6,
    'teleport': 7,
    'forcepush': 9
}
SKILLS_PREREQ = {
    'kick': [],
    'clash': ['kick'],
    'whirlwind': ['kick','clash'],
    'firebolt': [],
    'lightning': ['firebolt'],
    'teleport': ['firebolt','lightning'],
    'forcepush': ['firebolt','lightning','teleport']
}
DELAYED_DAMAGE_SKILLS = ['clash', 'forcepush']

SWORD_SKILLS = [
    {"name": "Kick", "desc": f"Deal +25% extra damage and knock your enemy back\n\nLevel {SKILL_LEVEL_REQ['kick']} required"},
    {"name": "Clash", "desc": f"Make a powerful blow ignoring enemy's defence\n\nLevel {SKILL_LEVEL_REQ['clash']} required\n'Kick' skill required"},
    {"name": "Whirlwind", "desc": f"Rageful spin attack hurting all nearby enemies\n\nLevel {SKILL_LEVEL_REQ['whirlwind']} required\n'Kick' and 'Clash' skills required"}
]
MAGIC_SKILLS = [
    {"name": "Firebolt", "desc": f"Launch a firebolt, dealing 12 fire damage\n\nLevel {SKILL_LEVEL_REQ['firebolt']} required"},
    {"name": "Lightning", "desc": f"Strike an enemy with lightning for 25 damage\n\nLevel {SKILL_LEVEL_REQ['lightning']} required\n\n'Firebolt' skill required"},
    {"name": "Teleport", "desc": f"Instantly travel from one location to another\n\nLevel {SKILL_LEVEL_REQ['teleport']} required\n\n'Firebolt' and 'Lightning' skills required"},
    {"name": "Forcepush", "desc": f"A wave of concussive, invisible force sending enemies out\n\nLevel {SKILL_LEVEL_REQ['forcepush']} required\nAll previous Will skills required"}
]
SPELLS = {
    'whirlwind': {"duration": 0.3, "speed": 0.03, "damage": 0, "mana_cost": 15, "rect_x": 256, "rect_y": 512, "rows": 5, "cols": 2, "offset_x": 40, "offset_y": 40},
    'fireball': {"duration": 0.4, "speed": 0.02, "damage": 0, "mana_cost": 5, "rect_x": 184, "rect_y": 85, "rows": 4, "cols": 5, "offset_x": 15, "offset_y": 15},
    'firebolt': {"duration": 0.4, "speed": 0.02, "damage": 25, "mana_cost": 5, "rect_x": 184, "rect_y": 85, "rows": 4, "cols": 5, "offset_x": 15, "offset_y": 15},
    'icebolt': {"duration": 0.4, "speed": 0.02, "damage": 25, "mana_cost": 0, "rect_x": 184, "rect_y": 85, "rows": 4, "cols": 5, "offset_x": 15, "offset_y": 15},
    'lightning': {"duration": 0.72, "speed": 0.03, "damage": .5, "mana_cost": 5, "rect_x": 98, "rect_y": 203, "rows": 4, "cols": 6, "offset_x": 150, "offset_y": 25},
    'teleport': {"duration": 0.9, "speed": 0.02, "damage": 0, "mana_cost": 10, "rect_x": 80, "rect_y": 67, "rows": 6, "cols": 6, "offset_x": 30, "offset_y": 10},
    'shock': {"duration": 0.6, "speed": 0.03, "damage": 0, "mana_cost": 5, "rect_x": 125, "rect_y": 100, "rows": 4, "cols": 5, "offset_x": 60, "offset_y": 30},
    'forcepush': {"duration": 0.4, "speed": 0.02, "damage": 0, "mana_cost": 20, "rect_x": 168, "rect_y": 148, "rows": 4, "cols": 5, "offset_x": 60, "offset_y": 50},
    'quake': {"duration": 0.3, "speed": 0.05, "damage": 0, "mana_cost": 0, "rect_x": 256, "rect_y": 128, "rows": 1, "cols": 6, "offset_x": 0, "offset_y": 50},
    'aura': {"duration": 0.8, "speed": 0.025, "damage": 0, "mana_cost": 0, "rect_x": 128, "rect_y": 128, "rows": 4, "cols": 8, "offset_x": 100, "offset_y": 20},
    'kick': {"duration": 0.8, "speed": 0.025, "damage": 0, "mana_cost": 5, "rect_x": 128, "rect_y": 128, "rows": 4, "cols": 8, "offset_x": 100, "offset_y": 20},
    'clash': {"duration": 0.8, "speed": 0.025, "damage": 0, "mana_cost": 5, "rect_x": 128, "rect_y": 128, "rows": 4, "cols": 8, "offset_x": 100, "offset_y": 20}
}
BURSTS = {
    'icebolt': {"duration": 0.48, "speed": 0.0075, "damage": 0, "mana_cost": 0, "rect_x": 128, "rect_y": 128, "rows": 8, "cols": 8, "offset_x": 70, "offset_y": 50},
    'firebolt': {"duration": 0.48, "speed": 0.0075, "damage": 0, "mana_cost": 0, "rect_x": 128, "rect_y": 128, "rows": 8, "cols": 8, "offset_x": 70, "offset_y": 50}
}

CHEST_INTERACTION_RANGE = 2
FIXED_IMAGES = ['loot.png', 'money.png', 'potion.png', 'health.png', 'mana.png', 'inv-bg.png']
ITEMS = {
    "helmet": [
        { "name": "Leather Cap of the Forest", "path": "helmet_0.png", "desc": "+2 to defence", "type": "helmet", "value": 100 },
        { "name": "Sturdy Helm of Night", "path": "helmet_1.png", "desc": "+4 to defence", "type": "helmet", "value": 240 },
        { "name": "Iron Helmet of Swiftness", "path": "helmet_2.png", "desc": "+7 to defence", "type": "helmet", "value": 350 },
        { "name": "Mystic Helmet of Shadows", "path": "helmet_3.png", "desc": "+10 to defence", "type": "helmet", "value": 500 },
        { "name": "Golden Helmet of Kings", "path": "helmet_4.png", "desc": "+12 to defence, +6 to willpower", "type": "helmet", "value": 600 },
        { "name": "Ethereal Helm of Valor", "path": "helmet_5.png", "desc": "+15 to defence, +10 to willpower", "type": "helmet", "value": 800 }
    ],
    "armor": [
        { "name": "Sturdy Leather Armor", "path": "armor_0.png", "desc": "+3 to defence", "type": "armor", "value": 140 },
        { "name": "Chainmail of the Wolf", "path": "armor_1.png", "desc": "+5 to defence", "type": "armor", "value": 200 },
        { "name": "Leather Armor of the Scout", "path": "armor_2.png", "desc": "+4 to defence, +3 to attack", "type": "armor", "value": 360 },
        { "name": "Heavy Plate of Valor", "path": "armor_3.png", "desc": "+8 to defence", "type": "armor", "value": 500 },
        { "name": "Robes of the Wise", "path": "armor_4.png", "desc": "+7 to defence, +3 to willpower", "type": "armor", "value": 700 },
        { "name": "Fortress Plate of Resilience", "path": "armor_5.png", "desc": "+8 to defence, +4 to attack", "type": "armor", "value": 1000 },
        { "name": "Shadow Armor of Night", "path": "armor_6.png", "desc": "+10 to defence, +5 to willpower", "type": "armor", "value": 1200 },
        { "name": "Mystic Chainmail of the Ancients", "path": "armor_7.png", "desc": "+15 to defence, +8 to attack", "type": "armor", "value": 1500 },
        { "name": "Blessed Armor of Light", "path": "armor_8.png", "desc": "+20 to defence, +10 to willpower", "type": "armor", "value": 1800 },
        { "name": "Celestial Cuirass of Harmony", "path": "armor_9.png", "desc": "+24 to defence, +10 to attack, +5 to willpower", "type": "armor", "value": 2000 }
    ],
    "weapon": [
        { "name": "Short Dagger", "path": "weapon_0.png", "desc": "+2 to attack", "type": "weapon", "value": 120 },
        { "name": "Sword of the Forest", "path": "weapon_1.png", "desc": "+3 to attack", "type": "weapon", "value": 220 },
        { "name": "Crystal Sword", "path": "weapon_2.png", "desc": "+5 to attack", "type": "weapon", "value": 360 },
        { "name": "Edge Sword of Clarity", "path": "weapon_3.png", "desc": "+8 to attack, +3 to defence", "type": "weapon", "value": 400 },
        { "name": "Heavy Sword of the Knight", "path": "weapon_4.png", "desc": "+12 to attack", "type": "weapon", "value": 600 },
        { "name": "Blade of the Elves", "path": "weapon_5.png", "desc": "+15 to attack, +3 to willpower", "type": "weapon", "value": 1000 },
        { "name": "Long Sword of Chaos", "path": "weapon_6.png", "desc": "+18 to attack, +4 to defence", "type": "weapon", "value": 1200 },
        { "name": "Rapier of Pain", "path": "weapon_7.png", "desc": "+22 to attack, +5 to defence", "type": "weapon", "value": 1500 },
        { "name": "Doomblade of the Fallen Hero", "path": "weapon_8.png", "desc": "+28 to attack, +8 to defence, +5 to willpower", "type": "weapon", "value": 1800 }
    ],
    "shields": [
        { "name": "Buckler of Defence", "path": "shield_0.png", "desc": "+4 to defence", "type": "shields", "value": 120 },
        { "name": "Tower Shield of Stone", "path": "shield_1.png", "desc": "+6 to defence", "type": "shields", "value": 240 },
        { "name": "Stormguard", "path": "shield_2.png", "desc": "+8 to defence", "type": "shields", "value": 360 },
        { "name": "Veil Shield of Illusions", "path": "shield_3.png", "desc": "+12 to defence, +2 to willpower", "type": "shields", "value": 500 },
        { "name": "Phoenix Wing Shield", "path": "shield_4.png", "desc": "+15 to defence, +4 to willpower", "type": "shields", "value": 700 },
        { "name": "Mystic Shield of Ages", "path": "shield_5.png", "desc": "+20 to defence, +5 to willpower", "type": "shields", "value": 900 }
    ],
    "boots": [
        { "name": "Boots of the Fleet", "path": "boots_0.png", "desc": "+2 to defence", "type": "boots", "value": 80 },
        { "name": "Iron Boots of Endurance", "path": "boots_1.png", "desc": "+3 to defence", "type": "boots", "value": 140 },
        { "name": "Ghostwalker Boots of Stealth", "path": "boots_2.png", "desc": "+4 to defence, +1 to speed", "type": "boots", "value": 300 },
        { "name": "Greaves of the Warrior", "path": "boots_3.png", "desc": "+8 to defence, +2 to speed", "type": "boots", "value": 500 },
        { "name": "Battle-Scarred Greaves of Power", "path": "boots_4.png", "desc": "+10 to defence, +3 to speed", "type": "boots", "value": 800 }
    ]
}

NPC_DIALOGUES = {
    "trader_1": "Ah, a valiant noble warrior! This world was once peaceful and prosperous... before the evil force came to it. Now, darkness taints the soil and shadows whisper in the ruins. We seek a champion to cleanse this land. Will you be the one to restore the light?",
    "trader_2": "Welcome to our seaside refuge, Paladin. Ebonwood Wilds is the last bastion of safety before the wild dark takes over. Stock up on your steel and provisions here while you can. Your path ahead leads through the brooding dark forest, deep into forgotten caves and crumbling ruins and more... Hone your melee strikes and master your emerging spells, for only by finding the true source of this evil at your journey's end can you hope to save us all. Ah, and one more thing - don't forget to look around the village for some useful items hidden in the chests. Safe travels, hero!",
    "trader_3": "Ha... you found me. Most wanderers pass this little wood without a glance. Luck, or fate, still has a soft spot for you. I set out with others to strike the evil at its heart. We thought ourselves ready. We were not. It was older and stronger than any of us, and I watched good fighters fall while I fled. Shame kept me here, among the roots, while the curse kept spreading. Listen well: do not linger. Pass through the Forgotten Cavern, then press on through the Old Ruins. Beyond those stones the land grows quiet in the wrong way... that is where the source of this evil waits. Go farther than I dared. Restore the light I failed to keep.",
}

ENEMY_STATS = {
    "Goblin": {
        "STYLE": "melee", "SPEED": 4.5, "MAX_HEALTH": 45, "DAMAGE": 10, "EXP": 150,
        "ROWS": 8, "COLS": 48, "ACTION_FRAMES": {'idle': (0, 4), 'run': (12, 20), 'attack': (20, 24), 'hurt': (30, 32), 'die': (40, 48)}
    },
    "Goblin Shaman": {
        "STYLE": "firebolt", "SPEED": 4.0, "MAX_HEALTH": 85, "DAMAGE": 8, "EXP": 350,
        "ROWS": 8, "COLS": 48, "ACTION_FRAMES": {'idle': (0, 4), 'run': (12, 20), 'attack': (20, 24), 'hurt': (30, 32), 'die': (40, 48)}
    },
    "Skeleton": {
        "STYLE": "melee", "SPEED": 2.8, "MAX_HEALTH": 60, "DAMAGE": 10, "EXP": 150,
        "ROWS": 8, "COLS": 32, "ACTION_FRAMES": {'idle': (0, 4), 'run': (4, 12), 'attack': (12, 16), 'hurt': (16, 22), 'die': (22, 28)}
    },
    "Skeleton Knight": {
        "STYLE": "melee", "SPEED": 3.0, "MAX_HEALTH": 110, "DAMAGE": 12, "EXP": 280,
        "ROWS": 8, "COLS": 28, "ACTION_FRAMES": {'idle': (0, 4), 'run': (4, 12), 'attack': (12, 16), 'hurt': (16, 22), 'die': (20, 28)}
    },
    "Skeleton Occultist": {
        "STYLE": "icebolt", "SPEED": 3.0, "MAX_HEALTH": 120, "DAMAGE": 8, "EXP": 440,
        "ROWS": 8, "COLS": 28, "ACTION_FRAMES": {'idle': (0, 4), 'run': (4, 12), 'attack': (16, 20), 'hurt': (15, 18), 'die': (20, 28)}
    },
    "Zombie": {
        "STYLE": "melee", "SPEED": 2.2, "MAX_HEALTH": 130, "DAMAGE": 12, "EXP": 280,
        "ROWS": 8, "COLS": 36, "ACTION_FRAMES": {'idle': (0, 4), 'run': (4, 12), 'attack': (12, 16), 'hurt': (16, 20), 'die': (28, 36)}
    },
    "Dark Zombie": {
        "STYLE": "melee", "SPEED": 2.6, "MAX_HEALTH": 180, "DAMAGE": 15, "EXP": 520,
        "ROWS": 8, "COLS": 36, "ACTION_FRAMES": {'idle': (0, 4), 'run': (4, 12), 'attack': (12, 16), 'hurt': (16, 20), 'die': (28, 36)}
    },
    "Spider": {
        "STYLE": "melee", "SPEED": 5.0, "MAX_HEALTH": 70, "DAMAGE": 12, "EXP": 250,
        "ROWS": 8, "COLS": 32, "ACTION_FRAMES": {'idle': (0, 4), 'run': (4, 12), 'attack': (14, 18), 'hurt': (16, 18), 'die': (18, 24)}
    },
    "Antilion": {
        "STYLE": "melee", "SPEED": 5.0, "MAX_HEALTH": 150, "DAMAGE": 18, "EXP": 480,
        "ROWS": 8, "COLS": 32, "ACTION_FRAMES": {'idle': (0, 4), 'run': (4, 12), 'attack': (12, 18), 'hurt': (18, 20), 'die': (18, 24)}
    },
    "Cursed Knight": {
        "STYLE": "melee", "SPEED": 4.2, "MAX_HEALTH": 250, "DAMAGE": 20, "EXP": 950,
        "ROWS": 8, "COLS": 32, "ACTION_FRAMES": {'idle': (0, 4), 'run': (4, 12), 'attack': (12, 16), 'hurt': (16, 18), 'die': (18, 24)}
    },
    "Werewolf": {
        "STYLE": "melee", "SPEED": 5.2, "MAX_HEALTH": 200, "DAMAGE": 25, "EXP": 650,
        "ROWS": 8, "COLS": 28, "ACTION_FRAMES": {'idle': (0, 8), 'run': (8, 16), 'attack': (16, 20), 'hurt': (20, 22), 'die': (20, 28)}
    },
    "Werebear": {
        "STYLE": "melee", "SPEED": 3.4, "MAX_HEALTH": 300, "DAMAGE": 30, "EXP": 850,
        "ROWS": 8, "COLS": 28, "ACTION_FRAMES": {'idle': (0, 4), 'run': (4, 12), 'attack': (12, 18), 'hurt': (18, 20), 'die': (18, 24)}
    },
    "Minotaur": {
        "STYLE": "melee", "SPEED": 4.0, "MAX_HEALTH": 350, "DAMAGE": 30, "EXP": 1200,
        "ROWS": 8, "COLS": 24, "ACTION_FRAMES": {'idle': (0, 4), 'run': (4, 12), 'attack': (12, 16), 'hurt': (16, 18), 'die': (18, 24)}
    },
    "Golem": {
        "STYLE": "melee", "SPEED": 2.4, "MAX_HEALTH": 500, "DAMAGE": 35, "EXP": 1400,
        "ROWS": 8, "COLS": 28, "ACTION_FRAMES": {'idle': (0, 4), 'run': (4, 12), 'attack': (12, 16), 'hurt': (16, 22), 'die': (22, 28)}
    },
    "Wyvern": {
        "STYLE": "melee", "SPEED": 5.0, "MAX_HEALTH": 600, "DAMAGE": 48, "EXP": 1750,
        "ROWS": 8, "COLS": 56, "ACTION_FRAMES": {'idle': (0, 8), 'run': (8, 16), 'attack': (40, 48), 'die': (48, 56)}
    },
    "Ice Wyvern": {
        "STYLE": "melee", "SPEED": 5.0, "MAX_HEALTH": 800, "DAMAGE": 52, "EXP": 2000,
        "ROWS": 8, "COLS": 56, "ACTION_FRAMES": {'idle': (0, 8), 'run': (8, 16), 'attack': (24, 32), 'die': (48, 56)}
    },
    "Demon": {
        "STYLE": "firebolt", "SPEED": 4.2, "MAX_HEALTH": 2000, "DAMAGE": 70, "EXP": 5000,
        "ROWS": 8, "COLS": 42, "ACTION_FRAMES": {'idle': (0, 4), 'run': (4, 13), 'attack': (13, 18), 'attack2': (18, 23), 'cast': (23, 29), 'die': (31, 42)}
    }
}