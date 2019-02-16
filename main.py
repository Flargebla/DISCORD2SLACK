import pygame, random
from cgconstants import *

pygame.init()
screen = pygame.display.set_mode((GWIDTH, GHEIGHT))

def drawMainGUI():
    # Setup the main GUI
    screen.fill(WHITE)
    pygame.draw.rect(screen, GREEN, (10, 10, 400, 400), 2)

def drawRandLine():
    randX = random.randint(0, GWIDTH)
    randXX = random.randint(0, GWIDTH)
    randY = random.randint(0, GHEIGHT)
    randYY = random.randint(0, GHEIGHT)
    pygame.draw.line(screen, BLACK, (randX,randY), (randXX,randYY), 5)

done = False
while not done:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # Redraw panels
    drawMainGUI()

    # Draw a random line
    drawRandLine()

    # Update the GUI
    pygame.display.flip()