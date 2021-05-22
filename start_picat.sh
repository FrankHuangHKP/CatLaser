#!/bin/bash
#
# Kunpeng Huang, kh537
# Xinyi Yang, xy98
# Project: script to run PiCat
# 05/19/2021
#

sudo pigpiod
python3 rpi_camera_stream.py &
python3 webapp/app.py

# python cat_detect.py
# sudo python3 picat_gui.py
