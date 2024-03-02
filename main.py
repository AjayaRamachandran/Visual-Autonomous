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


###### FUNCTIONS ######
def convertCoords(input):
    x, y = input[0] * 900 + 10, input[1] * 900 + 10
    return x, y

###### POINT MANAGEMENT ######

points = [
    [[0.1,0.1],[0.2,0.2],[0.3,0.3]],
    [[0.2,0.1],[0.3,0.2],[0.4,0.3]]
]



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

    ### Draws Curves ###
    for index, point in enumerate(points):
        if not index == len(points) - 1:
            point1 = points[index][1] # point 1 is the starting point
            point2 = points[index][2] # point 2 is the first handle (off of the first point)
            point3 = points[index + 1][0] # point 3 is the second handle (off of the second point)
            point4 = points[index + 1][1] # point 4 is the ending point

            for t in range(0, 40):
                tValue = t/39
                x = point1[0]*(-tValue**3 + 3*tValue**2 - 3*tValue + 1) + point2[0]*(3*tValue**3 - 6*tValue**2 + 3*tValue) + point3[0]*(-3*tValue**3 + 3*tValue**2) + point4[0]*(tValue**3)
                y = point1[1]*(-tValue**3 + 3*tValue**2 - 3*tValue + 1) + point2[1]*(3*tValue**3 - 6*tValue**2 + 3*tValue) + point3[1]*(-3*tValue**3 + 3*tValue**2) + point4[1]*(tValue**3)
                blitX, blitY = convertCoords([x, y])

                pygame.draw.circle(screen, [255, 255, 255], [blitX, blitY], 2)
    
    ### Draws Points / Handle Points ###
    for index, point in enumerate(points):
        handle1 = tuple(convertCoords(point[0]))
        midpoint = tuple(convertCoords(point[1]))
        handle2 = tuple(convertCoords(point[2]))

        pygame.draw.aaline(screen, [255, 255, 255], handle1, midpoint)
        pygame.draw.aaline(screen, [255, 255, 255], midpoint, handle2)

        pygame.draw.circle(screen, [255, 255, 0], handle1, 5)
        pygame.draw.circle(screen, [255, 255, 255], midpoint, 5)
        pygame.draw.circle(screen, [255, 255, 0], handle2, 5)

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