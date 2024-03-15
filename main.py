###### IMPORT ######

import pygame
import random
import time
from math import *
import numpy as np
import copy
import bisect

import gui
import inout as io

###### SETUP ######

windowSize = (1440, 920)

pygame.display.set_caption("Visual Autonomous Path Editor") # Sets title of window
screen = pygame.display.set_mode(windowSize) # Sets the dimensions of the window to the windowSize
icon = pygame.image.load("AppIcon.png")
pygame.display.set_icon(icon)

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

deleteIcon = "DeleteIcon.png"
delete = pygame.image.load(deleteIcon)
delete_rect = delete.get_rect()

mode = "skills"
pointSelected = [0, 0]
selector = "edit"
initialReverse = False
totalCurve = []

POINTSPACING = 0.00694444444
SAMPLINGRESOLUTION = 500

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

addPTButton = gui.Button(
    name="passthrough_button",
    width=510,
    height=60,
    cornerRadius = 15,
    color=[100, 120, 100],
    text="Add Passthrough Point",
    x=1175,
    y=200,
    scale=1,
    fontSize=26
    )

addTurnButton = gui.Button(
    name="turning_button",
    width=510,
    height=60,
    cornerRadius = 15,
    color=[100, 120, 100],
    text="Add Turning Point",
    x=1175,
    y=270,
    scale=1,
    fontSize=26
    )

addReflexButton = gui.Button(
    name="reflex_button",
    width=510,
    height=60,
    cornerRadius = 15,
    color=[100, 120, 100],
    text="Add Reflex Point",
    x=1175,
    y=340,
    scale=1,
    fontSize=26
    )

deleteButton = gui.Button(
    name="delete_button",
    width=510,
    height=60,
    cornerRadius = 15,
    color=[120, 100, 100],
    text="Delete Point",
    x=1175,
    y=480,
    scale=1,
    fontSize=26
    )

startInReverse = gui.Button(
    name="reversing_button",
    width=250,
    height=60,
    cornerRadius = 15,
    color=[35, 35, 43],
    text="Start in Reverse",
    x=1045,
    y=875,
    scale=1,
    fontSize=26
    )

startForward = gui.Button(
    name="forward_button",
    width=250,
    height=60,
    cornerRadius = 15,
    color=[35, 35, 43],
    text="Start Forward",
    x=1305,
    y=875,
    scale=1,
    fontSize=26
    )

export = gui.Button(
    name="export_button",
    width=510,
    height=60,
    cornerRadius = 15,
    color=[148, 132, 84],
    text="Export",
    x=1175,
    y=620,
    scale=1,
    fontSize=26
    )

###### POINT MANAGEMENT ######

points = [
    [[0.2,0.2],[0.3,0.3],[0.2,0.2]]
]

pointTypes = [
    "reflex"
]

###### FUNCTIONS ######

def dist(point1, point2): # calculates the distance between two points
    return sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

def dir(point1, point2): # calculates the direction between one point and another
    return atan2((point2[1] - point1[1]), (point2[0] - point1[0]))

def lookUpTable(table, inputY): # a function that is given a list of values Y with equal spaced X, can give any value of X given Y
    leftPoint = [bisect.bisect_left(table, inputY) - 1, table[bisect.bisect_left(table, inputY) - 1]]
    rightPoint = [bisect.bisect_left(table, inputY), table[bisect.bisect_left(table, inputY)]]

    return (((inputY - leftPoint[1]) / (rightPoint[1] - leftPoint[1])) + leftPoint[0]) / len(table)

def convertCoords(input, direction): # converts the 0 - 1 UV coords of the field into screen coordinates and vice versa
    if direction == "f":
        x, y = input[0] * 900 + 10, input[1] * 900 + 10
    else:
        x, y = (input[0] - 10) / 900, (input[1] - 10) / 900
    return x, y

def detectClosestPoint(): # function to detect which point on the field is closest to mouse and whether it is eligible for dragging
    global pointSelected
    mousePos = convertCoords(pygame.mouse.get_pos(), "b")

    for index, group in enumerate(points):
        for selectIndex, point in enumerate(group):
            if dist(point, mousePos) < 0.01 and pointSelected == [0,0]:
                pointSelected = [index, selectIndex]

def generateOutput(): # generates a text file that contains the path data
    output = open("output.txt", "w")
    output.write("double coordinates[][2] = {")
    lengths = []
    for index1, curve in enumerate(totalCurve): # structure of file is a list of points (the waypoints), then a second list which contains the arclengths between the handles
        for index2, point in enumerate(curve):
            output.write("{" + f"{point[0]}, {point[1]}" + "}")
            if index2 == len(curve) - 1 and index1 == len(totalCurve) - 1:
                output.write("")
            else:
                output.write(",")
        lengths.append(len(curve))
    output.write("};\n")
    output.write("double curveLengths[] = {")
    for index, length in enumerate(lengths):
        output.write(f"{length}")
        if index != len(lengths) - 1:
            output.write(",")
    output.write("};\n")
    output.close()
    io.showOutput("output.txt") # shows the text file to the screen using subprocess

###### MAINLOOP ######

running = True # Runs the game loop
while running:
    screen.fill((25,25,30))
    if mode == "skills":
        screen.blit(skillsField, skills_rect)
    elif mode == "auton":
        screen.blit(matchField, match_rect)

    # draws all the GUI elements to the screen using the GUI library
    skillsButton.draw(screen, mode=int(mode=="skills"))
    autonButton.draw(screen, mode=int(mode=="auton"))
    addPTButton.draw(screen)
    addTurnButton.draw(screen)
    addReflexButton.draw(screen)
    deleteButton.draw(screen)
    startInReverse.draw(screen, mode=int(initialReverse))
    startForward.draw(screen, mode=int(not initialReverse))
    export.draw(screen)

    ### Draws Curves ###
    reverse = initialReverse
    totalCurve = []
    for index, group in enumerate(points):
        if not index == len(points) - 1:
            point1 = points[index][1] # point 1 is the starting point
            point2 = points[index][2] # point 2 is the first handle (off of the first point)
            point3 = points[index + 1][0] # point 3 is the second handle (off of the second point)
            point4 = points[index + 1][1] # point 4 is the ending point

            prevPoint = [point1[0], point1[1]]
            distances = []
            for t in range(0, SAMPLINGRESOLUTION):
                tValue = t/(SAMPLINGRESOLUTION - 1)
                x = point1[0]*(-tValue**3 + 3*tValue**2 - 3*tValue + 1) + point2[0]*(3*tValue**3 - 6*tValue**2 + 3*tValue) + point3[0]*(-3*tValue**3 + 3*tValue**2) + point4[0]*(tValue**3)
                y = point1[1]*(-tValue**3 + 3*tValue**2 - 3*tValue + 1) + point2[1]*(3*tValue**3 - 6*tValue**2 + 3*tValue) + point3[1]*(-3*tValue**3 + 3*tValue**2) + point4[1]*(tValue**3)

                distToLastPoint = dist([x, y], prevPoint) # calculates the distance between current sample point and the last
                distances.append(distToLastPoint)
                prevPoint = [x, y]

            arcLength = sum(distances)
            cumulativeSum = 0
            for iter in range(len(distances)): # finds the arclength of a curve by summing the distances between all the sample points
                distances[iter] += cumulativeSum
                cumulativeSum = distances[iter]
            
            numSamplePoints = round(arcLength / POINTSPACING) # ensures that all points on the field will be equally spaced by making the # points in a curve proportional to its arclength

            equallySpacedPoints = []
            for iter in range(numSamplePoints): # 
                equallySpacedPoints.append(lookUpTable(distances, arcLength * iter / numSamplePoints)) # uses a lookup table to sample points that are equally spaced by distance, not t value

            pointCoords = []
            for tValue in equallySpacedPoints: # bezier formula, using Freya Holmer's brilliant explanation about everything bezier curve-related
                x = point1[0]*(-tValue**3 + 3*tValue**2 - 3*tValue + 1) + point2[0]*(3*tValue**3 - 6*tValue**2 + 3*tValue) + point3[0]*(-3*tValue**3 + 3*tValue**2) + point4[0]*(tValue**3)
                y = point1[1]*(-tValue**3 + 3*tValue**2 - 3*tValue + 1) + point2[1]*(3*tValue**3 - 6*tValue**2 + 3*tValue) + point3[1]*(-3*tValue**3 + 3*tValue**2) + point4[1]*(tValue**3)
                pointCoords.append([x, y])
                blitX, blitY = convertCoords([x, y], "f")
                if reverse:
                    pygame.draw.circle(screen, [80, 80, 80], [blitX, blitY], 2)
                else:
                    pygame.draw.circle(screen, [255, 255, 255], [blitX, blitY], 2)
            totalCurve.append(pointCoords)
            if pointTypes[index + 1] == "reflex": # in the special case of reflex points, the direction we travel in flips
                reverse = not reverse

    ### Draws Points / Handle Points ###
    for index, group in enumerate(points):
        for dotIndex, dot in enumerate(group):
            if pointSelected == [index, dotIndex]:
                if selector == "edit":
                    if dotIndex == 1: #checks to see if the point selected is not a handle
                        group[0][0] += convertCoords(pygame.mouse.get_pos(), "b")[0] - dot[0] # changes both handles to stay locked to the center point
                        group[0][1] += convertCoords(pygame.mouse.get_pos(), "b")[1] - dot[1]

                        group[2][0] += convertCoords(pygame.mouse.get_pos(), "b")[0] - dot[0] # changes both handles to stay locked to the center point
                        group[2][1] += convertCoords(pygame.mouse.get_pos(), "b")[1] - dot[1]

                    if (dotIndex == 0 or dotIndex == 2) and not index == 0 and pointTypes[index] == "passthrough": # checks to see if the point selected is an in-handle, if so adjust out-handle to be on opposite side of point
                        if dotIndex == 0:
                            outHandleLength = dist(group[1], group[2]) # gets distance between point and out handle
                            outHandleDirection = dir(group[0], group[1]) # gets the direction that the out handle needs to be facing
                            group[2][0] = group[1][0] + outHandleLength * cos(outHandleDirection)
                            group[2][1] = group[1][1] + outHandleLength * sin(outHandleDirection)
                        else:
                            inHandleLength = dist(group[1], group[0]) # gets distance between point and in handle
                            inHandleDirection = dir(group[2], group[1]) # gets the direction that the in handle needs to be facing
                            group[0][0] = group[1][0] + inHandleLength * cos(inHandleDirection)
                            group[0][1] = group[1][1] + inHandleLength * sin(inHandleDirection)
                        dot[0], dot[1] = convertCoords(pygame.mouse.get_pos(), "b")
                    elif (dotIndex == 0 or dotIndex == 2) and not index == 0 and pointTypes[index] == "reflex":
                        dot[0], dot[1] = convertCoords(pygame.mouse.get_pos(), "b")
                        if dotIndex == 0:
                            group[2][0], group[2][1] = dot[0], dot[1]
                        elif dotIndex == 2:
                            group[0][0], group[0][1] = dot[0], dot[1]
                    else:
                        dot[0], dot[1] = convertCoords(pygame.mouse.get_pos(), "b")

        handle1 = tuple(convertCoords(group[0], "f"))
        midpoint = tuple(convertCoords(group[1], "f"))
        handle2 = tuple(convertCoords(group[2], "f"))
        
        if not index == 0:
            pygame.draw.aaline(screen, [255, 255, 255], handle1, midpoint)
        pygame.draw.aaline(screen, [255, 255, 255], midpoint, handle2)

        if not index == 0:
            if pointTypes[index] == "passthrough": # makes the in handle yellow if it is passthrough point, green if it is turning
                pygame.draw.circle(screen, [255, 255, 0], handle1, 5)
            elif pointTypes[index] == "turning":
                pygame.draw.circle(screen, [0, 255, 0], handle1, 5)

        pygame.draw.circle(screen, [255, 255, 255], midpoint, 5)

        if pointTypes[index] == "passthrough": # makes the out handle yellow if it is passthrough point, red if it is turning
            pygame.draw.circle(screen, [255, 255, 0], handle2, 5)
        elif pointTypes[index] == "turning":
            pygame.draw.circle(screen, [255, 0, 0], handle2, 5)
        elif pointTypes[index] == "reflex":
            pygame.draw.circle(screen, [0, 0, 255], handle2, 5)

    # detects if any GUI elements are interacted with, using GUI library
    if skillsButton.isClicked():
        mode = "skills"
    elif autonButton.isClicked():
        mode = "auton"
    elif startInReverse.isClicked():
        initialReverse = True
    elif startForward.isClicked():
        initialReverse = False
    elif addPTButton.isClicked():
        if not points[len(points) - 1][0] == [0.4,0.4]:
            points.append([[0.4,0.4],[0.5,0.5],[0.6,0.6]])
            pointTypes.append("passthrough")
    elif addTurnButton.isClicked():
        if not points[len(points) - 1][0] == [0.4,0.4]:
            points.append([[0.4,0.4],[0.5,0.5],[0.6,0.6]])
            pointTypes.append("turning")
    elif addReflexButton.isClicked():
        if not points[len(points) - 1][0] == [0.4,0.4]:
            points.append([[0.4,0.4],[0.5,0.5],[0.4,0.4]])
            pointTypes.append("reflex")
    elif deleteButton.isClicked():
        selector = "delete"
    elif export.isClicked() and not pressingExport:
        generateOutput()
        pressingExport = True
    if not export.isClicked():
        pressingExport = False

    for index, group in enumerate(points): # detects if any points are deleted
        for dotIndex, dot in enumerate(group):
            if pointSelected == [index, dotIndex]:
                if selector == "delete" and not index == 0:
                    points.pop(index)
                    pointTypes.pop(index)
                    selector = "edit"
                    pointSelected = [0,0]
                    print(len(points))

    if selector == "delete": # shows little delete icon on mouse when in delete mode
        delete_rect.centery = pygame.mouse.get_pos()[1]
        delete_rect.centerx = pygame.mouse.get_pos()[0]
        screen.blit(delete, delete_rect)

    for event in pygame.event.get(): # checks if program is quit, if so stops the code
        if event.type == pygame.QUIT:
            running = False

    if pygame.mouse.get_pressed()[0]:
        detectClosestPoint() # runs code to allow points to detect when clicked, so they may be dragged around
    elif not pygame.mouse.get_pressed()[0]:
        pointSelected = [0,0]

    # runs framerate wait time
    clock.tick(fps)
    # update the screen
    pygame.display.update()

# quit Pygame
pygame.quit()