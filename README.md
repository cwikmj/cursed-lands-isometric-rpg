<div align="center">

<img width="256" height="256" alt="image" src="https://github.com/user-attachments/assets/7259c386-0ce0-453b-ae55-a02dd05cd98d" />

# Cursed Lands

### A solo-developed, isometric dark-fantasy action RPG

*Explore the wilds. Master steel and magic. Find the source of the curse.*

Python · Pygame · Single-player · Diablo-inspired

[Getting started](#getting-started) · [Controls](#controls) · [The world](#the-world) · [Behind the game](#behind-the-game) · [Credits](#credits)

</div>

---

<img width="1192" height="795" alt="image" src="https://github.com/user-attachments/assets/f6607b5f-1d1c-42d8-aa44-7903ec643fdd" />

## Enter the Cursed Lands

Once, this land was peaceful. Now darkness taints its soil, the dead wander its forgotten paths, and the people of a small seaside refuge wait for someone willing to venture beyond the safety of their village.

You are that someone: a Paladin with a blade, an emerging command of magic, and a long road ahead.

Cursed Lands is a mouse-driven action RPG inspired by the atmosphere and rhythm of classic Diablo-style adventures. Fight through connected isometric locations, collect equipment, develop your skills, and follow the survivors' warnings toward the heart of the corruption. From the forests of Ebonwood to caves, ruined stonework, and a frozen path, each step carries you farther from safety—and closer to an answer.

This is not just a combat prototype. It brings exploration, character progression, trading, dialogue, sound, and a final confrontation together into a complete journey.

<img width="1198" height="797" alt="image" src="https://github.com/user-attachments/assets/f4dcf70f-42cc-4dd9-ac53-1febb4e6e22b" />

### Why play?

- Seven connected locations, with distinct environments and enemy lineups.
- Mouse-driven movement, melee attacks, spells, and world interactions.
- Two skill paths: the Way of the Sword and the Way of the Will.
- Equipment bonuses, loot drops, treasure chests, and merchant inventories.
- Unlockable waypoints for returning to places you have discovered.
- NPC conversations that introduce the world and point you toward its mysteries.
- Animated characters and effects, location-specific music, and footsteps matched to the terrain.
- A final boss encounter with its own dialogue, abilities, and ending sequence.

### A year at one desk

Cursed Lands is a personal project by [cwikmj](https://github.com/cwikmj), built over more than a year of work. Its programming, world layout, encounters, and dialogue came together without a studio or co-developers—one system, one location, and one late-evening bug hunt at a time.

The in-game credits describe a journey of roughly one to two hours, although your pace will depend on how much you explore and how you approach combat.

> Created with courage, patience, and fun.

## Getting started

### Requirements

- Python 3.12 or newer.
- Pygame.
- The complete project, including its `assets/` directory.
- A keyboard and a mouse with left and right buttons.

Python 3.12+ is important for the current source: some f-strings reuse quote characters inside embedded expressions, using syntax supported by newer Python versions.

<img width="1194" height="796" alt="image" src="https://github.com/user-attachments/assets/0ff17e4d-4be0-4d06-9873-4c6d786c2d69" />

### Run from source

Download or clone this repository, then open a terminal in the project folder containing `main.py` and `assets/`.

Install Pygame:

```bash
python -m pip install pygame
```

Start the game:

```bash
python main.py
```

On Windows, if you use the Python launcher:

```powershell
py -3.12 -m pip install pygame
py -3.12 main.py
```

Keep the assets in their original folders. Images, maps, fonts, music, and sound effects are loaded through relative paths, so launch the game from the project root rather than an unrelated working directory.

### Controls

| Input | Action |
| --- | --- |
| Left mouse button | Move to a walkable location; attack an enemy in melee range; interact with NPCs, loot, chests, passages, and waypoints |
| Right mouse button | Use the selected unlocked skill |
| `1` | Select Kick |
| `2` | Select Clash |
| `3` | Select Whirlwind |
| `4` | Select Firebolt |
| `5` | Select Lightning |
| `6` | Select Teleport |
| `7` | Select Forcepush |
| `T` | Open or close the skill tree |
| `I` | Open or close the inventory |
| `H` | Drink a health potion |
| `M` | Drink a mana potion |
| `Esc` | Close supported menus or open the pause menu |
| `C` in the pause menu | Show the controls panel |
| `Enter` on the title screen | Start the game |

Skills must be unlocked before their hotkeys can select them. You can also select skills through the HUD icons.

<img width="1194" height="797" alt="image" src="https://github.com/user-attachments/assets/5a447294-e75c-4708-897b-dd0a8c19890b" />

### Your first steps

1. Talk to the people around the seaside refuge. Their advice provides both context and practical guidance.
2. Look around the village for chests before heading into the forest.
3. Check merchant stock and drag compatible equipment from your inventory into its gear slot.
4. Spend skill points as new abilities become available.
5. Activate waypoints as you discover them, then interact with an activated waypoint again to choose another unlocked destination.
6. Keep potions ready. Their restoration happens over time, so do not wait until the last possible moment to drink one.

Talking to the refuge's NPCs also restores your health and mana. Exploration is worthwhile: useful supplies and one of the story's important voices are not all placed directly on your starting path.

### Configuration

The base window is 1200 × 800. Window dimensions, the frame cap, fonts, UI layout, skill requirements, item definitions, and NPC dialogue are configured in `settings.py`.

The intended play cap is 60 FPS. The current loop uses elapsed time for movement, not a separate fixed-step simulation.

If the game reports a missing asset, check that the entire `assets/` directory is present and that your terminal is in the project root. If Python reports a syntax error around an f-string, check your interpreter version.

## The world

### Beyond Ebonwood

Ebonwood Wilds is home to the seaside refuge and the beginning of your journey. Johan offers hope, Nuka prepares you for what lies ahead, and Carth Mago carries the memory of an expedition that went farther than it should have.

Their conversations reveal a land overtaken by an evil older and stronger than its people expected. Your task is not merely to survive its creatures, but to push beyond those who tried before you and discover what is spreading the curse.

| Location | What awaits |
| --- | --- |
| Ebonwood Wilds | The seaside refuge, traders, hidden supplies, and a forest already threatened by goblins and the undead |
| Cold Cave | Underground passages inhabited by spiders, zombies, and skeleton knights |
| Dark Moor | A darker wilderness with shamans, occultists, werewolves, and corrupted undead |
| Forgotten Cavern | Deeper underground danger, including antilions and werebears |
| Old Ruins | Broken stonework guarded by cursed knights, minotaurs, golems, and wyverns |
| Icebound Path | Snow-covered terrain and an enemy lineup that includes ice wyverns |
| Cursed Den | The destination at the end of the trail—and the confrontation the survivors have warned you about |

The locations are connected through defined passages. Waypoints provide another route between discovered areas; they are unlocked through exploration rather than all being available from the start.

<img width="1188" height="792" alt="image" src="https://github.com/user-attachments/assets/02af9b82-2ae5-4a5b-aa46-bcc1a9f967c2" />

### Steel and Will

Your abilities grow along two branches. Learning a skill requires a skill point, the appropriate character level, and any prerequisite abilities.

| Path | Skill | Required level | Prerequisites |
| --- | --- | --- | --- |
| Way of the Sword | Kick | 3 | None |
| Way of the Sword | Clash | 5 | Kick |
| Way of the Sword | Whirlwind | 7 | Kick and Clash |
| Way of the Will | Firebolt | 4 | None |
| Way of the Will | Lightning | 6 | Firebolt |
| Way of the Will | Teleport | 7 | Firebolt and Lightning |
| Way of the Will | Forcepush | 9 | Firebolt, Lightning, and Teleport |

The Sword branch expands your close-range attacks, culminating in Whirlwind's ability to threaten nearby enemies. The Will branch adds fire projectiles, targeted lightning, repositioning through Teleport, and Forcepush's concussive knockback.

Defeating enemies awards experience. Leveling grants a skill point and increases maximum health and mana. Discovering every waypoint rewards an additional skill point. Once all skills are unlocked, remaining points can be invested in maximum health or mana through the skill-tree interface.

### Gear and supplies

Equipment defines more than your appearance. Item descriptions carry bonuses to attack, defence, willpower, and speed, which the player system collects when your gear changes.

Attack strengthens melee damage, defence reduces incoming damage, speed affects movement, and willpower reduces spell cooldowns and contributes to selected spell-damage calculations.

Enemy drops and chests supply gold, potions, and equipment. Merchants let you buy supplies and sell unwanted items. Their stock is generated from the game's item catalogue, giving you a reason to inspect more than one shop.

Your journey is remembered while the game is running: defeated enemies, remaining loot, and opened chests belong to their maps and remain in that state when you return. This is session persistence, not a disk-based save system.

## Behind the game

Cursed Lands uses Pygame for its window, input, surfaces, sprites, fonts, and audio. The RPG systems around those building blocks are implemented directly in the project's Python modules.

### Isometric space

The world is simulated on a two-dimensional grid, then projected into an isometric view. With 128 × 64 tiles, screen placement is based on:

```text
screen_x = (grid_x - grid_y) * 64 + camera_offset_x
screen_y = (grid_x + grid_y) * 32 + camera_offset_y
```

Mouse positions are converted back into grid coordinates for navigation and interactions. The player and enemies move between grid destinations while maintaining fractional positions, rather than snapping to each tile on every frame.

The camera follows the player through interpolated offsets, keeping the character near the centre while allowing movement to feel less abrupt.

### Layered maps

`MapManager` loads chunk-based JSON map data, assembles layer grids, and slices tileset images into reusable tile surfaces. Each map also has its own bounds and set of walkable cells.

The renderer draws a visible grid range rather than traversing the entire map for every frame. Layers below the actors are drawn first; `props-high` is drawn after the world objects, allowing foreground scenery to cover them. This is layered rendering, rather than a general depth sort of every object.

Map content and map rules are separated: JSON describes the layout, while `map_data.py` defines titles, passages, spawn regions, enemy lists, chests, terrain sounds, and waypoint positions.

### Navigation and enemy AI

Click-to-move navigation uses a custom A* implementation with a heap-based search frontier. It considers cardinal and diagonal neighbours, and diagonal movement checks adjacent tiles to prevent cutting through blocked corners.

Interaction helpers search for reachable positions near NPCs, chests, and passages, so the character can approach an object rather than needing to stand directly on it.

Melee enemies pursue the player, choose attack positions nearby, and check other enemies when moving. Their path searches account for occupied tiles and claimed destinations. Ranged enemies reposition when necessary and launch directional projectiles. Distance checks and aggression flags determine when enemies engage or stop pursuing.

The final boss extends the ordinary enemy class with its own decision-making and encounter presentation.

<details>
<summary>Boss implementation — spoilers</summary>

Vorthax is implemented by `DemonBoss`, a subclass of `Enemy`. Its behaviour includes ranged fire attacks, teleporting around the player's position, gradual health regeneration, and voice playback with randomized delays. Pending visual effects are passed back to the main loop, while the introduction, death sequence, victory text, and credits are handled by the surrounding game state.

</details>

<img width="1195" height="798" alt="image" src="https://github.com/user-attachments/assets/1e95afa4-dc11-44df-a6f0-08a547557f80" />

### Combat and animation

Player and enemy sprites use directional animation frames and action states such as idle, run, attack, cast, and death. Melee damage is tied to particular animation frames, with per-enemy hit flags preventing repeated damage during the same attack window.

Spells, travelling projectiles, and impact bursts are separate objects with their own update and drawing logic. Projectiles move in one of eight directions, test their path against walkable map cells, and use rectangle collisions for hits. Spell definitions provide animation timing, duration, damage, and mana cost.

The base implementation uses elapsed time for movement and effect lifetimes, while some combat checks run once per frame. The frame cap and simulation are therefore related; the current implementation is not fully frame-rate-independent.

### Items, UI, and audio

Items combine gameplay data with a world sprite, a hover label, and a small toss-and-bounce animation. Equipment bonuses are parsed from item descriptions when the inventory system updates the player's gear.

The HUD brings health, mana, experience, skill selection, cooldown feedback, and a short event log together. Inventory drag-and-drop, skill purchases, trading, tooltips, progressively revealed dialogue, and ending screens are implemented in the display layer.

Audio is organized through `SoundManager` and the mappings in `sound_data.py`. Effects are loaded for reuse, music changes by location, and footsteps draw from grass, concrete, or snow sound sets according to the current map.

### Source guide

| Module | Responsibility |
| --- | --- |
| `main.py` | Initialization, event handling, active game state, updates, and rendering orchestration |
| `settings.py` | Shared configuration, fonts, skill rules, item catalogue, enemy statistics, and NPC dialogue |
| `map.py` | Map loading, tile caches, walkable cells, viewport bounds, and tile rendering |
| `map_data.py` | Location definitions, passages, enemy populations, chests, and waypoints |
| `pathfinding.py` | A* search and movement-neighbour rules |
| `player.py` | Movement, animation, combat, cooldowns, equipment statistics, potions, and progression state |
| `enemy.py` | Enemy behaviour, pursuit, attacks, drops, and the final boss |
| `spell.py`, `projectile.py`, `burst.py` | Spell effects, travelling attacks, knockback, and impact visuals |
| `item.py`, `chest.py` | Loot objects, pickup behaviour, chest contents, and collection |
| `npc.py`, `teleport.py` | NPC animation and merchant stock; waypoint state and animation |
| `display.py` | HUD, inventory, skill tree, trading, dialogue, tooltips, and ending screens |
| `menu.py` | Title screen, pause menu, controls, loading presentation, and game-over flow |
| `gamelog.py` | Short-lived gameplay messages |
| `sounds.py`, `sound_data.py` | Audio playback and asset mappings |
| `utils.py` | Coordinate transforms, interaction destinations, transitions, and supporting helpers |

## Credits

### Design and development

Game programming, world layout, encounters, and dialogue by [cwikmj](https://github.com/cwikmj).

Cursed Lands was developed as a one-person project. Its world was assembled and brought to life through code, but its atmosphere owes a great deal to the artists and musicians whose work fills its forests, caves, battles, and quiet moments.

My sincere thanks to every creator listed below, and to the communities that make their work discoverable. This adventure would have been far quieter—and far emptier—without you.

### Environments and props

| Asset | Creator and attribution |
| --- | --- |
| [Old Ruins Tileset](https://opengameart.org/content/old-ruins-tileset) | rubberduck; additional attribution is recorded in the pack's `CREDITS.txt` |
| [Grassland Tileset](https://opengameart.org/content/grassland-tileset-1) | rubberduck |
| [Cave Tileset](https://opengameart.org/content/cave-tileset) | Clint Bellanger |
| [Isometric Trees](https://opengameart.org/content/isometric-trees-1) | rubberduck |
| [Isometric Props and Tents](https://opengameart.org/content/isometric-props-and-tents) | rubberduck; the source page also acknowledges incorporated CC0 resources |
| [Teleporter Circle](https://opengameart.org/content/teleporter-circle) | Clint Bellanger; texture sources by Luke.RUSTLTD and Yughues |

### Skills and spell effects

| Asset | Creator and attribution |
| --- | --- |
| [2D Spell Effects](https://opengameart.org/content/2d-spell-effects) | Mikodrak — effects created for Nyrthos |
| [Fireball Spell](https://opengameart.org/content/fireball-spell) | Clint Bellanger |
| [Icicle Spell](https://opengameart.org/content/icicle-spell) | Clint Bellanger |
| [Quake Spell](https://opengameart.org/content/quake-spell) | Clint Bellanger |
| [Explosion Effects and More](https://opengameart.org/content/explosion-effects-and-more) | Soluna Software |
| [Circular Skill Icons](https://lazygogo.itch.io/skill-icon) | LazyGogo |

### Player and NPCs

| Asset | Creator and attribution |
| --- | --- |
| [HD 8-Directional Top-Down Character Pack 1](https://smallscaleint.itch.io/hd-8-directional-top-down-character-pack-1) | SmallScaleInt |
| [Wandering Vendor NPC](https://opengameart.org/content/wandering-vendor-npc) | TiZiana, as requested by the asset's attribution instructions |

### Enemies and creatures

Some of these creatures build on another artist's original model, textures, or animation work. Both the original contributors and the creators of the adaptations are acknowledged below.

| Asset | Creator and attribution |
| --- | --- |
| [Skeleton Warrior](https://opengameart.org/content/skeleton-warrior-0) | Clint Bellanger; sword based on a concept sketch by Misha |
| [FLARE Skeleton Mod — Skeletal Knight](https://opengameart.org/content/flare-skeleton-mod-skeletal-knight) | VWolfdog; based on Clint Bellanger's Skeleton Warrior model |
| [FLARE Skeleton Mod — Skeletal Occultist](https://opengameart.org/content/flare-skeleton-mod-skeletal-occultist) | VWolfdog; based on Clint Bellanger's Skeleton Warrior model |
| [Zombie Sprites](https://opengameart.org/content/zombie-sprites) | Clint Bellanger |
| [FLARE Zombie Mod — Pirate Officer Ghost](https://opengameart.org/content/flare-zombie-mod-pirate-officer-ghost) | VWolfdog; based on Clint Bellanger's zombie model |
| [Goblin](https://opengameart.org/content/goblin) | Clint Bellanger |
| [FLARE Mod — Goblin Shaman](https://opengameart.org/content/flare-mod-goblin-shaman) | Short-Ribs; based on Clint Bellanger's goblin model |
| [Spider FLARE Sprite Sheets](https://opengameart.org/content/spider-flare-sprite-sheets) | Wciow — model and texture; John.d.h / johndh — rig and animations |
| [Antlion](https://opengameart.org/content/antlion) | Clint Bellanger |
| [Werebear FLARE Sprite Sheets](https://opengameart.org/content/werebear-flare-sprite-sheets) | johndh |
| [FLARE Mod — Werewolf](https://opengameart.org/content/flare-mod-werewolf) | VWolfdog; based on Clint Bellanger's base human mesh |
| [Minotaur](https://opengameart.org/content/minotaur) | Clint Bellanger |
| [Golem](https://opengameart.org/content/golem-0) | m7600; uses an adapted skeleton armature by Clint Bellanger and textures from Flare |
| [Wyvern](https://opengameart.org/content/wyvern-1) | Clint Bellanger — model and animations; Justin Nichol — diffuse texture; concept inspiration credited to Sarah Benalene |
| [Wyvern Elemental Skins](https://opengameart.org/content/wyvern-elemental-skins) | Justin Nichol — elemental textures; Clint Bellanger — model and animations |
| [Demon — Flare Sprite Sheets](https://opengameart.org/content/demon-flare-sprite-sheets) | ryan.dansie — sprite sheets; umask007 — animated demon model, with upstream model attribution on the [Animated Daemon source page](https://opengameart.org/content/animated-daemon) |

### Music

Thank you to the creators whose music helps give Cursed Lands its atmosphere:

- Alkatrab
- Aurélien Montero
- Anton Z
- phatphrogstudio

### Asset licences

Third-party assets are credited here individually and remain governed by their respective licences or creator-provided terms. Follow the linked source pages and the attribution or licence files supplied with each download for the applicable conditions and any additional contributor credits.

The assets do not all share one licence. This credit section does not relicense them, replace their original notices, or grant permission to redistribute them as standalone resources. Attribution, licence notices, and any requirements concerning modified assets must be preserved as applicable.

### More from the developer

If you enjoy exploring smaller Pygame projects, take a look at [Forgotten Depths](https://github.com/cwikmj/pygame-crawler-forgotten-depths), another game by the same developer.

For contact, feedback, and more projects, visit [cwikmj on GitHub](https://github.com/cwikmj).

---

*Thank you for journeying through the Cursed Lands. May your blade hold and your courage carry you farther than those who came before.*

---

Copyright © 2026 cwikmj@gmail.com. All rights reserved. The source code is available to the public for viewing only. It is prohibited to copy, modify or use the code for commercial or private purposes without the author's permission.
