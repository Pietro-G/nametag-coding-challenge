import pygame
import sys
import os
from button import Button
from updater import read_current_version, check_for_updates

pygame.init()

WIDTH, HEIGHT = 900, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pomodoro Timer")

# Define colors
RED = (186, 73, 73)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (73, 186, 73)
BLUE = (73, 73, 186)
YELLOW = (186, 186, 73)

# List of available colors for background
BACKGROUND_COLORS = [RED, GREEN, BLUE, YELLOW]
background_color = RED  # Default background color

# Initialize clock
CLOCK = pygame.time.Clock()

# Get the base directory for assets
if getattr(sys, 'frozen', False):
    # If running from a frozen executable
    BASE_DIR = sys._MEIPASS
else:
    # If running from a script
    BASE_DIR = os.path.dirname(__file__)

ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
VERSION_FILE = os.path.join(BASE_DIR, 'version.txt')

# Load assets
BACKDROP = pygame.image.load(os.path.join(ASSETS_DIR, "backdrop.png"))
WHITE_BUTTON = pygame.image.load(os.path.join(ASSETS_DIR, "button.png"))

FONT = pygame.font.Font(os.path.join(ASSETS_DIR, "ArialRoundedMTBold.ttf"), 120)
VERSION_FONT = pygame.font.Font(os.path.join(ASSETS_DIR, "ArialRoundedMTBold.ttf"), 20)  # Font for the version box

timer_text = FONT.render("25:00", True, WHITE)
timer_text_rect = timer_text.get_rect(center=(WIDTH/2, HEIGHT/2-25))

START_STOP_BUTTON = Button(WHITE_BUTTON, (WIDTH/2, HEIGHT/2+100), 170, 60, "START", 
                    pygame.font.Font(os.path.join(ASSETS_DIR, "ArialRoundedMTBold.ttf"), 20), "#c97676", "#9ab034")
POMODORO_BUTTON = Button(None, (WIDTH/2-150, HEIGHT/2-140), 120, 30, "Pomodoro", 
                    pygame.font.Font(os.path.join(ASSETS_DIR, "ArialRoundedMTBold.ttf"), 20), "#FFFFFF", "#9ab034")
SHORT_BREAK_BUTTON = Button(None, (WIDTH/2, HEIGHT/2-140), 120, 30, "Short Break", 
                    pygame.font.Font(os.path.join(ASSETS_DIR, "ArialRoundedMTBold.ttf"), 20), "#FFFFFF", "#9ab034")
LONG_BREAK_BUTTON = Button(None, (WIDTH/2+150, HEIGHT/2-140), 120, 30, "Long Break", 
                    pygame.font.Font(os.path.join(ASSETS_DIR, "ArialRoundedMTBold.ttf"), 20), "#FFFFFF", "#9ab034")

POMODORO_LENGTH = 1500  # 1500 secs / 25 mins
SHORT_BREAK_LENGTH = 300  # 300 secs / 5 mins
LONG_BREAK_LENGTH = 900  # 900 secs / 15 mins

current_seconds = POMODORO_LENGTH
pygame.time.set_timer(pygame.USEREVENT, 1000)
started = False

def draw_version_box():
    version_text = read_current_version()
    version_surface = VERSION_FONT.render(version_text, True, BLACK)
    version_rect = pygame.Rect(WIDTH - 160, HEIGHT - 40, 150, 30)  # Position and size of the box
    pygame.draw.rect(SCREEN, WHITE, version_rect)  # Draw the box
    SCREEN.blit(version_surface, version_surface.get_rect(center=version_rect.center))

def draw_color_options():
    colors = BACKGROUND_COLORS
    box_size = 40
    start_x = WIDTH - 250
    start_y = HEIGHT - 100
    for i, color in enumerate(colors):
        color_rect = pygame.Rect(start_x + i * (box_size + 10), start_y, box_size, box_size)
        pygame.draw.rect(SCREEN, color, color_rect)
        pygame.draw.rect(SCREEN, BLACK, color_rect, 2)  # Border around each color box

# Check for updates
def check_for_and_apply_update():
    try:
        if check_for_updates():
            print("An update is available. Please run 'make update' to update the application.")
            pygame.quit()
            sys.exit()
    except Exception as e:
        print(f"An error occurred while checking for updates: {e}")
        pygame.quit()
        sys.exit()

# Run the update check
check_for_and_apply_update()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if START_STOP_BUTTON.check_for_input(mouse_pos):
                started = not started
                START_STOP_BUTTON.text_input = "STOP" if started else "START"
                START_STOP_BUTTON.text = pygame.font.Font(os.path.join(ASSETS_DIR, "ArialRoundedMTBold.ttf"), 20).render(
                    START_STOP_BUTTON.text_input, True, START_STOP_BUTTON.base_color)

            if POMODORO_BUTTON.check_for_input(mouse_pos):
                current_seconds = POMODORO_LENGTH
                started = False
            if SHORT_BREAK_BUTTON.check_for_input(mouse_pos):
                current_seconds = SHORT_BREAK_LENGTH
                started = False
            if LONG_BREAK_BUTTON.check_for_input(mouse_pos):
                current_seconds = LONG_BREAK_LENGTH
                started = False

            # TODO: v1.1
            # new_color = get_color_from_pos(mouse_pos)
            # if new_color:
            #     background_color = new_color

        if event.type == pygame.USEREVENT and started:
            current_seconds -= 1

    SCREEN.fill(background_color)

    # Update and draw elements
    START_STOP_BUTTON.update(SCREEN, pygame.mouse.get_pos())
    POMODORO_BUTTON.update(SCREEN, pygame.mouse.get_pos())
    SHORT_BREAK_BUTTON.update(SCREEN, pygame.mouse.get_pos())
    LONG_BREAK_BUTTON.update(SCREEN, pygame.mouse.get_pos())

    # Draw timer text
    timer_text = FONT.render(f"{current_seconds//60:02}:{current_seconds%60:02}", True, WHITE)
    SCREEN.blit(timer_text, timer_text_rect)

    draw_version_box()
    # TODO: v1.1
    # draw_color_options()

    pygame.display.flip()
    CLOCK.tick(30)
