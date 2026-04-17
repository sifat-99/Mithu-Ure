import sys
try:
    from OpenGL.GL import *
    from OpenGL.GLUT import *
    from OpenGL.GLU import *
except ModuleNotFoundError as e:
    print(f"Missing module: {e.name}")
    print("This script must run with the project's virtual environment.")
    print(r"Use: e:\\GameDevelopment\\.venv\\Scripts\\python.exe -u e:\\GameDevelopment\\main.py")
    print(r"Or activate first: & e:\\GameDevelopment\\.venv\\Scripts\\Activate.ps1")
    sys.exit(1)
import random
import pygame
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

bird_frame = 0
frame_counter = 0

textures = []
bg_textures = []
bg_index = 0
bg_scroll = 0.0

jump_sound = None
bg_sound = None

lives = 3
gems = 0

def play_jump_sound():
    global jump_sound
    if jump_sound:
        jump_sound.play()


def play_background_sound():
    global bg_sound
    if bg_sound:
        bg_sound.play(loops=-1)

def init():
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    global textures, bg_textures, bg_index, jump_sound, bg_sound

    textures = glGenTextures(4)
    for i in range(4):
        try:
            glBindTexture(GL_TEXTURE_2D, textures[i])
            img = Image.open(f'assets/Texture/bird{i+1}.png')
            img = img.transpose(Image.FLIP_TOP_BOTTOM).convert('RGBA')

            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                         img.width, img.height, 0,
                         GL_RGBA, GL_UNSIGNED_BYTE, img.tobytes())

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        except:
            print("Bird texture missing")

    bg_files = ['assets/Texture/bg1.png', 'assets/Texture/bg2.png']
    bg_textures = glGenTextures(len(bg_files))

    for i, path in enumerate(bg_files):
        try:
            glBindTexture(GL_TEXTURE_2D, bg_textures[i])
            img = Image.open(path)
            img = img.transpose(Image.FLIP_TOP_BOTTOM).convert('RGBA')

            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                         img.width, img.height, 0,
                         GL_RGBA, GL_UNSIGNED_BYTE, img.tobytes())

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        except:
            print("BG missing")

    bg_index = random.randrange(len(bg_files))

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

    play_background_sound()

def draw_background():
    global bg_scroll
    glColor3f(1, 1, 1)
    glBindTexture(GL_TEXTURE_2D, bg_textures[bg_index])

    glBegin(GL_QUADS)
    glTexCoord2f(bg_scroll, 0); glVertex2f(-1, -1)
    glTexCoord2f(bg_scroll + 2, 0); glVertex2f(1, -1)
    glTexCoord2f(bg_scroll + 2, 1); glVertex2f(1, 1)
    glTexCoord2f(bg_scroll, 1); glVertex2f(-1, 1)
    glEnd()

def draw_bird():
    glBindTexture(GL_TEXTURE_2D, textures[bird_frame])

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(bird_x - bird_width, bird_y - bird_height)
    glTexCoord2f(1, 0); glVertex2f(bird_x + bird_width, bird_y - bird_height)
    glTexCoord2f(1, 1); glVertex2f(bird_x + bird_width, bird_y + bird_height)
    glTexCoord2f(0, 1); glVertex2f(bird_x - bird_width, bird_y + bird_height)
    glEnd()

def draw_pipe(x, gap_y):
    glDisable(GL_TEXTURE_2D)
    glColor3f(0, 1, 0)

    glBegin(GL_QUADS)
    glVertex2f(x - pipe_width/2, -1)
    glVertex2f(x + pipe_width/2, -1)
    glVertex2f(x + pipe_width/2, gap_y - pipe_gap/2)
    glVertex2f(x - pipe_width/2, gap_y - pipe_gap/2)
    glEnd()

    glBegin(GL_QUADS)
    glVertex2f(x - pipe_width/2, gap_y + pipe_gap/2)
    glVertex2f(x + pipe_width/2, gap_y + pipe_gap/2)
    glVertex2f(x + pipe_width/2, 1)
    glVertex2f(x - pipe_width/2, 1)
    glEnd()

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

    draw_text(-0.95, 0.9, f"Lives: {lives}")
    draw_text(0.6, 0.9, f"Score: {score}")
    draw_text(0.6, 0.8, f"Gems: {gems}")

    if game_over:
        draw_text(-0.25, 0.0, "GAME OVER (R=Restart, Q=Quit)")

    glutSwapBuffers()

def update(value):
    global bird_y, bird_vel, pipes, score, game_over
    global bird_frame, frame_counter, app_running
    global bg_scroll, lives, gems

    if not app_running:
        return

    if not game_over:
        frame_counter += 1
        if frame_counter >= 8:
            bird_frame = (bird_frame + 1) % 4
            frame_counter = 0

        bird_vel += gravity
        bird_y += bird_vel

        for pipe in pipes:
            pipe[0] -= pipe_speed

        bg_scroll += pipe_speed * 0.5
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

            pipe_left = pipe[0] - pipe_width/2
            pipe_right = pipe[0] + pipe_width/2
            gap_top = pipe[1] + pipe_gap/2
            gap_bottom = pipe[1] - pipe_gap/2

            touching_x = (
                bird_right >= pipe_left - margin and
                bird_left <= pipe_right + margin
            )

            if touching_x:
                if bird_top >= gap_top - margin or bird_bottom <= gap_bottom + margin:
                    lives -= 1
                    if lives <= 0:
                        game_over = True

        for pipe in pipes:
            if pipe[0] < bird_x and not pipe[2]:
                score += 1
                gems += 1
                pipe[2] = True

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def keyboard(key, x, y):
    global bird_vel, game_over, pipes, score, bird_y, app_running, lives, gems

    if key == b' ' and not game_over:
        bird_vel = 0.008
        play_jump_sound()

    elif key == b'r':
        bird_y = 0
        bird_vel = 0
        pipes.clear()
        score = 0
        gems = 0
        lives = 3
        game_over = False

    elif key == b'q':
        try:
            pygame.mixer.stop()
            pygame.mixer.quit()
        except Exception:
            pass
        app_running = False
        glutLeaveMainLoop()
        sys.exit()

def main():
    glutInit(sys.argv)
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
