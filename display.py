import pygame

from settings import *
from gamelog import *
from map_data import *
from item import Item
from resource_path import resource_path


SWORD_TITLE = FONTS["TITLE"].render("Way of the Sword", True, LIGHT)
MAGIC_TITLE = FONTS["TITLE"].render("Way of the Will", True, LIGHT)
SKILL_TREE_TITLE = FONTS["LARGE"].render("SKILLS TREE", True, LIGHT)
INV_TITLE = FONTS["LARGE"].render("INVENTORY", True, LIGHT)

UI_BG = pygame.Surface((SCREEN_WIDTH, UI_HEIGHT), pygame.SRCALPHA)
UI_BG.fill(UI_BACKGROUND)

skill_INV_bg = pygame.Surface((SKILL_INV_WIDTH, SKILL_INV_HEIGHT), pygame.SRCALPHA)
pygame.draw.rect(skill_INV_bg, SKILL_INV_BG, (0, 0, SKILL_INV_WIDTH, SKILL_INV_HEIGHT), border_radius=15)
pygame.draw.rect(skill_INV_bg, SKILL_INV_BORDER, (0, 0, SKILL_INV_WIDTH, SKILL_INV_HEIGHT), 2, border_radius=15)

inventory_bg = pygame.Surface((SKILL_INV_WIDTH, SKILL_INV_HEIGHT), pygame.SRCALPHA)
pygame.draw.rect(inventory_bg, SKILL_INV_BG, (0, 0, SKILL_INV_WIDTH, SKILL_INV_HEIGHT), border_radius=15)
pygame.draw.rect(inventory_bg, SKILL_INV_BORDER, (0, 0, SKILL_INV_WIDTH, SKILL_INV_HEIGHT), 2, border_radius=15)

dragged_item = None
dragged_from_inventory = False
dragged_index = -1
_trade_clicked = False
_SCALED_IMAGE_CACHE = {}
_LEVEL_NAME_CACHE = {}
_INV_BOTTOM_IMGS = None

# HELPERS
def load_skill_icons():
    icons = {}
    SKILLS.append('skill')
    SKILLS.append('skill-active')
    for skill in SKILLS:
        icon = pygame.image.load(resource_path(os.path.join("assets/skills/", f'{skill}.png'))).convert_alpha()
        icon = pygame.transform.scale(icon, SKILL_ICON_SIZE)
        icons[skill] = icon
    return icons

def prepare_inventory_images(loaded_images):
    global _INV_BOTTOM_IMGS
    _INV_BOTTOM_IMGS = {
        "health": scaled_image(loaded_images["health.png"], (45, 45)),
        "mana": scaled_image(loaded_images["mana.png"], (45, 45)),
        "cash": scaled_image(loaded_images["money.png"], (45, 45)),
    }

def scaled_image(source, size, alpha=None):
    key = (source, tuple(size), alpha)
    image = _SCALED_IMAGE_CACHE.get(key)
    if image is None:
        image = pygame.transform.scale(source, size)
        if alpha is not None:
            image.set_alpha(alpha)
        _SCALED_IMAGE_CACHE[key] = image
    return image

def draw_tooltip(screen, text_lines, mouse_pos, text_color=EXP, bg_color=SKILL_INV_BG, border_color=SKILL_INV_BORDER, padding_x=15, padding_y=10, border_radius=15):
    """
    Draws a tooltip with a rounded border and background.
    Text is centered horizontally within the tooltip.
    """
    line_surfaces = [FONTS["TITLE"].render(line, True, text_color) for line in text_lines]
    max_width = max(surf.get_width() for surf in line_surfaces)
    total_height = sum(surf.get_height() for surf in line_surfaces)
    rect_width = max_width + padding_x * 2
    rect_height = total_height + padding_y * 2
    mx, my = mouse_pos
    rect_x, rect_y = mx + 20, my

    if my < SCREEN_HEIGHT - 50:
        rect_y = my - rect_height - 10
    if mx > SCREEN_WIDTH * .7:
        rect_x = mx - rect_width - 10

    bg_rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
    pygame.draw.rect(screen, border_color, bg_rect, border_radius=border_radius)
    inner_rect = bg_rect.inflate(-4, -4)
    pygame.draw.rect(screen, bg_color, inner_rect, border_radius=border_radius)

    current_y = rect_y + padding_y
    for surf in line_surfaces:
        line_rect = surf.get_rect(centerx=bg_rect.centerx)
        line_rect.top = current_y
        screen.blit(surf, line_rect)
        current_y += surf.get_height()

def prepare_level_name(current_map):
    if current_map in _LEVEL_NAME_CACHE:
        return

    name = LEVELS_DATA[current_map]["title"]
    text = FONTS["TITLE"].render(name, True, LIGHT)
    shadow = FONTS["TITLE"].render(name, True, (0, 0, 0))

    padding = 10
    shadow_offset = 3
    width = max(text.get_width() + padding, 5 + shadow_offset + shadow.get_width())
    height = max(text.get_height() + padding, 5 + shadow_offset + shadow.get_height())
    panel = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(panel, UI_BACKGROUND, (0, 0, text.get_width() + padding, text.get_height() + padding), border_radius=5)
    panel.blit(shadow, (5 + shadow_offset, 5 + shadow_offset))
    panel.blit(text, (5, 5))
    _LEVEL_NAME_CACHE[current_map] = panel

# PUBLIC FUNCTIONS
def draw_level_name(screen, current_map):
    screen.blit(_LEVEL_NAME_CACHE[current_map], (15, 15))

def draw_ui(screen, player, skill_icons, game_log):
    """
    Draws UI at the bottom including health, mana bars, level, experience, skill choice and game log.
    """
    # --- Constants and Layout ---
    UI_TOP = SCREEN_HEIGHT - UI_HEIGHT
    bar_width, bar_height = 200, 20
    exp_bar_width, exp_bar_height = 150, 10
    bar_x = 20
    health_y = SCREEN_HEIGHT - UI_HEIGHT + 30
    mana_y = SCREEN_HEIGHT - UI_HEIGHT + 55
    exp_x = bar_x + bar_width + 250
    exp_y = mana_y + (bar_height - exp_bar_height) // 2 + 10

    # --- UI Background ---
    screen.blit(UI_BG, (0, UI_TOP))
    pygame.draw.line(screen, TEXT, (0, UI_TOP), (SCREEN_WIDTH, UI_TOP), 2)

    # --- Health and Mana Bars ---
    health_percent = player.health / player.max_health
    mana_percent = player.mana / player.max_mana
    pygame.draw.rect(screen, (80, 50, 20), (bar_x, health_y, bar_width, bar_height), 0, 3)
    pygame.draw.rect(screen, (180, 30, 30), (bar_x, health_y, bar_width * health_percent, bar_height), 0, 3)
    pygame.draw.rect(screen, LIGHT, (bar_x, health_y, bar_width, bar_height), 2, 3)
    pygame.draw.rect(screen, (40, 30, 20), (bar_x, mana_y, bar_width, bar_height), 0, 3)
    pygame.draw.rect(screen, (30, 100, 200), (bar_x, mana_y, bar_width * mana_percent, bar_height), 0, 3)
    pygame.draw.rect(screen, LIGHT, (bar_x, mana_y, bar_width, bar_height), 2, 3)
    
    # --- Drink potion animation ---
    if hasattr(player, '_potion_animations') and player._potion_animations:
        for anim in player._potion_animations:
            if anim['active']:
                icon = FONTS["TITLE"].render("+" if anim['type'] == 'health' else "~", True, EXP)
                x_pos = bar_x + 212
                y_pos = health_y if anim['type'] == 'health' else mana_y + 42
                screen.blit(icon, (x_pos, y_pos - 20))

    # --- Experience Bar ---
    exp_percent = (player.exp - EXP_LEVELS[player.level - 1]) / (EXP_LEVELS[player.level] - EXP_LEVELS[player.level - 1])
    pygame.draw.rect(screen, BACKGROUND, (exp_x, exp_y, exp_bar_width, exp_bar_height), 0, 3)
    pygame.draw.rect(screen, EXP, (exp_x, exp_y, exp_bar_width * exp_percent, exp_bar_height), 0, 3)
    pygame.draw.rect(screen, LIGHT, (exp_x, exp_y, exp_bar_width, exp_bar_height), 2, 3)

    # --- Text Labels ---
    health_text = FONTS["UI"].render(f"HP: {int(player.health)}/{int(player.max_health)}", True, LIGHT)
    mana_text = FONTS["UI"].render(f"MP: {int(player.mana)}/{int(player.max_mana)}", True, LIGHT)
    new_skill_text = FONTS["UI"].render(f"skills available !", True, EXP)
    current_exp = FONTS["UI"].render(f"EXP: {player.exp}/{EXP_LEVELS[player.level]}", True, LIGHT)
    level_text = FONTS["UI"].render(f"Level {player.level}", True, LIGHT)

    screen.blit(health_text, (bar_x + bar_width + 10, health_y))
    screen.blit(mana_text, (bar_x + bar_width + 10, mana_y))
    screen.blit(current_exp, (exp_x - 80, exp_y - 30))
    if player.skill_points > 0:
        screen.blit(new_skill_text, (exp_x - 80, exp_y - 55))
    screen.blit(level_text, (exp_x - 80, exp_y - 5))

    # --- Draw Add Health Button ---
    skillbook_x = exp_x + exp_bar_width // 2 + 20
    skillbook_y = exp_y - 60
    icon = skill_icons['skill-active'] if player.skill_points > 0 else skill_icons['skill']
    screen.blit(icon, (skillbook_x, skillbook_y))

    # --- Skill Bar (Transparent) ---
    pygame.draw.rect(screen, TEXT, (SKILL_BAR_X, SKILL_BAR_Y, SKILL_BAR_WIDTH, SKILL_BAR_HEIGHT), 2, border_radius=10)
    icon_rects = []
    for skills_row, row_index in [(SKILLS[:4], 0), (SKILLS[4:], 1)]:
        for col_index, skill in enumerate(skills_row):
            if skill in player.skills:
                scaled_icon = pygame.transform.scale(skill_icons[skill], SKILL_BAR_ICON_SIZE)
                y_pos = SKILL_BAR_Y + SKILL_BAR_ICON_PADDING + row_index * (scaled_icon.get_height() + SKILL_BAR_ICON_PADDING)
                x_pos = SKILL_BAR_X + SKILL_BAR_ICON_PADDING + col_index * (scaled_icon.get_width() + SKILL_BAR_ICON_PADDING)
                icon_rect = scaled_icon.get_rect(topleft=(x_pos, y_pos))
                screen.blit(scaled_icon, icon_rect)
                if player.current_skill == skill and not skill == 'attack':
                    pygame.draw.rect(screen, EXP, icon_rect.inflate(5, 5), 2, border_radius=5)
                if skill == 'attack':
                    pygame.draw.rect(screen, LIGHT, icon_rect.inflate(5, 5), 2, border_radius=5)
                icon_rects.append((icon_rect, skill))

    # --- Game Log ---
    pygame.draw.rect(screen, TEXT, (LOG_X, LOG_Y, LOG_WIDTH, LOG_HEIGHT), 2, border_radius=10)
    for i, line in enumerate(game_log.get_lines()):
        text = FONTS["LOG"].render(line, True, LIGHT)
        screen.blit(text, (LOG_X + 10, LOG_Y + 2 + i * 18))

    # --- Interaction ---
    mouse_x, mouse_y = pygame.mouse.get_pos()
    skill_keys = {
        'kick': '1',
        'clash': '2',
        'whirlwind': '3',
        'firebolt': '4',
        'lightning': '5',
        'teleport': '6',
        'forcepush': '7'
    }

    for icon_rect, skill in icon_rects:
        if icon_rect.collidepoint(mouse_x, mouse_y):
            skill_name = skill.capitalize()
            if skill in skill_keys:
                skill_name += f" ({skill_keys[skill]})"
            draw_tooltip(screen, [skill_name], (mouse_x, mouse_y))
            if pygame.mouse.get_pressed()[0] and skill != 'attack':
                player.current_skill = skill

    if (skillbook_x <= mouse_x <= skillbook_x + 40 and skillbook_y <= mouse_y <= skillbook_y + 40):
        draw_tooltip(screen, ["Skills Tree (T)"], (mouse_x, mouse_y))
    if (skillbook_x <= mouse_x <= skillbook_x + 40 and skillbook_y <= mouse_y <= skillbook_y + 40):
        draw_tooltip(screen, ["Skills Tree (T)"], (mouse_x, mouse_y))

def draw_cooldown_bar(screen, player):
    """
    Draws cooldown bar above the UI with a decreasing progress bar called on every spell cast.
    """
    if not player.active_cooldown:
        return
    if player.current_skill in ('kick', 'clash'):
        return

    current_time = pygame.time.get_ticks()
    spell, duration = player.active_cooldown
    elapsed = current_time - player.spell_cast_time
    progress = min(elapsed / duration, 1.0) if duration > 0 else 1.0
    
    bar_width, bar_height = 250, 10
    bar_x = (SCREEN_WIDTH - bar_width) // 2
    bar_y = SCREEN_HEIGHT - UI_HEIGHT - 20
    spell_name = spell.replace('firebolt', 'fireball').title()
    spell_ready = "Ready" if progress >= 0.85 else "Cooldown"
    text = FONTS["TITLE"].render(f"{spell_name} {spell_ready}", True, EXP)
    text_rect = text.get_rect(center=(bar_x + bar_width // 2, bar_y - 20))
    bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    pygame.draw.rect(screen, (40, 30, 30), bg_rect, border_radius=10)
    pygame.draw.rect(screen, LIGHT, bg_rect, 1, border_radius=10)
    fill_width = bar_width * progress
    fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)

    if progress < 0.5:
        color = (100, 40, 40)   # dark red
    elif progress < 0.8:
        color = (180, 120, 50)  # bronze
    else:
        color = EXP

    pygame.draw.rect(screen, color, fill_rect, border_radius=10)
    pygame.draw.rect(screen, LIGHT, fill_rect, 1, border_radius=10)
    screen.blit(text, text_rect)

def draw_skill_tree(screen, player, skill_icons, sound_manager):
    global _skill_tree_clicked
    # --- Background / Titles ---
    screen.blit(skill_INV_bg, (SKILL_INV_X, SKILL_INV_Y))
    skill_points_text = FONTS["LARGE"].render(f"points: {player.skill_points}", True, EXP)
    screen.blit(SKILL_TREE_TITLE, (SKILL_INV_X + 20, SKILL_INV_Y + 20))
    screen.blit(skill_points_text, (SKILL_INV_X + 400, SKILL_INV_Y + 60))
    screen.blit(SWORD_TITLE, (SKILL_INV_X + 120 - SWORD_TITLE.get_width() // 2, SKILL_INV_Y + 140))
    screen.blit(MAGIC_TITLE, (SKILL_INV_X + 410 - MAGIC_TITLE.get_width() // 2, SKILL_INV_Y + 140))

    # --- Skill Data ---
    sword_x = SKILL_INV_X + 100
    sword_y_start = SKILL_INV_Y + 220
    magic_x = SKILL_INV_X + 400
    magic_y_start = SKILL_INV_Y + 220

    # --- Draw Sword Skills ---
    for i, skill in enumerate(SWORD_SKILLS):
        skill_color = EXP if skill["name"].lower() in player.skills else LIGHT
        y = sword_y_start + i * SKILL_TREE_GAP
        pygame.draw.circle(screen, skill_color, (sword_x, y), SKILL_TREE_NODE_RADIUS)
        icon = skill_icons[skill["name"].lower()]
        screen.blit(icon, (sword_x - 32, y - 32))
        skill_text = FONTS["TITLE"].render(skill["name"], True, skill_color)
        screen.blit(skill_text, (sword_x + 50, y - 10))
        if i > 0:
            prev_skill = SWORD_SKILLS[i-1]
            prev_color = EXP if prev_skill["name"].lower() in player.skills else LIGHT
            pygame.draw.line(screen, prev_color, (sword_x, y - SKILL_TREE_GAP + SKILL_TREE_NODE_RADIUS), (sword_x, y - SKILL_TREE_NODE_RADIUS), 3)

    # --- Draw Magic Skills ---
    for i, skill in enumerate(MAGIC_SKILLS):
        skill_color = EXP if skill["name"].lower() in player.skills else LIGHT
        y = magic_y_start + i * SKILL_TREE_GAP
        pygame.draw.circle(screen, skill_color, (magic_x, y), SKILL_TREE_NODE_RADIUS)
        icon = skill_icons[skill["name"].lower()]
        screen.blit(icon, (magic_x - 32, y - 32))
        skill_text = FONTS["TITLE"].render(skill["name"], True, skill_color)
        screen.blit(skill_text, (magic_x + 50, y - 10))
        if i > 0:
            prev_skill = MAGIC_SKILLS[i-1]
            prev_color = EXP if prev_skill["name"].lower() in player.skills else LIGHT
            pygame.draw.line(screen, prev_color, (magic_x, y - SKILL_TREE_GAP + SKILL_TREE_NODE_RADIUS), (magic_x, y - SKILL_TREE_NODE_RADIUS), 3)

    # --- Draw Buttons ---
    health_button_rect = pygame.Rect(SKILL_INV_X + 20, SKILL_INV_Y + 580, 90, 40)
    mana_button_rect = pygame.Rect(SKILL_INV_X + 120, SKILL_INV_Y + 580, 90, 40)
    total_skills_count = len(SWORD_SKILLS) + len(MAGIC_SKILLS)
    all_skills_unlocked = len(player.skills) >= total_skills_count + 1

    if all_skills_unlocked and player.skill_points > 0:
        mx, my = pygame.mouse.get_pos()

        # --- Draw Add Health Button ---
        is_hovering_health = health_button_rect.collidepoint(mx, my)
        border_h = 3 if is_hovering_health else 2
        health_color = EXP if is_hovering_health else LIGHT
        pygame.draw.rect(screen, health_color, health_button_rect, border_h, 5)
        health_text = FONTS["TITLE"].render("+ Health", True, health_color)
        screen.blit(health_text, (health_button_rect.x + 10, health_button_rect.y + 10))

        # --- Draw Add Mana Button ---
        is_hovering_mana = mana_button_rect.collidepoint(mx, my)
        border_m = 3 if is_hovering_mana else 2
        mana_color = EXP if is_hovering_mana else LIGHT
        pygame.draw.rect(screen, mana_color, mana_button_rect, border_m, 5)
        mana_text = FONTS["TITLE"].render("+ Mana", True, mana_color)
        screen.blit(mana_text, (mana_button_rect.x + 10, mana_button_rect.y + 10))

    # --- Tooltip and Skill Unlocking ---
    mouse_pos = pygame.mouse.get_pos()
    tooltip_lines = None

    # --- Check skill tree nodes for tooltip ---
    for i, skill in enumerate(SWORD_SKILLS + MAGIC_SKILLS):
        x = sword_x if i < len(SWORD_SKILLS) else magic_x
        y = (sword_y_start + i * SKILL_TREE_GAP) if i < len(SWORD_SKILLS) else (magic_y_start + (i - len(SWORD_SKILLS)) * SKILL_TREE_GAP)
        if ((x - mouse_pos[0]) ** 2 + (y - mouse_pos[1]) ** 2) ** 0.5 <= SKILL_TREE_NODE_RADIUS:
            tooltip_lines = skill["desc"].split('\n')

    # --- Check buttons for tooltip ---
    if all_skills_unlocked and player.skill_points > 0:
        if health_button_rect.collidepoint(mouse_pos):
            tooltip_lines = ["Add 10 Health Points"]
        elif mana_button_rect.collidepoint(mouse_pos):
            tooltip_lines = ["Add 10 Mana Points"]

    # --- Draw tooltip if needed ---
    if tooltip_lines:
        draw_tooltip(screen, tooltip_lines, mouse_pos)

    # --- Event handling (inside your event loop) ---
    if '_skill_tree_clicked' not in globals():
        _skill_tree_clicked = False

    mouse_pressed = pygame.mouse.get_pressed()
    
    if mouse_pressed[0] and not _skill_tree_clicked:
        _skill_tree_clicked = True
        
        if all_skills_unlocked and player.skill_points > 0:
            if health_button_rect.collidepoint(mouse_pos):
                sound_manager.play_sound('button')
                player.skill_points -= 1
                player.health += 10
                player.max_health += 10
            elif mana_button_rect.collidepoint(mouse_pos):
                sound_manager.play_sound('button')
                player.skill_points -= 1
                player.mana += 10
                player.max_mana += 10
        else:
            # --- Skill tree node click logic ---
            for i, skill in enumerate(SWORD_SKILLS + MAGIC_SKILLS):
                x = sword_x if i < len(SWORD_SKILLS) else magic_x
                y = (sword_y_start + i * SKILL_TREE_GAP) if i < len(SWORD_SKILLS) else (magic_y_start + (i - len(SWORD_SKILLS)) * SKILL_TREE_GAP)
                if ((x - mouse_pos[0]) ** 2 + (y - mouse_pos[1]) ** 2) ** 0.5 <= SKILL_TREE_NODE_RADIUS:
                    if (player.skill_points > 0 and player.level >= SKILL_LEVEL_REQ[skill['name'].lower()] and
                        set(SKILLS_PREREQ[skill['name'].lower()]).issubset(player.skills)):
                        sound_manager.play_sound('button')
                        player.skills.append(skill['name'].lower())
                        player.skill_points -= 1

    elif not mouse_pressed[0]:
        _skill_tree_clicked = False

def draw_inventory(screen, player, loaded_images, items, sound_manager):
    global dragged_item, dragged_from_inventory, dragged_index
    INV_BOTTOM_IMGS = _INV_BOTTOM_IMGS
    gear_slot_size, gear_padding = 60, 22
    slot_size, slot_padding = 58, 10
    slots_x, slots_y = 8, 2
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()

    # --- Background / Titles ---
    screen.blit(inventory_bg, (INVENTORY_X, SKILL_INV_Y))
    screen.blit(INV_TITLE, (INVENTORY_X + 20, SKILL_INV_Y + 20))

    # --- Player Stats ---
    stats_bg = pygame.Surface((200, 140), pygame.SRCALPHA)
    pygame.draw.rect(stats_bg, UI_BACKGROUND, (0, 0, 200, 140), border_radius=5)
    pygame.draw.rect(stats_bg, TEXT, (0, 0, 200, 140), 2, border_radius=5)
    screen.blit(stats_bg, (INVENTORY_X + 20, SKILL_INV_Y + 150))

    attack_text = FONTS["TOOLTIP"].render(f"Attack: {player.stats["attack"]}", True, TEXT)
    screen.blit(attack_text, (INVENTORY_X + 40, SKILL_INV_Y + 160))
    defence_text = FONTS["TOOLTIP"].render(f"Defence: {player.stats["defence"]}", True, TEXT)
    screen.blit(defence_text, (INVENTORY_X + 40, SKILL_INV_Y + 190))
    willpower_text = FONTS["TOOLTIP"].render(f"Willpower: {player.stats["willpower"]}", True, TEXT)
    screen.blit(willpower_text, (INVENTORY_X + 40, SKILL_INV_Y + 220))
    speed_text = FONTS["TOOLTIP"].render(f"Speed: {player.stats["speed"]}", True, TEXT)
    screen.blit(speed_text, (INVENTORY_X + 40, SKILL_INV_Y + 250))


    # --- Gear Slots (Human Body Layout) ---
    helmet_x = INVENTORY_X + 100 + (SKILL_INV_WIDTH - gear_slot_size) // 2
    helmet_y = SKILL_INV_Y + 120
    armor_x = helmet_x
    armor_y = helmet_y + gear_slot_size + gear_padding
    weapon_x = armor_x - gear_slot_size - gear_padding
    weapon_y = armor_y
    shield_x = armor_x + gear_slot_size + gear_padding
    shield_y = armor_y
    boots_x = helmet_x
    boots_y = helmet_y + 2 * gear_slot_size + 2 * gear_padding

    knight_img = loaded_images['inv-bg.png']
    bg_width = (shield_x + gear_slot_size) - weapon_x + 60
    bg_height = (boots_y + gear_slot_size) - helmet_y + 40
    knight_scaled = scaled_image(knight_img, (bg_width, bg_height), alpha=80)
    knight_scaled.set_alpha(80)
    knight_x = weapon_x - 40
    knight_y = helmet_y - 50
    screen.blit(knight_scaled, (knight_x, knight_y))

    gear_slots = [
        {"name": "Helmet", "rect": (helmet_x, helmet_y, gear_slot_size, gear_slot_size), "type": "helmet"},
        {"name": "Armor", "rect": (armor_x, armor_y, gear_slot_size, gear_slot_size), "type": "armor"},
        {"name": "Weapon", "rect": (weapon_x, weapon_y, gear_slot_size, gear_slot_size), "type": "weapon"},
        {"name": "Shield", "rect": (shield_x, shield_y, gear_slot_size, gear_slot_size), "type": "shield"},
        {"name": "Boots", "rect": (boots_x, boots_y, gear_slot_size, gear_slot_size), "type": "boots"},
    ]

    for gear in gear_slots:
        pygame.draw.rect(screen, LIGHT, gear["rect"], 2, 5)
        gear_label = FONTS["GEAR"].render(gear["name"], True, LIGHT)
        screen.blit(gear_label, (gear["rect"][0] + 5, gear["rect"][1] + 5 - gear_padding))
        gear_item = player.gear.get(gear["type"])
        if gear_item is not None and hasattr(gear_item, "image"):
            gear_img = scaled_image(gear_item.image, (gear_slot_size - 6, gear_slot_size - 6))
            rect_x, rect_y = gear["rect"][0], gear["rect"][1]
            screen.blit(gear_img, (rect_x + 3, rect_y + 3))

    # --- Inventory Slots ---
    start_x = INVENTORY_X + (SKILL_INV_WIDTH - (slots_x * slot_size + (slots_x - 1) * slot_padding)) // 2
    start_y = boots_y + gear_slot_size + 70

    for y in range(slots_y):
        for x in range(slots_x):
            slot_x = start_x + x * (slot_size + slot_padding)
            slot_y = start_y + y * (slot_size + slot_padding)
            pygame.draw.rect(screen, LIGHT, (slot_x, slot_y, slot_size, slot_size), 2, 5)

    # --- Items in Slots ---
    for i, item in enumerate(player.inventory):
        if i >= slots_x * slots_y:
            break
        if item is not None:
            x = i % slots_x
            y = i // slots_x
            slot_x = start_x + 3 + x * (slot_size + slot_padding)
            slot_y = start_y + 3 + y * (slot_size + slot_padding)
            item_image = scaled_image(item.image, (slot_size - 5, slot_size - 5))
            screen.blit(item_image, (slot_x, slot_y))


    # --- Handling Drag and Drop Logic ---
    if mouse_pressed[0]:
        # Start drag from inventory
        if dragged_item is None:
            for y in range(slots_y):
                for x in range(slots_x):
                    slot_x = start_x + x * (slot_size + slot_padding)
                    slot_y = start_y + y * (slot_size + slot_padding)
                    if slot_x <= mouse_x <= slot_x + slot_size and slot_y <= mouse_y <= slot_y + slot_size:
                        idx = y * slots_x + x
                        if idx < len(player.inventory) and player.inventory[idx] is not None and hasattr(player.inventory[idx], 'image'):
                            dragged_item = player.inventory[idx]
                            dragged_from_inventory = True
                            dragged_index = idx
                            player.inventory.pop(dragged_index)
                            break
                if dragged_item is not None:
                    break

        # Start drag from gear slot
        if dragged_item is None:
            for gear in gear_slots:
                rect = gear["rect"]
                if rect[0] <= mouse_x <= rect[0] + rect[2] and rect[1] <= mouse_y <= rect[1] + rect[3]:
                    dragged_index = gear["type"]
                    current_item = player.gear.get(dragged_index)
                    if current_item is not None:
                        dragged_item = current_item
                        dragged_from_inventory = False
                        player.gear[dragged_index] = None  # Clear gear slot while dragging
                    break

    else:
        # Mouse released, drop logic
        if dragged_item is not None:
            dropped = False
            sound_manager.play_sound('item-move')

            # Attempt to equip to gear slot
            for gear in gear_slots:
                rect = gear["rect"]
                if rect[0] <= mouse_x <= rect[0] + rect[2] and rect[1] <= mouse_y <= rect[1] + rect[3]:
                    if dragged_item.type.split('_')[0] == gear["type"]:
                        if player.gear[gear["type"]] is None:
                            # Equip item, remove from inventory fully if dragged from inventory
                            player.gear[gear["type"]] = dragged_item
                            dropped = True
                        else:
                            # Swap gear and keep dragging swapped item
                            temp = player.gear[gear["type"]]
                            player.gear[gear["type"]] = dragged_item
                            dragged_item = temp
                            dragged_from_inventory = False
                        break

            if not dropped:
                # Attempt to drop in inventory slot
                placed_in_slot = False
                for y in range(slots_y):
                    for x in range(slots_x):
                        slot_x = start_x + x * (slot_size + slot_padding)
                        slot_y = start_y + y * (slot_size + slot_padding)
                        if slot_x <= mouse_x <= slot_x + slot_size and slot_y <= mouse_y <= slot_y + slot_size:
                            idx = y * slots_x + x
                            if idx >= len(player.inventory):
                                placed_in_slot = True
                            else:
                                # Swap items
                                player.inventory[idx], dragged_item = dragged_item, player.inventory[idx]
                                dragged_from_inventory = True
                                dragged_index = idx
                            break
                    if placed_in_slot or (dragged_from_inventory and dragged_item is not None):
                        break

                if not placed_in_slot and not dropped:
                    # If dragged from gear and dropped outside slots, append to inventory
                    if not dragged_from_inventory:
                        if len(player.inventory) < INVENTORY_SLOT_LIMIT:
                            player.inventory.append(dragged_item)
                            dropped = True
                        else:
                            # drop item on the map
                            item = Item(player.x, player.y, dragged_item.type, dragged_item.name, dragged_item.value, dragged_item.desc)
                            items.add(item)

            # If dropped anywhere, return item to inventory
            if not dropped and dragged_item is not None and len(player.inventory) < INVENTORY_SLOT_LIMIT:
                player.inventory.append(dragged_item)

            # Reset drag state
            dragged_item = None
            dragged_from_inventory = False
            dragged_index = -1
            player.update_stats()

    # --- Draw Dragged Item ---
    if dragged_item is not None and hasattr(dragged_item, 'image'):
        dragged_item_image = scaled_image(dragged_item.image, (slot_size - 5, slot_size - 5))
        screen.blit(dragged_item_image, (mouse_x - slot_size // 2, mouse_y - slot_size // 2))

    # --- Tooltip for Gear Items ---
    for gear in gear_slots:
        rect_x, rect_y, rect_w, rect_h = gear["rect"]
        if (rect_x <= mouse_x <= rect_x + rect_w and rect_y <= mouse_y <= rect_y + rect_h):
            gear_item = player.gear.get(gear["type"])
            if gear_item is not None:
                lines = [gear_item.name, "", gear_item.desc]
                draw_tooltip(screen, lines, (mouse_x, mouse_y))
            else:
                tooltip_text = FONTS["TOOLTIP"].render('empty', True, EXP)
                screen.blit(tooltip_text, (mouse_x + 25, mouse_y + 25))
            break
    
    # --- Tooltip for Items ---
    for y in range(slots_y):
        for x in range(slots_x):
            slot_x = start_x + x * (slot_size + slot_padding)
            slot_y = start_y + y * (slot_size + slot_padding)
            if (slot_x <= mouse_x <= slot_x + slot_size and slot_y <= mouse_y <= slot_y + slot_size):
                idx = y * slots_x + x
                if idx < len(player.inventory) and player.inventory[idx] is not None:
                    item = player.inventory[idx]
                    lines = [item.name, "", item.desc]
                    draw_tooltip(screen, lines, (mouse_x, mouse_y))
                else:
                    tooltip_text = FONTS["TOOLTIP"].render('empty', True, EXP)
                    screen.blit(tooltip_text, (mouse_x + 25, mouse_y + 25))
                break

    # --- Potions and Cash ---
    screen.blit(INV_BOTTOM_IMGS["health"], (INVENTORY_X + 30, boots_y + 290))
    player_health_potions = FONTS["TOOLTIP"].render(f"{player.potions["health"]}", True, LIGHT)
    screen.blit(player_health_potions, (INVENTORY_X + 90, boots_y + 300))

    screen.blit(INV_BOTTOM_IMGS["mana"], (INVENTORY_X + 150, boots_y + 290))
    player_mana_potions = FONTS["TOOLTIP"].render(f"{player.potions["mana"]}", True, LIGHT)
    screen.blit(player_mana_potions, (INVENTORY_X + 210, boots_y + 300))

    cash_slot_x = boots_x + 5
    cash_slot_y = boots_y + 280
    pygame.draw.rect(screen, LIGHT, (cash_slot_x, cash_slot_y, 200, 64), 2, 5)
    screen.blit(INV_BOTTOM_IMGS["cash"], (boots_x + 15, boots_y + 285))
    player_cash = FONTS["TOOLTIP"].render(f"{player.cash}", True, LIGHT)
    screen.blit(player_cash, (boots_x + 125, boots_y + 300))

def draw_teleports_menu(screen, current_tp, teleports, mx, my):
    target_map = None
    mouse_pressed = pygame.mouse.get_pressed()
    screen.blit(skill_INV_bg, (SKILL_INV_X, SKILL_INV_Y))
    title = FONTS["LARGE"].render("WAYPOINTS", True, LIGHT)
    screen.blit(title, (SKILL_INV_X + 20, SKILL_INV_Y + 20))
    
    slot_size, slot_padding = 58, 20
    start_x = SKILL_INV_X + 40
    start_y = SKILL_INV_Y + 100
    
    for i, tp in enumerate(teleports):
        slot_x = start_x
        slot_y = start_y + i * (slot_size + slot_padding)
        is_current = (current_tp is not None and tp.tp_id == current_tp.tp_id)
        is_unlocked = tp.active
        
        color = TEXT
        if is_current:
            color = EXP
        elif is_unlocked:
            color = LIGHT
        btn_rect = pygame.Rect(slot_x, slot_y, 300, slot_size)
        
        if is_unlocked and not is_current:
            if btn_rect.collidepoint((mx, my)):
                pygame.draw.rect(screen, TEXT, btn_rect, border_radius=5)

                if mouse_pressed[0]:
                    target_map = tp.dest_map
        pygame.draw.rect(screen, TEXT, (slot_x, slot_y, slot_size, slot_size), 2, 5)
        
        source = tp.frames[1] if is_unlocked else tp.frames[0]
        tp_icon = scaled_image(source, (slot_size - 6, slot_size - 2), alpha=150)
        screen.blit(tp_icon, (slot_x + 3, slot_y + 3))
        
        text = FONTS["TITLE"].render(tp.name.upper(), True, color)
        text_y = slot_y + (slot_size - text.get_height()) // 2
        screen.blit(text, (slot_x + slot_size + 15, text_y + 2))
        
    return target_map

def draw_npc_modal(screen, npc, current_time):
    """
    Draws the NPC dialogue modal with a typewriter effect.
    Returns the close/continue button rect for click detection.
    """
    MODAL_WIDTH = 800
    PADDING = 30
    MODAL_X = (SCREEN_WIDTH - MODAL_WIDTH) // 2

    char_speed = 30
    if npc.dialogue_fully_revealed:
        visible_text = npc.dialogue
        is_finished_typing = True
    else:
        time_since_opened = current_time - npc.dialogue_start_time
        chars_to_show = min(len(npc.dialogue), time_since_opened // char_speed)
        visible_text = npc.dialogue[:chars_to_show]
        is_finished_typing = chars_to_show >= len(npc.dialogue)

    words = visible_text.split(' ')
    lines = []
    current_line = []
    max_text_width = MODAL_WIDTH - (PADDING * 2)

    for word in words:
        test_line = ' '.join(current_line + [word])
        if FONTS["TITLE"].size(test_line)[0] <= max_text_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))

    line_height = FONTS["TITLE"].get_linesize() + 5
    text_total_height = len(lines) * line_height
    MODAL_HEIGHT = max(200, 70 + text_total_height + 70) 
    MODAL_Y = SCREEN_HEIGHT - UI_HEIGHT - MODAL_HEIGHT - 20

    modal_bg = pygame.Surface((MODAL_WIDTH, MODAL_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(modal_bg, SKILL_INV_BG, (0, 0, MODAL_WIDTH, MODAL_HEIGHT), border_radius=15)
    pygame.draw.rect(modal_bg, SKILL_INV_BORDER, (0, 0, MODAL_WIDTH, MODAL_HEIGHT), 2, border_radius=15)
    screen.blit(modal_bg, (MODAL_X, MODAL_Y))
    title = FONTS["LARGE"].render(npc.name.upper(), True, EXP)
    screen.blit(title, (MODAL_X + PADDING, MODAL_Y + 20))
    pygame.draw.line(screen, TEXT, (MODAL_X + PADDING, MODAL_Y + 55), (MODAL_X + MODAL_WIDTH - PADDING, MODAL_Y + 55), 2)
    text_y = MODAL_Y + 70
    for line in lines:
        text_surf = FONTS["TITLE"].render(line, True, LIGHT)
        screen.blit(text_surf, (MODAL_X + PADDING, text_y))
        text_y += line_height

    trade_btn_rect = pygame.Rect(MODAL_X + MODAL_WIDTH - 280, MODAL_Y + MODAL_HEIGHT - 50, 120, 35)
    close_btn_rect = pygame.Rect(MODAL_X + MODAL_WIDTH - 150, MODAL_Y + MODAL_HEIGHT - 50, 120, 35)
    
    if is_finished_typing:
        mx, my = pygame.mouse.get_pos()
        
        t_hovered = trade_btn_rect.collidepoint((mx, my))
        pygame.draw.rect(screen, EXP if t_hovered else TEXT, trade_btn_rect, 2, border_radius=8)
        t_text = FONTS["UI"].render("TRADE", True, LIGHT)
        screen.blit(t_text, t_text.get_rect(center=trade_btn_rect.center))
        
        c_hovered = close_btn_rect.collidepoint((mx, my))
        pygame.draw.rect(screen, EXP if c_hovered else TEXT, close_btn_rect, 2, border_radius=8)
        c_text = FONTS["UI"].render("FAREWELL", True, LIGHT)
        screen.blit(c_text, c_text.get_rect(center=close_btn_rect.center))
        
        return trade_btn_rect, close_btn_rect
    
    return None, None

def draw_trade_menu(screen, player, npc, loaded_images, sound_manager):
    global _trade_clicked
    
    MODAL_WIDTH, MODAL_HEIGHT = 800, 500
    MODAL_X = (SCREEN_WIDTH - MODAL_WIDTH) // 2
    MODAL_Y = (SCREEN_HEIGHT - MODAL_HEIGHT) // 2
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()
    
    # --- Background ---
    modal_bg = pygame.Surface((MODAL_WIDTH, MODAL_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(modal_bg, UI_BACKGROUND, (0, 0, MODAL_WIDTH, MODAL_HEIGHT), border_radius=15)
    pygame.draw.rect(modal_bg, SKILL_INV_BORDER, (0, 0, MODAL_WIDTH, MODAL_HEIGHT), 2, border_radius=15)
    screen.blit(modal_bg, (MODAL_X, MODAL_Y))
    
    # --- Titles ---
    shop_title = FONTS["LARGE"].render(f"{npc.name.upper()}'S WARES", True, EXP)
    inv_title = FONTS["LARGE"].render("YOUR ITEMS", True, LIGHT)
    
    screen.blit(shop_title, (MODAL_X + 30, MODAL_Y + 20))
    screen.blit(inv_title, (MODAL_X + 430, MODAL_Y + 20))
    pygame.draw.line(screen, TEXT, (MODAL_X + 400, MODAL_Y + 20), (MODAL_X + 400, MODAL_Y + MODAL_HEIGHT - 20), 2)

    # --- Player Cash Styling (Matching Inventory) ---
    INV_BOTTOM_ICONS = (45, 45)
    cash_icon = pygame.transform.scale(loaded_images["money.png"], INV_BOTTOM_ICONS)
    
    cash_slot_x = MODAL_X + 430
    cash_slot_y = MODAL_Y + 415
    pygame.draw.rect(screen, LIGHT, (cash_slot_x, cash_slot_y, 200, 64), 2, 5)
    screen.blit(cash_icon, (cash_slot_x + 10, cash_slot_y + 5))
    player_cash_text = FONTS["TOOLTIP"].render(f"{player.cash}", True, LIGHT)
    screen.blit(player_cash_text, (cash_slot_x + 120, cash_slot_y + 20))

    slot_size, slot_padding = 58, 10
    slots_x, slots_y = 5, 5
    
    tooltip_data = None
    action_taken = False

    if mouse_pressed[0] and not _trade_clicked:
        _trade_clicked = True
        is_click = True
    elif not mouse_pressed[0]:
        _trade_clicked = False
        is_click = False
    else:
        is_click = False

    # --- Draw NPC Inventory ---
    npc_start_x = MODAL_X + 30
    npc_start_y = MODAL_Y + 70
    
    for y in range(slots_y + 1):
        for x in range(slots_x):
            slot_x = npc_start_x + x * (slot_size + slot_padding)
            slot_y = npc_start_y + y * (slot_size + slot_padding)
            pygame.draw.rect(screen, LIGHT, (slot_x, slot_y, slot_size, slot_size), 2, 5)
            
            idx = y * slots_x + x
            if idx < len(npc.inventory):
                item = npc.inventory[idx]
                if hasattr(item, 'image'):
                    item_image = pygame.transform.scale(item.image, (slot_size - 5, slot_size - 5))
                    screen.blit(item_image, (slot_x + 2, slot_y + 2))
                
                if slot_x <= mouse_x <= slot_x + slot_size and slot_y <= mouse_y <= slot_y + slot_size:
                    tooltip_data = [item.name, item.desc, "", f"Price: {item.value} coins", "[Click to Buy]"]
                    
                    if is_click and not action_taken:
                        if player.cash >= item.value and len(player.inventory) < 25: 
                            player.cash -= item.value
                            if item.type in ['health', 'mana']:
                                sound_manager.play_sound('potion')
                                player.potions[item.name] += 1
                            else:
                                player.inventory.append(item)
                                sound_manager.play_sound('item-pick')
                            npc.inventory.pop(idx)
                            action_taken = True
                            
    # --- Draw Player Inventory ---
    plr_start_x = MODAL_X + 430
    plr_start_y = MODAL_Y + 70
    
    for y in range(slots_y):
        for x in range(slots_x):
            slot_x = plr_start_x + x * (slot_size + slot_padding)
            slot_y = plr_start_y + y * (slot_size + slot_padding)
            pygame.draw.rect(screen, TEXT, (slot_x, slot_y, slot_size, slot_size), 2, 5)
            
            idx = y * slots_x + x
            if idx < len(player.inventory) and player.inventory[idx] is not None:
                item = player.inventory[idx]
                if hasattr(item, 'image'):
                    item_image = pygame.transform.scale(item.image, (slot_size - 5, slot_size - 5))
                    screen.blit(item_image, (slot_x + 2, slot_y + 2))
                
                if slot_x <= mouse_x <= slot_x + slot_size and slot_y <= mouse_y <= slot_y + slot_size:
                    sell_price = max(1, int(round(item.value * .7)))
                    tooltip_data = [item.name, item.desc, "", f"Price: {item.value // 2} coins", "[Click to Sell]"]
                    
                    if is_click and not action_taken:
                        player.cash += sell_price
                        sound_manager.play_sound('item-drop')
                        npc.inventory.append(item)
                        player.inventory.pop(idx)
                        action_taken = True

    # --- Draw Tooltip ---
    if tooltip_data:
        draw_tooltip(screen, tooltip_data, (mouse_x, mouse_y))
        
    # --- Draw Close Button ---
    close_btn = pygame.Rect(MODAL_X + MODAL_WIDTH - 140, MODAL_Y + MODAL_HEIGHT - 60, 100, 35)
    btn_hovered = close_btn.collidepoint((mouse_x, mouse_y))
    pygame.draw.rect(screen, EXP if btn_hovered else TEXT, close_btn, 2, border_radius=8)
    btn_text = FONTS["UI"].render("LEAVE", True, LIGHT)
    screen.blit(btn_text, btn_text.get_rect(center=close_btn.center))
    
    if is_click and btn_hovered:
        return True 
        
    return False

def draw_boss_intro_modal(screen, boss, current_time):
    MODAL_WIDTH, PADDING = 800, 30
    MODAL_X = (SCREEN_WIDTH - MODAL_WIDTH) // 2
    char_speed = 30
    dialogue = (
        "So you have come this far. How admirable. "
        "You call it courage. I call it ignorance wearing a brave face. "
        "Hope is only the first thing suffering devours. "
        "Struggle if you wish. Every victory you claimed has led you here. "
        "And here, at last, you will learn what awaits all things."
    )

    if boss.dialogue_fully_revealed:
        visible_text = dialogue
        is_finished_typing = True
    else:
        elapsed = current_time - boss.dialogue_start_time
        chars_to_show = min(len(dialogue), elapsed // char_speed)
        visible_text = dialogue[:chars_to_show]
        is_finished_typing = chars_to_show >= len(dialogue)

    max_text_width = MODAL_WIDTH - (PADDING * 2)
    words = visible_text.split(" ")
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        if FONTS["TITLE"].size(test_line)[0] <= max_text_width:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))

    line_height = FONTS["TITLE"].get_linesize() + 5
    text_total_height = len(lines) * line_height
    MODAL_HEIGHT = max(200, 70 + text_total_height + 70)
    MODAL_Y = SCREEN_HEIGHT - UI_HEIGHT - MODAL_HEIGHT - 20
    boss_background = (40, 26, 30, 235)
    boss_border = (125, 55, 58, 255)
    boss_title_color = (205, 85, 75)
    boss_divider_color = (135, 80, 75)
    boss_button_color = (175, 70, 65)

    modal_bg = pygame.Surface((MODAL_WIDTH, MODAL_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(modal_bg, boss_background, (0, 0, MODAL_WIDTH, MODAL_HEIGHT), border_radius=15)
    pygame.draw.rect(modal_bg, boss_border, (0, 0, MODAL_WIDTH, MODAL_HEIGHT), 2, border_radius=15)
    screen.blit(modal_bg, (MODAL_X, MODAL_Y))
    title = FONTS["TITLE"].render("VORTHAX", True, boss_title_color)
    screen.blit(title, (MODAL_X + PADDING, MODAL_Y + 20))
    pygame.draw.line(screen, boss_divider_color, (MODAL_X + PADDING, MODAL_Y + 55), (MODAL_X + MODAL_WIDTH - PADDING, MODAL_Y + 55), 2)
    text_y = MODAL_Y + 70

    for line in lines:
        text_surface = FONTS["TITLE"].render(line, True, LIGHT)
        screen.blit(text_surface, (MODAL_X + PADDING, text_y))
        text_y += line_height

    if is_finished_typing:
        continue_button = pygame.Rect(MODAL_X + MODAL_WIDTH - 150, MODAL_Y + MODAL_HEIGHT - 50, 120, 35)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        is_hovered = continue_button.collidepoint((mouse_x, mouse_y))
        pygame.draw.rect(screen, boss_button_color if is_hovered else TEXT, continue_button, 2, border_radius=8)
        button_text = FONTS["UI"].render("CONTINUE", True, LIGHT)
        screen.blit(button_text, button_text.get_rect(center=continue_button.center))

def draw_boss_outro_screen(screen, current_time, outro_start_time):
    MODAL_WIDTH, PADDING = 800, 30
    MODAL_X = (SCREEN_WIDTH - MODAL_WIDTH) // 2
    outro_text = (
        "The demon's final cry fades into the silence of the outer realm, "
        "and the oppressive shadows that once choked the ruins begin to lift. "
        "Thanks to your unwavering blade and newly mastered spells, the corrupted "
        "soil of Ebonwood Wilds can finally heal from its long nightmare. "
        "The seaside refuge and every surviving villager are forever safe "
        "because you chose to answer the call of the Light. "
        "Though the journey is over, tales of the valiant Paladin who cleansed "
        "the Cursed Lands will echo for generations to come."
    )

    char_speed = 30
    elapsed = current_time - outro_start_time
    chars_to_show = min(len(outro_text), elapsed // char_speed)
    visible_text = outro_text[:chars_to_show]
    is_finished_typing = chars_to_show >= len(outro_text)
    max_text_width = MODAL_WIDTH - (PADDING * 2)
    words = visible_text.split(" ")
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        if FONTS["TITLE"].size(test_line)[0] <= max_text_width:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    line_height = FONTS["TITLE"].get_linesize() + 5
    text_total_height = len(lines) * line_height
    MODAL_HEIGHT = max(220, 70 + text_total_height + 85)

    MODAL_Y = SCREEN_HEIGHT - UI_HEIGHT - MODAL_HEIGHT - 20
    modal_bg = pygame.Surface((MODAL_WIDTH, MODAL_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(modal_bg, SKILL_INV_BG, (0, 0, MODAL_WIDTH, MODAL_HEIGHT), border_radius=15)
    pygame.draw.rect(modal_bg, LIGHT, (0, 0, MODAL_WIDTH, MODAL_HEIGHT), 2, border_radius=15)
    screen.blit(modal_bg, (MODAL_X, MODAL_Y))
    title = FONTS["LARGE"].render("VORTHAX HAS FALLEN... YOU'VE WON!", True, EXP)
    screen.blit(title, (MODAL_X + PADDING, MODAL_Y + 20))
    pygame.draw.line(screen, TEXT, (MODAL_X + PADDING, MODAL_Y + 55), (MODAL_X + MODAL_WIDTH - PADDING, MODAL_Y + 55), 2)

    text_y = MODAL_Y + 70

    for line in lines:
        text_surface = FONTS["TITLE"].render(line, True, LIGHT)
        screen.blit(text_surface, (MODAL_X + PADDING, text_y))
        text_y += line_height
    quit_button = None

    if is_finished_typing:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        quit_button = pygame.Rect(MODAL_X + MODAL_WIDTH - 150, MODAL_Y + MODAL_HEIGHT - 50, 120, 35)
        quit_hovered = quit_button.collidepoint((mouse_x, mouse_y))
        pygame.draw.rect(screen, EXP if quit_hovered else TEXT, quit_button, 2, border_radius=8)
        close_text = FONTS["UI"].render("CLOSE", True, LIGHT)
        screen.blit(close_text, close_text.get_rect(center=quit_button.center))

    return quit_button

def draw_credits_modal(screen):
    """
    Draws the final credits modal.
    Returns the CLOSE button Rect so main.py can handle its click.
    """
    modal_width, modal_height = 560, 650
    modal_x, modal_y = (SCREEN_WIDTH - modal_width) // 2, (SCREEN_HEIGHT - modal_height) // 2
    padding = 34

    modal_bg = pygame.Surface((modal_width, modal_height), pygame.SRCALPHA)
    pygame.draw.rect(modal_bg, SKILL_INV_BG, (0, 0, modal_width, modal_height), border_radius=15)
    pygame.draw.rect(modal_bg, SKILL_INV_BORDER, (0, 0, modal_width, modal_height), width=2, border_radius=15)
    screen.blit(modal_bg, (modal_x, modal_y))

    title = FONTS['LARGE'].render("THANK YOU FOR PLAYING", True, EXP)
    title_rect = title.get_rect(center=(modal_x + modal_width // 2, modal_y + 45))
    screen.blit(title, title_rect)
    pygame.draw.line(screen, TEXT, (modal_x + padding, modal_y + 78), (modal_x + modal_width - padding, modal_y + 78), 2)

    credits_text = (
        "Thank you for journeying through the Cursed Lands.\n\n"
        "For You it's been probably around 1-2hrs of fun, for me it was well over a year of work. "
        "This game, its world, and all of its code were created by one person. "
        "Every location, NPC, battle, and late-evening bug hunt came from a single "
        "desk, with no co-developers and no studio behind it.\n\n"
        "The tilesets, music, and sound effects are the exception: those assets "
        "were made by others, and this world would feel far quieter and emptier "
        "without their work (credits for them on my github).\n\n"
        "Created with courage, patience, and fun.\n\n"
        "For contact purposes, go to my Github page."
    )

    body_font = FONTS['TITLE']
    max_text_width = modal_width - padding * 2
    lines = []

    for paragraph in credits_text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        words = paragraph.split()
        current_line = ""

        for word in words:
            candidate = word if not current_line else current_line + " " + word
            if body_font.size(candidate)[0] <= max_text_width:
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

    text_y = modal_y + 105
    line_height = body_font.get_linesize() + 5
    for line in lines:
        if line:
            text_surface = body_font.render(line, True, LIGHT)
            screen.blit(text_surface, (modal_x + padding, text_y))
        text_y += line_height

    close_button = pygame.Rect(modal_x + (modal_width - 150) // 2, modal_y + modal_height - 62, 150, 38)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    hovered = close_button.collidepoint(mouse_x, mouse_y)
    pygame.draw.rect(screen, EXP if hovered else TEXT, close_button, width=2, border_radius=8)
    quit_text = FONTS['UI'].render("QUIT", True, LIGHT)
    screen.blit(quit_text, quit_text.get_rect(center=close_button.center))
    return close_button