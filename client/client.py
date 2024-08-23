import pygame
import sys
import requests
from button import Button
from updater import CURRENT_VERSION, check_for_updates

pygame.init()

WIDTH, HEIGHT = 900, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pomodoro Timer")

# Define colors
RED = (186, 73, 73)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Initialize clock
CLOCK = pygame.time.Clock()

# Load assets
BACKDROP = pygame.image.load("assets/backdrop.png")
WHITE_BUTTON = pygame.image.load("assets/button.png")

FONT = pygame.font.Font("assets/ArialRoundedMTBold.ttf", 120)
VERSION_FONT = pygame.font.Font("assets/ArialRoundedMTBold.ttf", 20)  # Font for the version box

timer_text = FONT.render("25:00", True, WHITE)
timer_text_rect = timer_text.get_rect(center=(WIDTH/2, HEIGHT/2-25))

START_STOP_BUTTON = Button(WHITE_BUTTON, (WIDTH/2, HEIGHT/2+100), 170, 60, "START", 
                    pygame.font.Font("assets/ArialRoundedMTBold.ttf", 20), "#c97676", "#9ab034")
POMODORO_BUTTON = Button(None, (WIDTH/2-150, HEIGHT/2-140), 120, 30, "Pomodoro", 
                    pygame.font.Font("assets/ArialRoundedMTBold.ttf", 20), "#FFFFFF", "#9ab034")
SHORT_BREAK_BUTTON = Button(None, (WIDTH/2, HEIGHT/2-140), 120, 30, "Short Break", 
                    pygame.font.Font("assets/ArialRoundedMTBold.ttf", 20), "#FFFFFF", "#9ab034")
LONG_BREAK_BUTTON = Button(None, (WIDTH/2+150, HEIGHT/2-140), 120, 30, "Long Break", 
                    pygame.font.Font("assets/ArialRoundedMTBold.ttf", 20), "#FFFFFF", "#9ab034")

POMODORO_LENGTH = 1500  # 1500 secs / 25 mins
SHORT_BREAK_LENGTH = 300  # 300 secs / 5 mins
LONG_BREAK_LENGTH = 900  # 900 secs / 15 mins

current_seconds = POMODORO_LENGTH
pygame.time.set_timer(pygame.USEREVENT, 1000)
started = False

def draw_version_box():
    version_text = CURRENT_VERSION  # Replace with actual version
    version_surface = VERSION_FONT.render(version_text, True, BLACK)
    version_rect = pygame.Rect(WIDTH - 160, HEIGHT - 40, 150, 30)  # Position and size of the box
    pygame.draw.rect(SCREEN, WHITE, version_rect)  # Draw the box
    SCREEN.blit(version_surface, version_surface.get_rect(center=version_rect.center))    

# Run the update check before opening the main window
check_for_updates()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if START_STOP_BUTTON.check_for_input(mouse_pos):
                started = not started
                if started:
                    START_STOP_BUTTON.text_input = "STOP"
                else:
                    START_STOP_BUTTON.text_input = "START"
                START_STOP_BUTTON.text = pygame.font.Font("assets/ArialRoundedMTBold.ttf", 20).render(
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

        if event.type == pygame.USEREVENT and started:
            current_seconds -= 1

    SCREEN.fill(RED)

    # Update and draw elements
    START_STOP_BUTTON.update(SCREEN, pygame.mouse.get_pos())
    POMODORO_BUTTON.update(SCREEN, pygame.mouse.get_pos())
    SHORT_BREAK_BUTTON.update(SCREEN, pygame.mouse.get_pos())
    LONG_BREAK_BUTTON.update(SCREEN, pygame.mouse.get_pos())

    # Draw timer text
    timer_text = FONT.render(f"{current_seconds//60:02}:{current_seconds%60:02}", True, WHITE)
    SCREEN.blit(timer_text, timer_text_rect)

    draw_version_box()

    pygame.display.flip()
    CLOCK.tick(30)
