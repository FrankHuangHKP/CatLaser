#
# Kunpeng Huang, kh537
# Xinyi Yang, xy98
# Project: PiCat User Interface
# 05/19/2021
#

# import time, os, pygame, and GPIO modules
import time
import os
import pygame
import RPi.GPIO as GPIO
from pygame.locals import *
from datetime import datetime

# set the environment variable to run on PiTFT
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

# for GPIO, use Broadcom SOC channel designation
GPIO.setmode(GPIO.BCM)

# callback function for button press on GPIO 27
# used as a physical quit button
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
def GPIO27_callback(channel): 
    global code_run   # Set code_run with global
    print ("quit")    # quit
    code_run = False  # set flag to end the python routine
# attach callback functions to button press events
GPIO.add_event_detect(27, GPIO.FALLING, callback=GPIO27_callback, bouncetime=300)

"""
round up a float number to 1 or -1, if its magnitude is smaller than 1
"""
def round_up(a):
    if a >= 0. and a < 1.:
        return 1.
    elif a < 0. and a > -1.:
        return -1.
    return a
    
"""
limit the minimum speed to 1 in each of the x and y coordinate
"""
def limit_speed(v):
    return [round_up(v[0]), round_up(v[1])]

"""
input:
    c1: center coordinate of ball 1
    c2: center coordinate of ball 2
    v1: velocity of ball 1
    v2: velocity of ball 2
return:
    the updated velocity of ball 1 and ball 2 based on 
    whether a collision occurs
reference for algorithm:
    Bruce Land, ECE 4760:
    https://people.ece.cornell.edu/land/courses/ece4760/labs/f2019/lab2_2019.html
    The implementation assumes a complete elastic collison between
    two balls with equal mass
"""
def update_speed(c1, c2, v1, v2):
    rx = c1[0] - c2[0]
    ry = c1[1] - c2[1]
    dis2 = rx ** 2 + ry ** 2   # squared distance between two balls
    n_v1 = v1
    n_v2 = v2
    global hitCounter          # Set hitCounter with global
    # if there is a recent collision and two balls are not overlapping
    if hitCounter > 0 and dis2 > (r1 + r2) ** 2:
        hitCounter -= 1        # decrement hit counter
    # if two balls overlap and there is no recent collision
    if dis2 <= (r1 + r2) ** 2 and hitCounter == 0: 
        hitCounter = 5         # set hitCounter to 5
        
        # compute the changes in velocity for the two balls in two axes
        vx = v1[0] - v2[0]
        vy = v1[1] - v2[1]
        dvx = -float(rx) ** 2 * vx / float(dis2)
        dvy = -float(ry) ** 2 * vy / float(dis2)
        # update the velocity
        n_v1x = v1[0] + dvx
        n_v1y = v1[1] + dvy
        n_v2x = v2[0] - dvx
        n_v2y = v2[1] - dvy
        
        # compute the total "kinetic energy" with the updated velocity
        total_n_e2 = n_v1x**2. + n_v1y**2. + n_v2x**2. + n_v2y**2.
        # scale the velocity component to conserve the total energy
        ratio = (total_e2 / total_n_e2) ** 0.5
        n_v1 = [n_v1x * ratio, n_v1y * ratio]
        n_v2 = [n_v2x * ratio, n_v2y * ratio]
        
    return limit_speed(n_v1), limit_speed(n_v2)

"""
convert a list of two float to two int
"""
def float2int(l):
    return [int(l[0]), int(l[1])]

# initialize all imported pygame modules
pygame.init()

size = width, height = 320, 240  # dimensions of PiTFT in pixels
speed1 = [2., 3.]                # initial speed of ball 1
speed2 = [-3., 2.]               # initial speed of ball 2
# The total initial "kinetic energy" of the two balls,
# assuming equal mass, which will be held constant after a collision
total_e2 = speed1[0]**2 + speed1[1]**2 + speed2[0]**2 + speed2[1]**2
black = 0, 0, 0                  # background color in rgb
grey = 192, 192, 192
hitCounter = 0                   # initialize hitCounter

white = 255,255,255
my_font = pygame.font.Font(None,24)

screen = pygame.display.set_mode(size) # initialize screen for display
pygame.mouse.set_visible(False)        # hide the mouse cursor

# load the two ball images from files as Surface
# get the rectangular areas of the two ball Surface
# get the radius of the balls

ball1 = pygame.image.load("image/ergou_90px.png")
ballrect1 = ball1.get_rect()
r1 = ballrect1.width / 2

ball2 = pygame.image.load("image/huahua_80px.png")
ballrect2 = ball2.get_rect()
r2 = ballrect2.width / 2
# move the second ball to top right corner
ballrect2 = ballrect2.move([240, 0])

logo_img = pygame.image.load("image/PiCat_logo.png")
logo = logo_img.get_rect().move([220, 0])
# record the start time
start_time = time.time()

total_time = 20             # maximum run time in seconds
fps = 30                    # variable for frame rate
clock = pygame.time.Clock() # create an object to help track time
code_run = True             # whether the main while loop should run

state = 0 #main page

#birthday
birth_img = pygame.image.load("image/birthday_icon.png")
birth = birth_img.get_rect().move([180, 30])

hospital_img = pygame.image.load("image/hospital_icon.png")
hospital = hospital_img.get_rect().move([180, 70])

insurance_img = pygame.image.load("image/insurance_icon.png")
insurance = insurance_img.get_rect().move([180, 110])

favorite_img = pygame.image.load("image/favorite_icon.png")
favorite = favorite_img.get_rect().move([180, 150])

name_font = pygame.font.Font(None,28)

back_button = "Back"
back_pos = (160,225)

#state1 ergou
ergou_img = pygame.image.load("image/ergou_160px.png")
ergou = ergou_img.get_rect().move([10, 30])
name1 = "Ergou"
name1_pos = (90,210)
male_img = pygame.image.load("image/male_icon.png")
male = male_img.get_rect().move([20, 190])
state1_buttons = {'02/29/2016':(0,45),'05/28':(0, 85), 'Update 03/31':(0, 125)}
favorite_list = {'Chicken':(0, 165), 'Salmon':(0,185), 'Huahua':(0, 205)}

#state2 huahua
huahua_img = pygame.image.load("image/huahua_160px.png")
huahua = huahua_img.get_rect().move([10, 30])
name2 = "Huahua"
female_img = pygame.image.load("image/female_icon.png")
female = female_img.get_rect().move([20, 190])
state2_buttons = {'05/11/2016':(0,45),'05/28':(0, 85), 'Update 06/17':(0, 125)}
favorite2_list = {'Beef':(0, 165), 'Salmon':(0,185), 'Ergou':(0, 205)}

time_pos = (80, 10)
time_font = pygame.font.Font(None,26)

# while code_run is set to true
while code_run:
    
    screen.fill(black)  # fill the screen surface with black
    
    # update ball velocity based on collision detection
    speed1, speed2 = update_speed(\
        ballrect1.center, ballrect2.center, speed1, speed2)
    
    """
    for the two balls:
        if the left or right edge of Rect hits the screen boundary
            reverse speed in x
        if the top or bottom edge of Rect hits the screen boundary
            reverse speed in y
    """
    if state == 0 :
        if ballrect1.left < 0 or ballrect1.right > width:
            speed1[0] = -speed1[0]
        if ballrect1.top < 0 or ballrect1.bottom > height:
            speed1[1] = -speed1[1]
    
        if ballrect2.left < 0 or ballrect2.right > width:
            speed2[0] = -speed2[0]
        if ballrect2.top < 0 or ballrect2.bottom > height:
            speed2[1] = -speed2[1]
    
        # move the Rect for the balls with specified displacements    
        ballrect1 = ballrect1.move(float2int(speed1))
        ballrect2 = ballrect2.move(float2int(speed2))
    
        for event in pygame.event.get():
            if (event.type is MOUSEBUTTONDOWN):
                pos = pygame.mouse.get_pos()
                if ballrect1.collidepoint(pos):
                    print ("ergou")
                    state = 1
                elif ballrect2.collidepoint(pos):
                    print ("huahua")
                    state = 2
            # if detect the mouse button up and the mouse positio is correct
            # then quit the program
            elif (event.type is MOUSEBUTTONUP):
                pos = pygame.mouse.get_pos()
                x,y = pos
                    
        # draw the two balls onto the screen at the coordinates of the ball Rect
        screen.blits([(ball1, ballrect1), (ball2, ballrect2), (logo_img, logo)])
    
        clock.tick(fps)        # update the clock to ensure the fps
    
    elif state == 1:
        # draw the two balls onto the screen at the coordinates of the ball Rect
        screen.blits([(ergou_img, ergou),(birth_img, birth),(hospital_img, hospital),
        (insurance_img, insurance),(favorite_img, favorite),(male_img, male)])
        
        for my_text, text_pos in state1_buttons.items():
            text_surface = my_font.render(my_text, True, white)
            rect = text_surface.get_rect(center = text_pos)
            rect.left = 220
            screen.blit(text_surface, rect)
            
        for my_text, text_pos in favorite_list.items():
            text_surface = my_font.render(my_text, True, white)
            rect = text_surface.get_rect(center = text_pos)
            rect.left = 220
            screen.blit(text_surface, rect)
    
        name_surface =  name_font.render(name1, True, white)
        name_rect = name_surface.get_rect(center = name1_pos)
        screen.blit(name_surface, name_rect)

        back_surface =  name_font.render(back_button, True, grey)
        back_rect = back_surface.get_rect(center = back_pos)
        screen.blit(back_surface, back_rect)
        
        
        for event in pygame.event.get():
            if (event.type is MOUSEBUTTONUP):
                pos = pygame.mouse.get_pos()
                x,y = pos
                if back_rect.collidepoint(pos):
                    state = 0;
                    
    elif state == 2:
        # draw the two balls onto the screen at the coordinates of the ball Rect
        screen.blits([(huahua_img, huahua),(birth_img, birth),(hospital_img, hospital),
        (insurance_img, insurance),(favorite_img, favorite),(female_img, female)])
        
        for my_text, text_pos in state2_buttons.items():
            text_surface = my_font.render(my_text, True, white)
            rect = text_surface.get_rect(center = text_pos)
            rect.left = 220
            screen.blit(text_surface, rect)
            
        for my_text, text_pos in favorite2_list.items():
            text_surface = my_font.render(my_text, True, white)
            rect = text_surface.get_rect(center = text_pos)
            rect.left = 220
            screen.blit(text_surface, rect)
    
        name_surface =  name_font.render(name2, True, white)
        name_rect = name_surface.get_rect(center = name1_pos)
        screen.blit(name_surface, name_rect)

        back_surface =  name_font.render(back_button, True, grey)
        back_rect = back_surface.get_rect(center = back_pos)
        screen.blit(back_surface, back_rect)
        
        
        for event in pygame.event.get():
            if (event.type is MOUSEBUTTONUP):
                pos = pygame.mouse.get_pos()
                x,y = pos
                if back_rect.collidepoint(pos):
                    state = 0;
    
    time_now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    time_surface =  time_font.render(time_now, True, grey)
    time_rect = time_surface.get_rect(center = time_pos)
    screen.blit(time_surface, time_rect)
    
    pygame.display.flip() # Update the display Surface to the screen
    
    clock.tick(fps)       # update the clock to ensure the fps
    # quit the script after a set number of seconds
    # if (time.time() - start_time > total_time):
        # code_run = False
    
# GPIO.cleanup() # clean up GPIO
