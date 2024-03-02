###### IMPORT ######

import pygame
import random
import time
from math import *
import numpy as np
import copy

import gui
###### SETUP ######


windowSize = (1440, 920)

pygame.display.set_caption("Visual Autonomous Path Editor") # Sets title of window
screen = pygame.display.set_mode(windowSize) # Sets the dimensions of the window to the windowSize

font = pygame.font.Font(None, 36)

skillsFieldPhoto = "Field Layout Skills.png"
skillsField = pygame.image.load(skillsFieldPhoto)
skills_rect = skillsField.get_rect()
skills_rect.centery = 460
skills_rect.centerx = 460

matchFieldPhoto = "Field Layout Match.png"
matchField = pygame.image.load(matchFieldPhoto)
match_rect = matchField.get_rect()
match_rect.centery = 460
match_rect.centerx = 460

mode = "skills"

###### INITIALIZE ######

fps = 60
clock = pygame.time.Clock()

skillsButton = gui.Button(
    name="skills_button",
    width=250,
    height=60,
    cornerRadius = 15,
    color=[100, 100, 120],
    text="Skills",
    x=1045,
    y=40,
    scale=1,
    fontSize=26
    )

autonButton = gui.Button(
    name="auton_button",
    width=250,
    height=60,
    cornerRadius = 15,
    color=[100, 100, 120],
    text="Match",
    x=1305,
    y=40,
    scale=1,
    fontSize=26
    )

###### POINT MANAGEMENT ######






###### MAINLOOP ######

running = True # Runs the game loop
while running:

    screen.fill((25,25,30))
    if mode == "skills":
        screen.blit(skillsField, skills_rect)
    elif mode == "auton":
        screen.blit(matchField, match_rect)

    skillsButton.draw(screen, mode=int(mode=="skills"))
    autonButton.draw(screen, mode=int(mode=="auton"))

    if skillsButton.isClicked():
        mode = "skills"
    elif autonButton.isClicked():
        mode = "auton"

    for event in pygame.event.get(): # checks if program is quit, if so stops the code
        if event.type == pygame.QUIT:
            running = False
    # runs framerate wait time
    clock.tick(fps)
    # update the screen
    pygame.display.update()
    #time.sleep(1)

# quit Pygame
pygame.quit()