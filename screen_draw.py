# Adam Rilatt
# 05 / 09 / 20
# Terminal Trouble -- Screen Drawing

import random
import msvcrt
import math
import time
import sys
import os

###########################
#       CONSTANTS         #
###########################

FRAMERATE = 20      # default 10

SCREEN_WIDTH = 200  # default 120
SCREEN_HEIGHT = 50  # default 36

CEILING_SHADE = " "
FLOOR_SHADE = "_"
#WALL_SHADES = [
#    " ",
#    "▒",
#    "▓",
#    "█"
#]
WALL_SHADES = list(
    "@%&M*akdqmOQCUXcuxjt\(1-+<il;,^' "
)[::-1]

MAP = [
    "################################",
    "#...#..........#.............###",
    "#.........######..............##",
    "#...#..........#...............#",
    "#####...###....................#",
    "#..............#...............#",
    "################################"
]
MAP_HEIGHT = len(MAP)
MAP_WIDTH = len(MAP[0])

PLAYER_FOV = math.pi / 3
PLAYER_VIEW_DISTANCE = 16
PLAYER_MOVE_SPEED = 2
PLAYER_TURN_SPEED = 2

###########################
#       FUNCTIONS         #
###########################

def coord_write (string, y, x):
    # move the pointer to the specified position and write a string there
    sys.stdout.write("\033[%d;%dH" % (y, x))
    sys.stdout.write(str(string))
    
    return

def screen_draw ():
    # raycasts to determine how the screen should be drawn, then writes to
    # the terminal.
    
    screen = list(" " * SCREEN_WIDTH * SCREEN_HEIGHT)
    
    # for each column on the screen:
    for x in range(SCREEN_WIDTH):
        
        # determine angle of raycast
        rayAngle = (playerA - PLAYER_FOV / 2) + (x / SCREEN_WIDTH) * PLAYER_FOV
        
        # vector parts of that ray angle so that the ray can be cast in 2D space
        rayAngleX = math.sin(rayAngle)
        rayAngleY = math.cos(rayAngle)
        
        distanceToWall = 0
        hitWall = False
        
        while not hitWall and distanceToWall < PLAYER_VIEW_DISTANCE:
            
            # cast the ray forward by increasing amounts
            distanceToWall += 0.1
            testX = int(playerX + rayAngleX * distanceToWall)
            testY = int(playerY + rayAngleY * distanceToWall)
            
            # if raycast exceeds the map bounds, stop casting the ray
            if testX < 0 or testX > MAP_WIDTH or testY < 0 or testY > MAP_HEIGHT:
                hitWall = True
                distanceToWall = PLAYER_VIEW_DISTANCE
            
            # wall square hit
            elif MAP[testY][testX] == "#":
                hitWall = True
        
        # determine the top and bottom of the section of wall to be drawn
        ceilingEnd = (SCREEN_HEIGHT / 2) - SCREEN_HEIGHT / distanceToWall
        floorEnd = SCREEN_HEIGHT - ceilingEnd
        
        
        # choose wall shading based on distance from wall
        wallShade = WALL_SHADES[0]
        n = len(WALL_SHADES)
        for i in range(len(WALL_SHADES)):
            
            if distanceToWall <= PLAYER_VIEW_DISTANCE / n:
                wallShade = WALL_SHADES[n - 1]
                break
                
            else:
                n -= 1
        
        for y in range(SCREEN_HEIGHT):
            
            # draw ceiling
            if y < ceilingEnd:
                screen[y * SCREEN_WIDTH + x] = CEILING_SHADE
            
            # draw floor
            elif y > floorEnd:
                
                screen[y * SCREEN_WIDTH + x] = FLOOR_SHADE
                
                # depending on how far away the floor is, we want the floor to be dithered
                #floorDitherChance = random.uniform(0.6, 1.5)
                #if (y / SCREEN_HEIGHT) > floorDitherChance:
                #    screen[y * SCREEN_WIDTH + x] = FLOOR_SHADE
                #else:
                #    screen[y * SCREEN_WIDTH + x] = CEILING_SHADE
            
            # draw wall            
            else:
                screen[y * SCREEN_WIDTH + x] = wallShade
                
    # refresh screen with new content
    coord_write("".join(screen), 0, 0)
    return

def get_input ():
    # polls the keyboard state so that the player can move
    global forward
    global backward
    global right
    global left
    
    forward = False
    backward = False
    left = False
    right = False
    
    if msvcrt.kbhit():
        key = msvcrt.getch().decode("utf-8").lower()
    
        if key == "w":
            forward = True
        elif key == "a":
            left = True
        elif key == "d":
            right = True
        elif key == "s":
            backward = True
        
        # quit via escape key
        elif key == "\x1b":
            sys.exit()
            
    return
    
def movement (dT):
    # uses the directional booleans to move the player
    
    global playerX
    global playerY
    global playerA
    
    # rotation
    if left:
        playerA -= PLAYER_TURN_SPEED * dT
    if right:
        playerA += PLAYER_TURN_SPEED * dT
    
    # project player forward in space to test for wall clipping
    
    newX = 0
    newY = 0
    
    if forward and backward:
        pass
    
    elif forward:
        
        newX = playerX + math.sin(playerA) * PLAYER_MOVE_SPEED * dT
        newY = playerY + math.cos(playerA) * PLAYER_MOVE_SPEED * dT
        
    elif backward:
        
        newX = playerX - math.sin(playerA) * PLAYER_MOVE_SPEED * dT
        newY = playerY - math.cos(playerA) * PLAYER_MOVE_SPEED * dT
    
    # perform the move if it leaves the player in a valid space
    if newX < MAP_WIDTH and newX >= 0 and MAP[int(playerY)][int(newX)] != "#":
        playerX = newX
            
    if newY < MAP_HEIGHT and newY >= 0 and MAP[int(newY)][int(playerX)] != "#":
        playerY = newY
        
    return

###########################
#          INIT           #
###########################

# set the terminal window size
os.system("mode " + str(SCREEN_WIDTH) + "," + str(SCREEN_HEIGHT))

# player position and rotation
playerX = 6
playerY = 2
playerA = 0

forward = False
backward = False
left = False
right = False

# used for FPS stabilization
currentTime = time.time()
oldTime = time.time()

###########################
#        GAME LOOP        #
###########################

while True:
    
    currentTime = time.time()
    deltaTime = currentTime - oldTime
    oldTime = currentTime

    get_input()
    movement(deltaTime)
    screen_draw()