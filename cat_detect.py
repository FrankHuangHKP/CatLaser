#from picamera import PiCamera
from subprocess import Popen, PIPE
import threading
from time import sleep
import os, fcntl
import cv2
import select
import shutil
from shutil import copyfile
import time

import RPi.GPIO as GPIO
import pigpio
import numpy as np
from random import uniform
from datetime import datetime

lastPhotoTime = time.time()
photoTime = 20

# ------------------  servo control start ------------------

laserPin = 21

# camera pitch angle, i.e., degree below horizontal
camera_pitch = -45

# setup for pan servo
panPin = 12
panCycle = [122, 26] #124 28
panAngle = [-90, 90]
panServo = [panPin, panAngle, panCycle]
   
# setup for tilt servo
tiltPin = 13
tiltCycle = [27, 69]
tiltAngle = [-90, 0]
tiltServo = [tiltPin, tiltAngle, tiltCycle]

GPIO.setmode(GPIO.BCM)
GPIO.setup(laserPin, GPIO.OUT)

pi_hw = pigpio.pi()
pi_hw.hardware_PWM(panPin, 50, 0) # 50Hz 0% dutycycle
pi_hw.hardware_PWM(tiltPin, 50, 0) # 50Hz 0% dutycycle

"""
Transform the image coordinates (range: 0-1, origin: top-left corner) to
the pan-tilt angles of the laser. The pitch angle of the camera is
considered.
"""
def screentoAngles(u, v):	
	u_c, v_c = u - 0.5, 0.5 - v
	u_dis = 0.828859
	v_dis = 1.10224
	u_a = np.degrees(np.arctan(u_c / u_dis))
	v_a = np.degrees(np.arctan(v_c / v_dis))
	return (u_a, v_a + camera_pitch)

"""
Set the duty cycles of the servos based on the desired coordinates
"""
def setServoPanTilt(u, v):
	angles = screentoAngles(u, v)
	panDutyCycle = np.interp(angles[0], panAngle, panCycle)
	tiltDutyCycle = np.interp(angles[1], tiltAngle, tiltCycle)
	pi_hw.hardware_PWM(panPin, 50, int(panDutyCycle * 1000))
	pi_hw.hardware_PWM(tiltPin, 50, int(tiltDutyCycle * 1000))

# ------------------  servo control end ------------------

# callback function for button press on GPIO 23
# used as a physical quit button
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
def GPIO23_callback(channel): 
    global code_run   # Set code_run with global
    print ("quit")    # quit
    code_run = False  # set flag to end the python routine
# attach callback functions to button press events
GPIO.add_event_detect(23, GPIO.FALLING, callback=GPIO23_callback, bouncetime=300)

#camera.capture('frame.jpg')
sleep(0.1)

#spawn darknet process
yolo_proc = Popen(["./darknet",
                   "detect",
                   "./cfg/yolov3-tiny.cfg",
                   "./yolov3-tiny.weights",
                   "-thresh","0.2"],
                   stdin = PIPE, stdout = PIPE)

fcntl.fcntl(yolo_proc.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

code_run = True

stdout_buf = ""
while code_run:
    try:
        select.select([yolo_proc.stdout], [], [])
        stdout = yolo_proc.stdout.read()
        stdout_buf += stdout
        if 'Enter Image Path' in stdout_buf:
            try:
               im = cv2.imread('predictions.png')
               # print(im.shape)
               cv2.imshow('yolov3-tiny',im)
               key = cv2.waitKey(5)  
            except Exception as e:
                print("Error:", e)
            # camera.capture('frame.jpg')
            
            img_list = os.listdir('img_buf')
            img_list.sort()
            copyfile('img_buf/' + img_list[-2], 'cur_frame.jpg')
            yolo_proc.stdin.write('cur_frame.jpg\n')

            stdout_buf = ""
        
        f = open("webapp/control_mode.txt", "r")
        mode = eval(f.read())
        u_auto, v_auto = 0, 0
        cat_detected = False
        
        if len(stdout.strip()) > 0:
            if "Box" in stdout:                
                cat_detected = True                    
                
                start_xy = stdout.find("(x,y)=(") + len("(x,y)=(")
                end_xy = stdout.find(") with")
                coord = stdout[start_xy:end_xy].split(',')
                print("coord: " + str(coord))
                
                start_wh = stdout.find("(w,h)=(") + len("(w,h)=(")
                end_wh = stdout.find(")", start_wh)
                dimen = stdout[start_wh:end_wh].split(',')
                print("dimen: " + str(dimen))
                
                w, h = float(dimen[0]), float(dimen[1])
                u_auto = np.clip(float(coord[0]) + uniform(-w, w), 0, 1)
                v_auto = np.clip(float(coord[1]) + uniform(-h, h), 0.1, 0.9)     
        
        curTime = time.time()
        
        # Save image and update images on server
        if cat_detected == True and curTime - lastPhotoTime > photoTime:
            lastPhotoTime = curTime
            now = datetime.now()
            timestamp = now.strftime('%Y%m%d_%H%M%S')
            copyfile('cur_frame.jpg', 'saved/cat_' + timestamp + '.jpg')
            
            path = 'webapp/static/current_saved/'
            os.remove(path + 'cat1.jpg')
            for i in range(2, 5):
                os.rename(path + 'cat' + str(i) + '.jpg', path + 'cat' + str(i-1) + '.jpg')
            copyfile('cur_frame.jpg', path + 'cat4.jpg')                
        
        # configure servo and laser
        if mode.get('laser') == 'on':
            if mode.get('mode') == 'manual':
                u_manual = float(mode.get('x')) / 640.
                v_manual = float(mode.get('y')) / 480.
                setServoPanTilt(u_manual, v_manual)
                GPIO.output(laserPin, GPIO.HIGH)         
            else: # audo mode
                if cat_detected == True:
                    setServoPanTilt(u_auto, v_auto)
                    GPIO.output(laserPin, GPIO.HIGH)
                else: # no cat detected
                    GPIO.output(laserPin, GPIO.LOW)
        else: # laser off
            GPIO.output(laserPin, GPIO.LOW)
            
    except KeyboardInterrupt:
        pi_hw.hardware_PWM(panPin, 0, 0)
        pi_hw.hardware_PWM(tiltPin, 0, 0)
        pi_hw.stop()
        GPIO.cleanup()

pi_hw.hardware_PWM(panPin, 0, 0)
pi_hw.hardware_PWM(tiltPin, 0, 0)
pi_hw.stop()
GPIO.cleanup()
