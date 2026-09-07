#!/usr/bin/env python3
import pygame
import sys
import math
import random
import argparse

# Internal Render Resolution
FIRE_WIDTH = 320
FIRE_HEIGHT = 240
NUM_STARS = 500

# Classic 37-color fire palette (converted to RGB tuples)
hex_palette = [
    0xFF070707, 0xFF1f0707, 0xFF2f0f07, 0xFF470f07, 0xFF571707, 0xFF671f07,
    0xFF771f07, 0xFF8f2707, 0xFF9f2f07, 0xFFaf3f07, 0xFFbf4707, 0xFFc74707,
    0xFFDF4F07, 0xFFdf5707, 0xFFdf5707, 0xFFd75f07, 0xFFd7670f, 0xFFcf6f0f,
    0xFFcf770f, 0xFFcf7f0f, 0xFFCF8717, 0xFFc78717, 0xFFc78f17, 0xFFc7971f,
    0xFFbf9f1f, 0xFFbf9f1f, 0xFFbfa727, 0xFFbfaf27, 0xFFBfb727, 0xFFbfbf2f,
    0xFFcfc72f, 0xFFcfcf37, 0xFFcfdf3f, 0xFFdfdf47, 0xFFefef4f, 0xFFffff5b,
    0xFFffffff 
]
firePalette = [((c >> 16) & 0xFF, (c >> 8) & 0xFF, c & 0xFF) for c in hex_palette]

# Expanded 3x5 font
font3x5 = [
    ["###", "# #", "###", "# #", "# #"], # 0: A
    ["## ", "# #", "## ", "# #", "## "], # 1: B
    [" ##", "#  ", "#  ", "#  ", " ##"], # 2: C
    ["## ", "# #", "# #", "# #", "## "], # 3: D
    ["###", "#  ", "## ", "#  ", "###"], # 4: E
    ["###", "#  ", "## ", "#  ", "#  "], # 5: F
    [" ##", "#  ", "# #", "# #", " ##"], # 6: G
    ["# #", "# #", "###", "# #", "# #"], # 7: H
    ["###", " # ", " # ", " # ", "###"], # 8: I
    ["  #", "  #", "  #", "# #", " # "], # 9: J
    ["# #", "# #", "## ", "# #", "# #"], # 10: K
    ["#  ", "#  ", "#  ", "#  ", "###"], # 11: L
    ["# #", "###", "###", "# #", "# #"], # 12: M 
    ["###", "# #", "# #", "# #", "# #"], # 13: N 
    ["###", "# #", "# #", "# #", "###"], # 14: O
    ["###", "# #", "###", "#  ", "#  "], # 15: P
    ["###", "# #", "# #", "###", "  #"], # 16: Q
    ["###", "# #", "## ", "# #", "# #"], # 17: R
    [" ##", "#  ", " # ", "  #", "## "], # 18: S
    ["###", " # ", " # ", " # ", " # "], # 19: T
    ["# #", "# #", "# #", "# #", "###"], # 20: U
    ["# #", "# #", "# #", "# #", " # "], # 21: V
    ["# #", "# #", "###", "###", "# #"], # 22: W 
    ["# #", "# #", " # ", "# #", "# #"], # 23: X
    ["# #", "# #", " # ", " # ", " # "], # 24: Y
    ["###", "  #", " # ", "#  ", "###"], # 25: Z
    ["   ", "   ", "   ", "   ", "   "], # 26: Space
    ["   ", "   ", "   ", "   ", " # "], # 27: .
    ["   ", "   ", "###", "   ", "   "], # 28: -
    [" # ", "###", "# #", "###", " # "], # 29: *
    [" # ", " # ", " # ", "   ", " # "], # 30: ! 
    ["#  ", "# #", "## ", "# #", "# #"], # 31: k 
    ["#  ", "#  ", "## ", "# #", "## "], # 32: b 
    ["# #", "# #", " ##", "  #", "## "], # 33: y 
    ["   ", "# #", "###", "# #", "# #"], # 34: m 
    ["   ", " ##", "  #", " ##", "###"], # 35: a 
    ["  #", "  #", " ##", "# #", " ##"], # 36: d 
    ["   ", " ##", "###", "#  ", " ##"]  # 37: e 
]

def drawChar(surface, ch_idx, cx, cy, scale, color):
    if ch_idx < 0 or ch_idx >= len(font3x5): return
    size = max(1, int(2.0 * scale))
    
    for y in range(5):
        for x in range(3):
            if font3x5[ch_idx][y][x] != ' ':
                px = int(cx + x * size)
                py = int(cy + y * size)
                pygame.draw.rect(surface, color, (px, py, size, size))

def drawGlowChar(surface, ch_idx, cx, cy, color):
    if ch_idx < 0 or ch_idx >= len(font3x5): return
    char_surf = pygame.Surface((3, 5))
    char_surf.set_colorkey((0, 0, 0))
    for y in range(5):
        for x in range(3):
            if font3x5[ch_idx][y][x] != ' ':
                char_surf.set_at((x, y), color)
    # Hardware accelerated additive blending
    surface.blit(char_surf, (cx, cy), special_flags=pygame.BLEND_RGB_ADD)

def main():
    parser = argparse.ArgumentParser(description="Linux Python Demoscene by k!M (Python3/pygame)", add_help=False)
    parser.add_argument('-f', '--fullscreen', action='store_true')
    parser.add_argument('-w', '--width', type=int, default=1280)
    parser.add_argument('-h', '--height', type=int, default=720)
    args = parser.parse_args()

    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()

    # Audio Setup
    try:
        pygame.mixer.music.load("bgm.mp3")
        has_bgm = True
    except:
        has_bgm = False
        print("Warning: bgm.mp3 missing. Continuing without BGM.")

    try:
        intro_sfx = pygame.mixer.Sound("intro.mp3")
        intro_channel = pygame.mixer.Channel(0)
        intro_channel.play(intro_sfx, fade_ms=2000)
    except:
        intro_channel = None
        print("Warning: intro.mp3 missing. Continuing without intro.")

    # Window Setup
    flags = pygame.RESIZABLE
    if args.fullscreen:
        flags |= pygame.FULLSCREEN | pygame.SCALED
        pygame.mouse.set_visible(False)
    
    screen = pygame.display.set_mode((args.width, args.height), flags)
    pygame.display.set_caption("Linux Python Demoscene by k!M (Python3/pygame)")
    
    # Internal scaled rendering canvas
    canvas = pygame.Surface((FIRE_WIDTH, FIRE_HEIGHT))
    clock = pygame.time.Clock()

    # Pre-calculate scanlines as an alpha mask for massive Python speedup
    scanline_overlay = pygame.Surface((FIRE_WIDTH, FIRE_HEIGHT), pygame.SRCALPHA)
    for y in range(0, FIRE_HEIGHT, 2):
        pygame.draw.line(scanline_overlay, (0, 0, 0, 128), (0, y), (FIRE_WIDTH, y))

    stars = [{'x': random.randint(-1000, 1000), 'y': random.randint(-1000, 1000), 'z': random.randint(1, 255)} for _ in range(NUM_STARS)]
    
    # 1D Array for blazing fast Python fire updates
    firePixels = bytearray(FIRE_WIDTH * FIRE_HEIGHT)
    
    # Pre-generating random numbers avoids Python function call overhead inside the 76,000-pixel inner loop
    # Fixed: Perfect 33% distribution
    rand_array = [random.randint(0, 3) for _ in range(100000)]
    rand_ptr = 0

    scrollText = "HELLO  DEMOSCENE  ***  WELCOME  TO  THE  PYTHON  TERMINAL  ***  ENJOY  THIS  PARALLAX  STARFIELD  WITH  SPHERICAL  TEXT  SPIN  AND  PIXEL  FIRE  ***  GREETINGS  FROM  NORWAY   ***"
    
    demo_state = 0 
    intro_frames = 0
    time_counter = 0
    running = True
    is_exiting = False
    exit_frames = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if not is_exiting:
                    is_exiting = True
                    if has_bgm: pygame.mixer.music.fadeout(2000)
                    if intro_channel: intro_channel.fadeout(2000)

        canvas.fill((0, 0, 0))

        # --- FIRE UPDATE ---
        for x in range(FIRE_WIDTH):
            firePixels[(FIRE_HEIGHT - 1) * FIRE_WIDTH + x] = 36
            
        # Fast 1D loop
        for x in range(FIRE_WIDTH):
            for y in range(1, FIRE_HEIGHT):
                idx = y * FIRE_WIDTH + x
                srcHeat = firePixels[idx]
                if srcHeat == 0:
                    firePixels[idx - FIRE_WIDTH] = 0
                    continue
                
                randIdx = rand_array[rand_ptr]
                rand_ptr = (rand_ptr + 1) % 100000
                
                dstX = x - randIdx + 1
                if 0 <= dstX < FIRE_WIDTH:
                    newHeat = srcHeat - (randIdx & 1)
                    firePixels[idx - FIRE_WIDTH - x + dstX] = newHeat if newHeat > 0 else 0

        starSpeed = 3.0

        # --- STATE 0: INTRO FADE-IN SCREEN ---
        if demo_state == 0:
            intro_frames += 1
            
            for s in stars:
                s['z'] -= starSpeed
                if s['z'] <= 1.0:
                    s['z'] = 255.0
                    s['x'], s['y'] = random.randint(-1000, 1000), random.randint(-1000, 1000)

            alpha = 0
            if intro_frames < 60: alpha = int((intro_frames * 255) / 60)
            elif intro_frames < 150: alpha = 255
            elif intro_frames < 210: alpha = 255 - int(((intro_frames - 150) * 255) / 60)
            
            if intro_frames >= 240:
                demo_state = 1
                if intro_channel: intro_channel.fadeout(2000)
                if has_bgm: pygame.mixer.music.play(loops=-1, fade_ms=2000)
                
            elif alpha > 0:
                intro_indices = [34, 35, 36, 37, 26, 32, 33, 26, 31, 30, 12]
                scale = 1.0
                size = 2
                char_width = 3 * size
                spacing = 1 * size
                total_width = 11 * char_width + 10 * spacing
                start_x = (FIRE_WIDTH - total_width) // 2
                start_y = (FIRE_HEIGHT - (5 * size)) // 2

                for i, char_idx in enumerate(intro_indices):
                    drawChar(canvas, char_idx, start_x + i * (char_width + spacing), start_y, scale, (alpha, alpha, alpha))
        
        # --- STATE 1: MAIN DEMO ---
        else:
            # Warp Stars
            for i, s in enumerate(stars):
                old_z = s['z']
                s['z'] -= starSpeed
                if s['z'] <= 1.0:
                    s['z'] = 255.0
                    s['x'], s['y'] = random.randint(-1000, 1000), random.randint(-1000, 1000)
                    old_z = s['z']
                
                px = int((s['x'] / s['z']) * 120 + (FIRE_WIDTH / 2))
                py = int((s['y'] / s['z']) * 120 + (FIRE_HEIGHT / 2))
                prev_px = int((s['x'] / old_z) * 120 + (FIRE_WIDTH / 2))
                prev_py = int((s['y'] / old_z) * 120 + (FIRE_HEIGHT / 2))
                
                intensity = max(0, min(255, int(255 - s['z']) - random.randint(0, 19)))
                
                r, g, b = intensity, intensity, intensity
                if i % 3 == 0: b = min(255, intensity + 50)
                elif i % 4 == 0: 
                    r = min(255, intensity + 50)
                    g = min(255, intensity + 20)
                
                pygame.draw.line(canvas, (r, g, b), (prev_px, prev_py), (px, py))

            # Spherical Text
            radius = 110.0
            for i, char in enumerate(scrollText):
                theta = (time_counter * 0.02) - (i * 0.35)
                if theta < 0.0 or theta > 3.14159265: continue
                
                z, x = math.sin(theta), math.cos(theta)
                scale = 0.5 + (z * 1.5)
                cx = (FIRE_WIDTH / 2.0) + (x * radius) - (scale * 4.0)
                cy = (FIRE_HEIGHT / 3.0) + (math.sin(time_counter * 0.02 + x * 2.0) * 40.0)

                char_idx = 26
                if 'A' <= char <= 'Z': char_idx = ord(char) - ord('A')
                elif char == '.': char_idx = 27
                elif char == '-': char_idx = 28
                elif char == '*': char_idx = 29

                depthColor = int(50 + z * 205)
                drawChar(canvas, char_idx, cx, cy, scale, (0, depthColor, 255))

            # Overlay Fire efficiently via PixelArray lock
            pxarray = pygame.PixelArray(canvas)
            for y in range(FIRE_HEIGHT):
                y_off = y * FIRE_WIDTH
                for x in range(FIRE_WIDTH):
                    heat = firePixels[y_off + x]
                    if heat > 3:
                        pxarray[x, y] = firePalette[heat]
            del pxarray # Unlock surface for further drawing

            time_counter += 1

        # Post-Processing: Scanlines
        canvas.blit(scanline_overlay, (0, 0))

        # Glowing Watermark
        wm_indices = [32, 33, 26, 31, 30, 12]
        wm_x = FIRE_WIDTH - 28
        wm_y = FIRE_HEIGHT - 8
        for i, ch_idx in enumerate(wm_indices):
            cx = wm_x + (i * 4)
            for oy in [-1, 0, 1]:
                for ox in [-1, 0, 1]:
                    if ox != 0 or oy != 0:
                        drawGlowChar(canvas, ch_idx, cx + ox, wm_y + oy, (0, 34, 68))
            drawGlowChar(canvas, ch_idx, cx, wm_y, (136, 255, 255))

        # Exit Fade Dimming Layer
        if is_exiting:
            exit_frames += 1
            dim = int((exit_frames / 120.0) * 255)
            if dim > 255: dim = 255
            
            dim_surf = pygame.Surface((FIRE_WIDTH, FIRE_HEIGHT), pygame.SRCALPHA)
            dim_surf.fill((0, 0, 0, dim))
            canvas.blit(dim_surf, (0, 0))
            if exit_frames >= 120: running = False

        # Scale canvas up to actual window resolution and flip
        pygame.transform.scale(canvas, screen.get_size(), screen)
        pygame.display.flip()
        clock.tick(60) # Lock to 60 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()