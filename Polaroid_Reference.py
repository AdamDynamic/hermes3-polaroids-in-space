#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Contains reference and master data information used by the rest of the package
'''

########################################
# Constants used in the taking of photos
########################################

PHOTOS_NUMBER_OF_SHOTS = 8                  # Number of photos available in the cartridge

GPIO_PIN_SHUTTER = 31                       # GPIO pin used to trigger the Polaroid camera shutter
STABILITY_CHECKS_MAX_ITERATIONS = 10        # Maximum number of times stability is checked before the photo is taken anyway
                                            # Mitigates the risk that the camera never actuates because of a check loop

PHOTOS_INTERVAL_SECONDS = 120               # Time in seconds between each polaroid photo being taken
PHOTOS_MIN_ATMOSPHERIC_PRESSURE = 50        # The lowest altitude at which polaroid photos can be taken (in millibars)
PHOTOS_MAX_TIME_DELAY = 90*60               # Trigger the photos to take after 90 mins into the flight

MOVING_AVERAGE_EXP_CONSTANT = 0.95          # Percentage of t-1 moving average included in the average at t-0
MOVING_AVERAGE_RATIO_THRESHOLD = 0.05       # The percentage of the exponential moving average the current acceleration must
                                            # be in order to consider the camera "stable"

#########################################
# Constants used by the DevelopingTray object to control environment that film is ejected into once a photo is taken
#########################################
DEVELOP_TRAY_TEMP_MIN = 15                  # Temp in celsius below which the heater turns on
DEVELOP_TRAY_TEMP_MAX = 20                  # Temp in celsius above which the heater turns off
GPIO_PIN_DEVELOP_TRAY = 33                  # The RPi GPIO pin that turns the heater on and off

GPIO_PIN_EXTERNAL_THERMOMETER = 7           # The one-wire pin that supports the DS18B20 external temperature sensor
EXTERNAL_THERMOMETER_ID = '28-0115a4e9c0ff' # Device ID of the external thermometer used in the water bath


#########################################
# Constants used for atmospheric testing
#########################################
DEFAULT_SEA_LEVEL_PRESSURE = 1020


#########################################
# Misc config of the payload
#########################################

CONFIG_LOGGING_FOLDER = '/home/pi/polaroid/Logs' #'/home/adam/Dropbox/PyCharm%20Projects'


# /etc/init.d/polaroidstartup
#http://www.stuffaboutcode.com/2012/06/raspberry-pi-run-program-at-start-up.html
# Remember to put python /script/path &