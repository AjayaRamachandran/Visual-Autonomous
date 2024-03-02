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
pointSelected = [0, 0]

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

points = [
    [[0.1,0.1],[0.2,0.2],[0.3,0.3]],
    [[0.2,0.1],[0.3,0.2],[0.4,0.3]]
]

###### FUNCTIONS ######
def convertCoords(input, direction):
    if direction == "f":
        x, y = input[0] * 900 + 10, input[1] * 900 + 10
    else:
        x, y = (input[0] - 10) / 900, (input[1] - 10) / 900
    return x, y

def detectClosestPoint():
    global pointSelected
    mousePos = convertCoords(pygame.mouse.get_pos(), "b")

    for index, triple in enumerate(points):
        for selectIndex, point in enumerate(triple):
            if sqrt((point[0] - mousePos[0])**2 + (point[1] - mousePos[1])**2) < 0.01:
                pointSelected = [index, selectIndex]
                #print(pointSelected)


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
    for index, triple in enumerate(points):
        if not index == len(points) - 1:
            point1 = points[index][1] # point 1 is the starting point
            point2 = points[index][2] # point 2 is the first handle (off of the first point)
            point3 = points[index + 1][0] # point 3 is the second handle (off of the second point)
            point4 = points[index + 1][1] # point 4 is the ending point

            for t in range(0, 40):
                tValue = t/39
                x = point1[0]*(-tValue**3 + 3*tValue**2 - 3*tValue + 1) + point2[0]*(3*tValue**3 - 6*tValue**2 + 3*tValue) + point3[0]*(-3*tValue**3 + 3*tValue**2) + point4[0]*(tValue**3)
                y = point1[1]*(-tValue**3 + 3*tValue**2 - 3*tValue + 1) + point2[1]*(3*tValue**3 - 6*tValue**2 + 3*tValue) + point3[1]*(-3*tValue**3 + 3*tValue**2) + point4[1]*(tValue**3)
                blitX, blitY = convertCoords([x, y], "f")

                pygame.draw.circle(screen, [255, 255, 255], [blitX, blitY], 2)
    
    ### Draws Points / Handle Points ###
    for index, triple in enumerate(points):
        for dotIndex, dot in enumerate(triple):
            if pointSelected == [index, dotIndex]:
                if dotIndex == 1: #checks to see if the point selected is not a handle
                    triple[dotIndex - 1][0] += convertCoords(pygame.mouse.get_pos(), "b")[0] - dot[0] # changes both handles to stay locked to the center point
                    triple[dotIndex - 1][1] += convertCoords(pygame.mouse.get_pos(), "b")[1] - dot[1]

                    triple[dotIndex + 1][0] += convertCoords(pygame.mouse.get_pos(), "b")[0] - dot[0] # changes both handles to stay locked to the center point
                    triple[dotIndex + 1][1] += convertCoords(pygame.mouse.get_pos(), "b")[1] - dot[1]
                dot[0], dot[1] = convertCoords(pygame.mouse.get_pos(), "b")
        handle1 = tuple(convertCoords(triple[0], "f"))
        midpoint = tuple(convertCoords(triple[1], "f"))
        handle2 = tuple(convertCoords(triple[2], "f"))

        if not index == 0:
            pygame.draw.aaline(screen, [255, 255, 255], handle1, midpoint)
        pygame.draw.aaline(screen, [255, 255, 255], midpoint, handle2)
        if not index == 0:
            pygame.draw.circle(screen, [255, 255, 0], handle1, 5)
        if not index == 0:
            pygame.draw.circle(screen, [255, 255, 255], midpoint, 5)
        else:
            pygame.draw.circle(screen, [255, 0, 0], midpoint, 5)
        pygame.draw.circle(screen, [255, 255, 0], handle2, 5)

    if skillsButton.isClicked():
        mode = "skills"
    elif autonButton.isClicked():
        mode = "auton"

    for event in pygame.event.get(): # checks if program is quit, if so stops the code
        if event.type == pygame.QUIT:
            running = False

    if pygame.mouse.get_pressed()[0]:
        #print("mousedown")
        detectClosestPoint()
    elif not pygame.mouse.get_pressed()[0]:
        pointSelected = [0,0]


    # runs framerate wait time
    clock.tick(fps)
    # update the screen
    pygame.display.update()
    #time.sleep(1)

# quit Pygame
pygame.quit()