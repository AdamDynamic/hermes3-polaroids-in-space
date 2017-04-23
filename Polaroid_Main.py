#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Main script for #PolaroidsInSpace
'''

#import logging
import os
import time

import RPi.GPIO as GPIO

import Polaroid_Reference as r
from Polaroid_Camera import PolaroidCamera
from Polaroid_Develop import DevelopingTray
from Polaroid_Payload import Payload, Screen

from Utils.Polaroid_Logging import *
from Utils.Sensehat_Stick import SenseStick

# Set up the logging for the script
#logging.basicConfig(filename="Polaroid_Log.txt",
#                    level=logging.DEBUG,
#                    format='%(levelname)s: %(asctime)s %(message)s',
#                    datefmt='%m/%d/%Y %I:%M:%S')

initialize_logger(r.CONFIG_LOGGING_FOLDER)


def run_diagnostic_checks(screen=None,developing_tray=None,payload=None,camera=None):
    ''' Runs a series of dignostic tests on the payload to ensure that it's working correctly '''

    screen.write("Running start-up diagnostics...")
    number_of_errors = 0
    g = [0, 255, 0]
    r = [255, 0, 0]

    # Payload
    try:
        payload.test()
    except Exception, e:
        logging.info("Payload config test failed")
        logging.info("Error message: {}".format(e))
        screen.write("Payload failed: {}".format(e))
        number_of_errors +=1
        screen.set_pixel(0,0,r)
    else:
        logging.info("Payload config test passed")
        screen.write("Payload: passed")
        screen.set_pixel(0,0,g)

    time.sleep(1)

    # Camera
    try:
        camera.test()
    except Exception, e:
        logging.info("Camera config test failed")
        logging.info("Error message: {}".format(e))
        screen.write("Camera failed: {}".format(e))
        number_of_errors +=1
        screen.set_pixel(1,0,r)
    else:
        logging.info("Camera config test passed")
        screen.write("Camera: passed")
        screen.set_pixel(1,0,g)

    time.sleep(1)

    # Developing tray
    try:
        developing_tray.test()
    except Exception, e:
        logging.info("Developing tray config test failed")
        logging.info("Error message: {}".format(e))
        screen.write("Developing tray failed: {}".format(e))
        number_of_errors +=1
        screen.set_pixel(2,0,r)
    else:
        logging.info("Developing tray config test passed")
        screen.write("Developing tray passed")
        screen.set_pixel(2,0,g)

    time.sleep(1)

    screen.write("Start-up checks completed", save_previous_screen=False)
    # Set the corner pixel to save the state for the user
    if number_of_errors ==0:
        screen.set_pixel(0, 0, g)
    else:
        screen.set_pixel(0, 0, r)

    logging.info("Number of errors on run_diagnostic_checks: {}".format(number_of_errors))

    return number_of_errors==0

def take_photos_from_space(developing_tray=None,payload=None,camera=None):
    ''' Takes photos from space using the on-board Polaroid camera, continues until all available shots have been taken

    :return:
    '''

    while True:

        developing_tray.check()                                 # Check to see whether the tray should be heated
        payload.get_pressure()                                  # Check the altitude of the payload
        payload.get_flight_time()                               # Check how long the payload has been in flight

        logging.info("Payload pressure: {}".format(payload.current_pressure))
        logging.info("Payload flight time: {}".format(payload.flight_duration))

        # Check if the payload is high enough or the delay since launch has been long enough. If so, start to take photos
        if payload.current_pressure < r.PHOTOS_MIN_ATMOSPHERIC_PRESSURE or payload.flight_duration > r.PHOTOS_MAX_TIME_DELAY:

            camera.calibrate_acceleration()  # Set an initial moving average for the payload
            logging.info("Camera acceleration calibrated: {}".format(camera.acceleration_exponential_ma))

            logging.info("### Photo taking process commenced ###")
            logging.info("Payload current pressure: {}".format(payload.current_pressure))
            logging.info("Payload flight duration: {}".format(payload.flight_duration))

            developing_tray.heater_enabled = False              # Disable the heater once the photos start to prevent
            logging.info("Developing tray heater disabled")     # them being burned by the wire

            # Keep trying to take photos while there are photos available in the cartridge
            while camera.number_of_photos_taken < r.PHOTOS_NUMBER_OF_SHOTS:
                # Test to see whether photo should be taken and if so, take one
                camera.take_photo()
                logging.info("Polaroid photo taken: {}".format(camera.number_of_photos_taken))
                logging.info("Payload current acceleration: {}".format(camera.current_acceleration))
                logging.info("Payload average acceleration: {}".format(camera.acceleration_exponential_ma))
                logging.info("Payload current pressure: {}".format(payload.current_pressure))
                logging.info ("Payload flight duration: {}".format(payload.flight_duration))

            logging.info("All polaroids photo taken, process ended")
            break

        else:
            time.sleep(15)

### Main entry point ###

screen = Screen()
stick = SenseStick()
camera = PolaroidCamera()
developing_tray = DevelopingTray()
payload = Payload()


# Set up the GPIO pins on the Board
GPIO.setmode(GPIO.BOARD)        # Defines the naming convention for the GPIO pins
GPIO.setup(r.GPIO_PIN_SHUTTER, GPIO.OUT)
GPIO.setup(r.GPIO_PIN_DEVELOP_TRAY, GPIO.OUT)
GPIO.setup(r.GPIO_PIN_EXTERNAL_THERMOMETER, GPIO.OUT)

screen.display_splash()         # Opening screen for the SenseHat

run_diagnostic_checks(screen=screen, developing_tray=developing_tray,payload=payload,camera=camera)

# Start the joystick
shutdown_check = 0
for event in stick:                                 # ToDo: Introduce a delay to stop button presses in fast sequence

    if event.state == stick.STATE_PRESS:

        if shutdown_check ==1:                      # If the user has selected the shutdown command
            if event.key == stick.KEY_DOWN:        # ToDo: Should the shutdown sequence be more robust?
                screen.write("System shutting down...")
                logging.info("Shutdown command confirmed by user, system shutting down")
                os.system("sudo shutdown -h now")
            else:                                   # Reset the check for any other keypress
                screen.write("Cancelled", save_previous_screen=False)
                logging.info("Shutdown command cancelled by user")
                screen.restore_previous_screen()
                shutdown_check = 0

        else:
            if event.key == stick.KEY_ENTER:
                screen.write("Please confirm shutdown")
                logging.info("Shutdown command requested by user")
                shutdown_check =1                   # Set check to high state and display red warning screen
                screen.save_current_screen()
                red_array = [[255, 0, 0]] * 64
                screen.sense.set_pixels(red_array)
                time.sleep(1)

            elif event.key == stick.KEY_UP: # Start the camera
                screen.write("Camera started", save_previous_screen=False)
                logging.info("Camera sequence started by user")
                payload.set_sea_level_pressure()
                take_photos_from_space(developing_tray=developing_tray, payload=payload, camera=camera)
                break

            elif event.key == stick.KEY_DOWN:
                run_diagnostic_checks(screen=screen, developing_tray=developing_tray, payload=payload, camera=camera)

            elif event.key == stick.KEY_RIGHT:
                pass

            elif event.key == stick.KEY_LEFT:
                pass

# ToDo: ### April 2017 ToDo list ###
# ToDo: Integrate non-Polaroid camera into payload
# ToDo: Create test rig to rest process without using polaroid film



            # Check to see if the camera is at a sufficiently high altitude
# Set a minimum flight duration, after which the camera starts to take photos anyway
# (Mitigates the risk that the altitude sensor doesn't work
# (Would need to trigger the start of the mission clock)

# Run start-up diagnostics to indicate to user that the script is running correctly




# ToDo: Figure out how to actuate the camera shutter with a GPIO pin
# ToDo: Figure out how to determine the altitude of the camera
# ToDo: Figure out how to determine the acceleration of the camera in three dimensions
# Sense HAT ordered - need to learn how to integrate it

# ToDo: Figure out how to measure temperature
# ToDo: Figure out how to keep the film warm

# Bill of materials:

# MOSFET
# Nichrome wire
# Metal screws to hold wire
# Container to hold liquid
# Suitable liquid


# Signal that the script is running successfully with an LED

# Check whether the RPi is at a high enough altitude

# Once at a high enough altitude, start taking photos at intervals

# For each photo, check whether the camera is sufficiently still

# Stop when there are no more photos to take

# Test whether the environment is warm enough for the film to work correctly