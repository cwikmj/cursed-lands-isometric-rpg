import pygame
import sys
import math
import random

from settings import *
from gamelog import *


def draw_button(screen, rect, label, hovered):
    border = EXP if hovered else TEXT
    pygame.draw.rect(screen, border, rect, 2, border_radius=12)
    screen.blit(label, label.get_rect(center=rect.center))

def main_menu(screen, clock, sound_manager, menu_bg):
    """
    Shows the entry menu and blocks until the player starts or quits.
    Returns "start" | "quit"
    """
    cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    game_name_shadow = FONTS["BASE"].render("cursed lands", True, (72, 77, 81))
    game_name = FONTS["BASE"].render("cursed lands", True, (129, 141, 151))
    start_label = FONTS["PAUSE"].render("start game", True, LIGHT)
    quit_label = FONTS["PAUSE"].render("quit", True, LIGHT)
    button_width = max(start_label.get_width(), quit_label.get_width()) + 80
    button_height = 68
    start_rect = pygame.Rect(0, 0, button_width, button_height)
    start_rect.center = (cx, cy + 10)
    quit_rect = pygame.Rect(0, 0, button_width, button_height)
    quit_rect.center = (cx, cy + 100)
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill(BACKGROUND)
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))

    while True:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.blit(menu_bg, (0, 0))
        screen.blit(overlay, (0, 0))
        title_x = cx - game_name.get_width() // 2
        title_y = cy - 220
        screen.blit(game_name_shadow, (title_x + 3, title_y + 3))
        screen.blit(game_name, (title_x, title_y))

        pygame.draw.line(screen, TEXT, (cx - 200, cy - 110), (cx + 200, cy - 110), 2)
        pygame.draw.line(screen, TEXT, (cx - 220, cy - 105), (cx + 220, cy - 105), 2)
        pygame.draw.line(screen, TEXT, (cx - 200, cy - 100), (cx + 200, cy - 100), 2)
        draw_button(screen, start_rect, start_label, start_rect.collidepoint(mouse_x, mouse_y))
        draw_button(screen, quit_rect, quit_label, quit_rect.collidepoint(mouse_x, mouse_y))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    screen.blit(background, (0, 0))
                    sound_manager.play_sound("button")
                    loading_notice(screen)
                    return "start"
                if event.key == pygame.K_ESCAPE:
                    return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_rect.collidepoint(event.pos):
                    screen.blit(background, (0, 0))
                    sound_manager.play_sound("button")
                    loading_notice(screen)
                    return "start"
                if quit_rect.collidepoint(event.pos):
                    return "quit"

def pause_menu(screen, last_screen_surface, sound_manager):
    """
    Draws paused menu with a darkened image of the current game state, 
    while pausing game loop. Includes hoverable and clickable UI buttons.
    """
    gamename_shadow = FONTS["BASE"].render("cursed lands", True, (72, 77, 81))
    gamename = FONTS["BASE"].render("cursed lands", True, (129, 141, 151))
    resume_surf = FONTS["PAUSE"].render("resume (ESC)", True, LIGHT)
    controls_surf = FONTS["PAUSE"].render("controls (C)", True, LIGHT)
    quit_surf = FONTS["PAUSE"].render("quit (Q)", True, LIGHT)
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    
    cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    btn_w = max(resume_surf.get_width(), quit_surf.get_width(), controls_surf.get_width()) + 60
    btn_h = 70
    
    resume_rect = pygame.Rect(0, 0, btn_w, btn_h)
    resume_rect.center = (cx, cy + 10)
    controls_rect = pygame.Rect(0, 0, btn_w, btn_h)
    controls_rect.center = (cx, cy + 100)
    quit_rect = pygame.Rect(0, 0, btn_w, btn_h)
    quit_rect.center = (cx, cy + 190)
    
    showing_controls = False

    while True:
        mx, my = pygame.mouse.get_pos()
        screen.blit(last_screen_surface, (0, 0))
        screen.blit(overlay, (0, 0))
        gamename_pos = (cx - gamename.get_width() // 2, cy - 220)
        shadow_offset = 3
        screen.blit(gamename_shadow, (gamename_pos[0] + shadow_offset, gamename_pos[1] + shadow_offset))
        screen.blit(gamename, gamename_pos)
        
        pygame.draw.line(screen, TEXT, (cx - 200, cy - 110), (cx + 200, cy - 110), 2)
        pygame.draw.line(screen, TEXT, (cx - 220, cy - 105), (cx + 220, cy - 105), 2)
        pygame.draw.line(screen, TEXT, (cx - 200, cy - 100), (cx + 200, cy - 100), 2)
        
        if showing_controls:
            show_controls_overlay(screen, cx, cy)
        else:
            draw_button(screen, resume_rect, resume_surf, resume_rect.collidepoint(mx, my))
            draw_button(screen, controls_rect, controls_surf, controls_rect.collidepoint(mx, my))
            draw_button(screen, quit_rect, quit_surf, quit_rect.collidepoint(mx, my))
            
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.KEYDOWN:
                if showing_controls:
                    sound_manager.play_sound('unpause')
                    showing_controls = False
                else:
                    if event.key == pygame.K_ESCAPE:
                        sound_manager.play_sound('unpause')
                        return
                    elif event.key == pygame.K_c:
                        sound_manager.play_sound('button')
                        showing_controls = True
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                        
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if showing_controls:
                    showing_controls = False
                else:
                    if resume_rect.collidepoint(mx, my):
                        sound_manager.play_sound('unpause')
                        return
                    elif controls_rect.collidepoint(mx, my):
                        sound_manager.play_sound('button')
                        showing_controls = True
                    elif quit_rect.collidepoint(mx, my):
                        pygame.quit()
                        sys.exit()

def show_controls_overlay(screen, cx, cy):
    """Draws the controls panel inside the pause menu."""
    panel_w, panel_h = 500, 400
    panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
    panel_rect.center = (cx, cy + 80)
    pygame.draw.rect(screen, (30, 30, 30, 240), panel_rect, border_radius=15)
    pygame.draw.rect(screen, LIGHT, panel_rect, 2, border_radius=15)
    
    # Title
    title = FONTS["LARGE"].render("IN-GAME CONTROLS", True, EXP)
    screen.blit(title, title.get_rect(center=(cx, panel_rect.top + 50)))
    pygame.draw.line(screen, TEXT, (cx - 150, panel_rect.top + 80), (cx + 150, panel_rect.top + 80), 2)
    
    # Controls map
    controls = [
        ("Left Click", "Move / Attack / Interact"),
        ("Right Click", "Cast Active Spell"),
        ("T", "Open/Close Skill Tree"),
        ("I", "Open/Close Inventory"),
        ("H", "Drink Health Potion"),
        ("M", "Drink Mana Potion"),
        ("1 - 7", "Select Active Spell"),
        ("ESC", "Pause Game / Close Menus")
    ]
    
    start_y = panel_rect.top + 120
    for i, (key, action) in enumerate(controls):
        y_pos = start_y + (i * 32)
        key_surf = FONTS["UI"].render(key, True, EXP)
        key_rect = key_surf.get_rect(midright=(cx - 70, y_pos))
        screen.blit(key_surf, key_rect)
        action_surf = FONTS["UI"].render(action, True, LIGHT)
        action_rect = action_surf.get_rect(midleft=(cx - 25, y_pos))
        screen.blit(action_surf, action_rect)

def loading_notice(screen):
    """
    Draws a full-screen themed loading state matching the 'Cursed Lands' UI.
    Includes an optimized RPG magic spinner with smooth arcs and embers.
    """
    bg_capture = screen.copy()
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    sy = cy + 220
    loading_surf = FONTS["BASE"].render("loading...", True, LIGHT)
    loading_shadow = FONTS["BASE"].render("loading...", True, (40, 40, 40))
    sub_surf = FONTS["LARGE"].render("CURSED LANDS", True, EXP)
    embers = [[random.uniform(cx-220, cx+220), random.uniform(cy-50, cy+450), random.uniform(0.15, 0.55), random.uniform(0, math.tau)] for _ in range(50)]
    start_ticks = pygame.time.get_ticks()
    clock = pygame.time.Clock()
    fx_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    while pygame.time.get_ticks() - start_ticks < 800:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        screen.blit(bg_capture, (0, 0))
        screen.blit(overlay, (0, 0))
        fx_surf.fill((0, 0, 0, 0))
        t = (pygame.time.get_ticks() - start_ticks) / 1000.0

        for dy, hw in [(-10, 180), (-5, 200), (0, 180)]:
            pygame.draw.line(screen, TEXT, (cx - hw, cy - 20 + dy), (cx + hw, cy - 20 + dy), 2)
        screen.blit(loading_shadow, (cx - loading_surf.get_width()//2 + 3, cy - 117))
        screen.blit(loading_surf, (cx - loading_surf.get_width()//2, cy - 120))
        screen.blit(sub_surf, (cx - sub_surf.get_width()//2, cy + 30))

        hr = int(28 + (0.6 + 0.4 * math.sin(t * 2.5)) * 6)
        for k in range(5): 
            pygame.draw.circle(fx_surf, (*LIGHT, int(15 - k*3)), (cx, sy), hr + k*3, 2)

        arc_r, rot = 64, t * 2.5
        for i in range(3): 
            start_rad = rot + i * (math.tau / 3)
            for a, width in [(30, 8), (80, 4), (255, 2)]:
                pygame.draw.arc(fx_surf, (*EXP, a), (cx-arc_r, sy-arc_r, arc_r*2, arc_r*2), -start_rad - 1.4, -start_rad, width)

        for i in range(3):
            p = t * 2.0 + i * (math.tau / 3)
            ox, oy = cx + math.cos(p) * 38, sy + math.sin(p) * 38
            r = max(2, int(9 * (1.0 + 0.18 * math.sin(t * 5.2 + i)) * (0.75 + 0.25 * math.sin(t * 13.0 + i*2.0))))
            
            pygame.draw.circle(fx_surf, (*EXP, 40), (int(ox), int(oy)), r + 6)
            pygame.draw.circle(fx_surf, EXP, (int(ox), int(oy)), r)
            pygame.draw.circle(fx_surf, LIGHT, (int(ox), int(oy)), max(1, r - 3), 1)
            pygame.draw.line(fx_surf, UI_BACKGROUND, (ox + math.cos(p)*(r+2), oy + math.sin(p)*(r+2)), (ox + math.cos(p)*(r+12), oy + math.sin(p)*(r+12)), 2)
        for e in embers:
            e[1] -= e[2]; e[0] += math.sin(t * 1.8 + e[3]) * 0.18; e[3] += 0.02
            if e[1] < cy - 140: 
                e[:] = [random.uniform(cx-180, cx+180), random.uniform(cy+90, cy+170), random.uniform(0.15, 0.55), random.uniform(0, math.tau)]
            pygame.draw.circle(fx_surf, (*EXP, int(40 + 40 * math.sin(t * 4.0 + e[3]))), (int(e[0]), int(e[1])), 2)

        screen.blit(fx_surf, (0, 0))
        pygame.display.flip()
        clock.tick(60)

def game_over(screen, last_frame, enemies):
    """
    Enemies go idle, a fade-in overlay appears, Game Over screen is shown with Restart and Exit buttons.
    """
    for enemy in enemies:
        enemy.path = []
        enemy.triggered = False

    font_btn     = pygame.font.Font(ACLONICA, 38)
    LARGE_shadow = FONTS["BASE"].render("you died", True, (55, 15, 15))
    LARGE_surf = FONTS["BASE"].render("you died", True, (190, 35, 35))
    sub_shadow = FONTS["LARGE"].render("you have fallen...", True, UI_BACKGROUND)
    sub_surf = FONTS["LARGE"].render("you have fallen...", True, TEXT)
    restart_surf = font_btn.render("continue", True, LIGHT)
    exit_surf    = font_btn.render("exit",                    True, LIGHT)
    cx, cy      = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    btn_w, btn_h = 210, 58
    gap          = 30
    restart_rect = pygame.Rect(cx - btn_w - gap // 2, cy + 70, btn_w, btn_h)
    exit_rect    = pygame.Rect(cx + gap // 2,          cy + 70, btn_w, btn_h)
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    max_alpha = 190
    clock = pygame.time.Clock()
    fade_start    = pygame.time.get_ticks()
    fade_duration = 1500

    while True:
        elapsed = pygame.time.get_ticks() - fade_start
        alpha   = min(int(elapsed / fade_duration * max_alpha), max_alpha)
        overlay.fill((0, 0, 0, alpha))
        screen.blit(last_frame, (0, 0))
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if elapsed >= fade_duration:
            break

    pygame.time.delay(300)
    overlay.fill((0, 0, 0, max_alpha))

    while True:
        mx, my = pygame.mouse.get_pos()
        screen.blit(last_frame, (0, 0))
        screen.blit(overlay, (0, 0))
        LARGE_y = cy - 230
        screen.blit(LARGE_shadow, (cx - LARGE_surf.get_width() // 2 + 3, LARGE_y + 3))
        screen.blit(LARGE_surf,   (cx - LARGE_surf.get_width() // 2,     LARGE_y))
        sub_y = LARGE_y + LARGE_surf.get_height() + 10
        screen.blit(sub_shadow, (cx - sub_surf.get_width() // 2 + 2, sub_y + 2))
        screen.blit(sub_surf,   (cx - sub_surf.get_width() // 2,     sub_y))
        line_y = cy - 50
        for dy, hw in [(-10, 200), (-5, 220), (0, 200)]: pygame.draw.line(screen, TEXT, (cx - hw, line_y + dy), (cx + hw, line_y + dy), 2)
        draw_button(screen, restart_rect, restart_surf, restart_rect.collidepoint(mx, my))
        draw_button(screen, exit_rect,    exit_surf,    exit_rect.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return 'restart'
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_rect.collidepoint(mx, my):
                    return 'restart'
                elif exit_rect.collidepoint(mx, my):
                    pygame.quit()
                    sys.exit()
