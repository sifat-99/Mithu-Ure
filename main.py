# pyright: reportWildcardImportFromLibrary=false
import sys
import os
import math

try:
    from OpenGL.GL import *  # type: ignore[import]  # noqa: F401, F403
    from OpenGL.GLUT import *  # type: ignore[import]  # noqa: F401, F403
    from OpenGL.GLU import *  # type: ignore[import]  # noqa: F401, F403
except ModuleNotFoundError as e:
    print(f"Missing module: {e.name}")
    print("This script must run with the project's virtual environment.")
    print(
        r"Use: e:\\GameDevelopment\\.venv\\Scripts\\python.exe -u e:\\GameDevelopment\\main.py"
    )
    print(r"Or activate first: & e:\\GameDevelopment\\.venv\\Scripts\\Activate.ps1")
    sys.exit(1)
import random
import pygame
import time
from PIL import Image

bird_x = -0.6
bird_y = 0.0
bird_vel = 0.0
gravity = -0.0005

pipes = []
score = 0
game_over = False
app_running = True

pipe_width = 0.1
pipe_gap = 0.4
pipe_speed = 0.004

bird_width = 0.06
bird_height = 0.10

bird_frame = 0.0
frame_counter = 0

last_time = 0.0

textures = []
bg_textures = []
bg_index = 0
bg_next = 1
bg_scroll = 0.0

# Cross-fade state
bg_fade_alpha = 0.0  # 0 = fully on current, 1 = fully on next
bg_fade_speed = 0.0  # alpha units per second (set when fade starts)
bg_hold_timer = 0.0  # counts seconds for the hold phase
BG_HOLD_TIME = 15.0  # seconds to display each background
BG_FADE_DURATION = 2.0  # seconds for each crossfade

jump_sound = None
bg_sound = None
coin_sound = None

lives = 3
gems = 0

# Coin system  [x, y, collected]
coins = []
COIN_RADIUS = 0.045


def play_jump_sound():
    global jump_sound
    if jump_sound:
        jump_sound.play()


def play_background_sound():
    global bg_sound
    if bg_sound:
        bg_sound.play(loops=-1)


def init():
    global textures, bg_textures, bg_index, jump_sound, bg_sound, coin_sound, last_time

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_POLYGON_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

    last_time = time.time()

    textures = glGenTextures(4)
    for i in range(4):
        try:
            glBindTexture(GL_TEXTURE_2D, textures[i])
            img = Image.open(f"assets/Texture/bird{i + 1}.png")
            img = img.transpose(Image.FLIP_TOP_BOTTOM).convert("RGBA")

            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGBA,
                img.width,
                img.height,
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                img.tobytes(),
            )

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        except:
            print("Bird texture missing")

    bg_files = [
        "assets/Texture/gemini_bg1.jpg",
        "assets/Texture/gemini_bg2.jpg",
        "assets/Texture/gemini_bg3.jpg",
        "assets/Texture/gemini_bg4.jpg",
        "assets/Texture/gemini_bg5.jpg",
    ]
    bg_textures = glGenTextures(len(bg_files))

    for i, path in enumerate(bg_files):
        try:
            glBindTexture(GL_TEXTURE_2D, bg_textures[i])
            img = Image.open(path)
            img = img.transpose(Image.FLIP_TOP_BOTTOM).convert("RGBA")

            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGBA,
                img.width,
                img.height,
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                img.tobytes(),
            )

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        except Exception as err:
            print(f"BG missing: {err}")

    # pick a random starting background; pre-pick the next (different) one
    bg_index = random.randrange(len(bg_files))
    choices = [i for i in range(len(bg_files)) if i != bg_index]
    bg_next = random.choice(choices)

    try:
        jump_sound = pygame.mixer.Sound("assets/Sound/jump.wav")
    except Exception:
        print("Jump sound not found")
        jump_sound = None

    try:
        bg_sound = pygame.mixer.Sound("assets/Sound/jungleSound.wav")
    except Exception:
        print("Background sound not found")
        bg_sound = None

    try:
        coin_sound = pygame.mixer.Sound("assets/Sound/coin.wav")
        coin_sound.set_volume(0.7)
    except Exception:
        print("Coin sound not found")
        coin_sound = None

    play_background_sound()


def draw_background():
    global bg_scroll

    # --- Draw the current background at full opacity ---
    glColor4f(1.0, 1.0, 1.0, 1.0)
    glBindTexture(GL_TEXTURE_2D, bg_textures[bg_index])
    glBegin(GL_QUADS)
    glTexCoord2f(bg_scroll, 0)
    glVertex2f(-1, -1)
    glTexCoord2f(bg_scroll + 2, 0)
    glVertex2f(1, -1)
    glTexCoord2f(bg_scroll + 2, 1)
    glVertex2f(1, 1)
    glTexCoord2f(bg_scroll, 1)
    glVertex2f(-1, 1)
    glEnd()

    # --- Draw the next background blended on top when fading ---
    if bg_fade_alpha > 0.0:
        glColor4f(1.0, 1.0, 1.0, bg_fade_alpha)
        glBindTexture(GL_TEXTURE_2D, bg_textures[bg_next])
        glBegin(GL_QUADS)
        glTexCoord2f(bg_scroll, 0)
        glVertex2f(-1, -1)
        glTexCoord2f(bg_scroll + 2, 0)
        glVertex2f(1, -1)
        glTexCoord2f(bg_scroll + 2, 1)
        glVertex2f(1, 1)
        glTexCoord2f(bg_scroll, 1)
        glVertex2f(-1, 1)
        glEnd()

    # Reset to white for subsequent drawing
    glColor4f(1.0, 1.0, 1.0, 1.0)


def draw_bird():
    glBindTexture(GL_TEXTURE_2D, textures[int(bird_frame) % 4])

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(bird_x - bird_width, bird_y - bird_height)
    glTexCoord2f(1, 0)
    glVertex2f(bird_x + bird_width, bird_y - bird_height)
    glTexCoord2f(1, 1)
    glVertex2f(bird_x + bird_width, bird_y + bird_height)
    glTexCoord2f(0, 1)
    glVertex2f(bird_x - bird_width, bird_y + bird_height)
    glEnd()


def draw_pipe(x, gap_y):
    glDisable(GL_TEXTURE_2D)

    def draw_node(nx, ny):
        glBegin(GL_QUADS)
        glColor3f(0.05, 0.35, 0.05)
        glVertex2f(nx - pipe_width / 2 - 0.008, ny - 0.01)
        glVertex2f(nx + pipe_width / 2 + 0.008, ny - 0.01)
        glVertex2f(nx + pipe_width / 2 + 0.008, ny + 0.01)
        glVertex2f(nx - pipe_width / 2 - 0.008, ny + 0.01)
        glEnd()
        glColor3f(0.6, 0.9, 0.5)
        glBegin(GL_LINES)
        glVertex2f(nx - pipe_width / 2 - 0.008, ny + 0.01)
        glVertex2f(nx + pipe_width / 2 + 0.008, ny + 0.01)
        glEnd()

    # Left half bottom
    glBegin(GL_QUADS)
    glColor3f(0.1, 0.5, 0.1)
    glVertex2f(x - pipe_width / 2, -1)
    glColor3f(0.5, 0.9, 0.4)
    glVertex2f(x, -1)
    glVertex2f(x, gap_y - pipe_gap / 2)
    glColor3f(0.1, 0.5, 0.1)
    glVertex2f(x - pipe_width / 2, gap_y - pipe_gap / 2)
    glEnd()

    # Right half bottom
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.9, 0.4)
    glVertex2f(x, -1)
    glColor3f(0.05, 0.3, 0.05)
    glVertex2f(x + pipe_width / 2, -1)
    glVertex2f(x + pipe_width / 2, gap_y - pipe_gap / 2)
    glColor3f(0.5, 0.9, 0.4)
    glVertex2f(x, gap_y - pipe_gap / 2)
    glEnd()

    # Nodes for bottom pipe
    nb = gap_y - pipe_gap / 2 - 0.15
    while nb > -1.0:
        draw_node(x, nb)
        nb -= 0.3

    # Left half top
    glBegin(GL_QUADS)
    glColor3f(0.1, 0.5, 0.1)
    glVertex2f(x - pipe_width / 2, gap_y + pipe_gap / 2)
    glColor3f(0.5, 0.9, 0.4)
    glVertex2f(x, gap_y + pipe_gap / 2)
    glVertex2f(x, 1)
    glColor3f(0.1, 0.5, 0.1)
    glVertex2f(x - pipe_width / 2, 1)
    glEnd()

    # Right half top
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.9, 0.4)
    glVertex2f(x, gap_y + pipe_gap / 2)
    glColor3f(0.05, 0.3, 0.05)
    glVertex2f(x + pipe_width / 2, gap_y + pipe_gap / 2)
    glVertex2f(x + pipe_width / 2, 1)
    glColor3f(0.5, 0.9, 0.4)
    glVertex2f(x, 1)
    glEnd()

    # Nodes for top pipe
    nt = gap_y + pipe_gap / 2 + 0.15
    while nt < 1.0:
        draw_node(x, nt)
        nt += 0.3

    # Caps
    glColor3f(0.2, 0.6, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(x - pipe_width / 2, gap_y - pipe_gap / 2 - 0.02)
    glVertex2f(x + pipe_width / 2, gap_y - pipe_gap / 2 - 0.02)
    glVertex2f(x + pipe_width / 2, gap_y - pipe_gap / 2)
    glVertex2f(x - pipe_width / 2, gap_y - pipe_gap / 2)
    glEnd()
    glBegin(GL_QUADS)
    glVertex2f(x - pipe_width / 2, gap_y + pipe_gap / 2)
    glVertex2f(x + pipe_width / 2, gap_y + pipe_gap / 2)
    glVertex2f(x + pipe_width / 2, gap_y + pipe_gap / 2 + 0.02)
    glVertex2f(x - pipe_width / 2, gap_y + pipe_gap / 2 + 0.02)
    glEnd()

    glEnable(GL_TEXTURE_2D)


def draw_coin(cx, cy):
    """Draw a shiny golden dollar coin using OpenGL primitives."""
    glDisable(GL_TEXTURE_2D)
    segments = 32
    r = COIN_RADIUS

    # Outer dark-gold ring
    glColor3f(0.72, 0.53, 0.04)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx, cy)
    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        glVertex2f(cx + math.cos(angle) * r, cy + math.sin(angle) * r)
    glEnd()

    # Main gold disk
    glColor3f(1.0, 0.82, 0.1)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx, cy)
    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        glVertex2f(cx + math.cos(angle) * r * 0.85, cy + math.sin(angle) * r * 0.85)
    glEnd()

    # Bright highlight arc (top-left)
    glColor3f(1.0, 0.96, 0.6)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx - r * 0.18, cy + r * 0.18)
    for i in range(segments // 2 + 1):
        angle = math.pi * 0.5 + math.pi * i / (segments // 2)
        glVertex2f(cx + math.cos(angle) * r * 0.55, cy + math.sin(angle) * r * 0.55)
    glEnd()

    # Dollar sign '$' drawn with thick lines
    glColor3f(0.55, 0.36, 0.0)
    glLineWidth(2.5)
    # Vertical bar of '$'
    glBegin(GL_LINES)
    glVertex2f(cx, cy - r * 0.55)
    glVertex2f(cx, cy + r * 0.55)
    glEnd()
    # Two horizontal humps approximated as quads
    hump_h = r * 0.18
    hump_w = r * 0.38
    # Top hump
    glBegin(GL_LINE_STRIP)
    for i in range(segments // 2 + 1):
        angle = math.pi * i / (segments // 2)
        glVertex2f(
            cx + math.cos(angle) * hump_w, cy + r * 0.15 + math.sin(angle) * hump_h
        )
    glEnd()
    # Bottom hump
    glBegin(GL_LINE_STRIP)
    for i in range(segments // 2 + 1):
        angle = math.pi + math.pi * i / (segments // 2)
        glVertex2f(
            cx + math.cos(angle) * hump_w, cy - r * 0.15 + math.sin(angle) * hump_h
        )
    glEnd()
    glLineWidth(1.0)

    glEnable(GL_TEXTURE_2D)


def draw_text(x, y, text):
    glDisable(GL_TEXTURE_2D)
    glColor3f(1, 1, 1)
    glRasterPos2f(x, y)
    for c in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
    glEnable(GL_TEXTURE_2D)


def display():
    glClear(GL_COLOR_BUFFER_BIT)

    draw_background()
    draw_bird()

    for pipe in pipes:
        draw_pipe(pipe[0], pipe[1])

    # Draw coins that haven't been collected
    for coin in coins:
        if not coin[2]:
            draw_coin(coin[0], coin[1])

    draw_text(-0.95, 0.9, f"Lives: {lives}")
    draw_text(0.6, 0.9, f"Score: {score}")
    draw_text(0.6, 0.8, f"Coins: {gems}")

    if game_over:
        draw_text(-0.25, 0.0, "GAME OVER (R=Restart, Q=Quit)")

    glutSwapBuffers()


def update(value):
    global bird_y, bird_vel, pipes, score, game_over
    global bird_frame, frame_counter, app_running
    global bg_scroll, lives, gems, last_time
    global bg_index, bg_next, bg_fade_alpha, bg_fade_speed, bg_hold_timer
    global coins

    if not app_running:
        return

    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time
    dt = min(dt, 0.1)
    factor = dt * 60.0

    if not game_over:
        frame_counter += 1 * factor
        if frame_counter >= 8:
            bird_frame = (bird_frame + 1) % 4
            frame_counter = 0

        bird_vel += gravity * factor
        bird_y += bird_vel * factor

        for pipe in pipes:
            pipe[0] -= pipe_speed * factor

        bg_scroll += pipe_speed * 0.5 * factor
        if bg_scroll > 1:
            bg_scroll -= 1

        pipes[:] = [p for p in pipes if p[0] > -1.2]

        if not pipes or pipes[-1][0] < 0.5:
            pipes.append([1.0, random.uniform(-0.3, 0.3), False])

        for pipe in pipes:
            hitbox_scale = 0.75
            margin = 0.002

            bird_left = bird_x - bird_width * hitbox_scale
            bird_right = bird_x + bird_width * hitbox_scale
            bird_top = bird_y + bird_height * hitbox_scale
            bird_bottom = bird_y - bird_height * hitbox_scale

            pipe_left = pipe[0] - pipe_width / 2
            pipe_right = pipe[0] + pipe_width / 2
            gap_top = pipe[1] + pipe_gap / 2
            gap_bottom = pipe[1] - pipe_gap / 2

            touching_x = (
                bird_right >= pipe_left - margin and bird_left <= pipe_right + margin
            )

            if touching_x:
                if bird_top >= gap_top - margin or bird_bottom <= gap_bottom + margin:
                    lives -= 1
                    if lives <= 0:
                        game_over = True

        for pipe in pipes:
            if pipe[0] < bird_x and not pipe[2]:
                score += 1
                pipe[2] = True

        # Move coins
        for coin in coins:
            if not coin[2]:
                coin[0] -= pipe_speed * factor

        # Remove off-screen coins
        coins[:] = [c for c in coins if c[0] > -1.3]

        # Spawn a new coin roughly every 2nd pipe (random chance in gap area)
        # We attach coins to newly-spawned pipes
        if pipes and not pipes[-1][2]:
            # Check if this pipe just entered (x close to 1.0) and has no coin yet
            newest = pipes[-1]
            has_coin = any(abs(c[0] - newest[0]) < 0.05 for c in coins)
            if not has_coin and newest[0] > 0.95 and random.random() < 0.6:
                # Spawn coin in the middle of the gap at a random y within it
                gap_y = newest[1]
                coin_y = gap_y + random.uniform(-pipe_gap / 2 * 0.6, pipe_gap / 2 * 0.6)
                coins.append([newest[0], coin_y, False])

        # Coin collection
        for coin in coins:
            if not coin[2]:
                dx = abs(coin[0] - bird_x)
                dy = abs(coin[1] - bird_y)
                if (
                    dx < COIN_RADIUS + bird_width * 0.7
                    and dy < COIN_RADIUS + bird_height * 0.7
                ):
                    coin[2] = True
                    gems += 1
                    if coin_sound:
                        coin_sound.play()

    # --- Background crossfade timer (always running, even on game over) ---
    if bg_fade_alpha > 0.0:
        # Currently fading in the next background
        bg_fade_alpha += bg_fade_speed * dt
        if bg_fade_alpha >= 1.0:
            # Fade complete – promote next to current
            bg_index = bg_next
            bg_fade_alpha = 0.0
            bg_fade_speed = 0.0
            bg_hold_timer = 0.0
            # Pre-pick the *next* one (different from current)
            choices = [i for i in range(len(bg_textures)) if i != bg_index]
            bg_next = random.choice(choices)
    else:
        bg_hold_timer += dt
        if bg_hold_timer >= BG_HOLD_TIME:
            # Start fading to the pre-picked next background
            bg_fade_alpha = 0.001  # kick it off
            bg_fade_speed = 1.0 / BG_FADE_DURATION

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)


def keyboard(key, x, y):
    global bird_vel, game_over, pipes, score, bird_y, app_running, lives, gems

    if key == b" " and not game_over:
        bird_vel = 0.008
        play_jump_sound()

    elif key == b"r":
        bird_y = 0
        bird_vel = 0
        pipes.clear()
        coins.clear()
        score = 0
        gems = 0
        lives = 3
        game_over = False

    elif key == b"q":
        try:
            pygame.mixer.stop()
            pygame.mixer.quit()
        except Exception:
            pass
        os._exit(0)


def main():
    glutInit(sys.argv)

    try:
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_MULTISAMPLE)
    except:
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)

    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Flappy Bird FIXED")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, -1, 1)

    try:
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
    except Exception:
        print("pygame mixer init failed")

    init()

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutTimerFunc(0, update, 0)

    glutMainLoop()


if __name__ == "__main__":
    main()
