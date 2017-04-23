#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Contains information on controlling the camera and taking photos
'''

import logging
import time
import datetime

import RPi.GPIO as GPIO
from sense_hat import SenseHat

import Polaroid_Reference as r


class PolaroidCamera(object):
    '''
    Controls the actions of the polaroid camera
    '''

    def __init__(self):

        self.number_of_photos_taken = 0
        self.acceleration_exponential_ma = 1                    # Moving average of the acceleration
        self.current_acceleration = 0

        self.time_last_photo_taken = datetime.datetime.now()    # The time that the previous polaroid photo was taken

        self.sense = SenseHat()

    def take_photo(self):
        ''' Takes a photo with the polaroid camera

        :return: True/False on whether the photo was taken correctly
        '''

        i = 0                               # Used to control the maximum number of iterations before the photo is taken

        # Check if the minimum time between photos has elapsed, otherwise wait
        time_now = datetime.datetime.now()
        time_elapsed = (time_now - self.time_last_photo_taken).total_seconds()
        if time_elapsed < r.PHOTOS_INTERVAL_SECONDS:
            time.sleep(r.PHOTOS_INTERVAL_SECONDS - time_elapsed)
            logging.debug("Sleeping while minimum time between photos elapses")

        while i < r.STABILITY_CHECKS_MAX_ITERATIONS:
            if self.camera_is_stable():     # Take the photo if possible and then stop trying
                break
            else:
                time.sleep(5)
                i +=1
        # Once the camera is stable or the max iterations are exhausted, take the photo
        result = self.actuate_shutter()

        if result:
            self.number_of_photos_taken += 1
            self.time_last_photo_taken = datetime.datetime.now()
            return result
        else:
            raise IOError("Photo not taken, unable to actuate shutter")

    def get_acceleration(self):
        ''' Updates the acceleration metrics of the camera

        :return: True/False depending on whether process was successful
        '''

        try:
            x, y, z = self.sense.get_accelerometer_raw().values()
        except Exception, e:
            logging.error("Error attempting to get x,y,z values from accelerometer")
            logging.error("Error message: {}".format(e))
            raise e
        else:
            self.current_acceleration = ((x ** 2) + (y ** 2) + (z ** 2)) ** 0.5  # Determine the acceleration
            self.acceleration_exponential_ma = (self.current_acceleration * (1 - r.MOVING_AVERAGE_EXP_CONSTANT)) + (
                r.MOVING_AVERAGE_EXP_CONSTANT * self.acceleration_exponential_ma)
            logging.debug("Current acceleration: {}".format(self.current_acceleration))
            logging.debug("Current moving average acceleration: {}".format(self.acceleration_exponential_ma))

            return True

    def calibrate_acceleration(self):
        ''' Calibrates the moving average for the acceleration of the camera

        :return:
        '''

        for _ in range(0,100):
            try:
                self.get_acceleration()
            except Exception, e:
                logging.error("Unable to calibrate moving average acceleration")
                break   # Suppress error so that camera continues to take photos
            else:
                time.sleep(0.1)

    def camera_is_stable(self):
        ''' Uses the accelerometer to determine if the camera is sufficiently stable to take a photo

        :return: True/False depending on whether the stability of the camera is within the bounds defined
        '''

        i = 0
        while i < 100:
            # Make decision dynamic depending on how much was left of the expected flight
            # i.e. blurry photo better than none?

            try:
                self.get_acceleration()

            except Exception, e:                 # If the acceleration check raises an error, log it and try again
                logging.error("Error attempting to check stability of camera")
                logging.error("Error message: {}".format(e))
                i += 1

            else:
                acceleration_ratio = abs((self.current_acceleration - self.acceleration_exponential_ma)
                                         / self.acceleration_exponential_ma)
                # Return whether the current acceleration is sufficiently less than the exponential moving average
                if acceleration_ratio < r.MOVING_AVERAGE_RATIO_THRESHOLD:
                    return True     # If the camera is sufficiently stable, return True and break the cycle
                else:
                    i += 1          # Increment the counter
                    time.sleep(0.1)

        return False                # If the camera isn't stable after 100 iterations, return False

    def actuate_shutter(self):
        ''' Uses the GPIO pins to actuate the camera shutter

        :return: True/False on whether the shutter actuated correctly
        '''

        try:
            GPIO.output(r.GPIO_PIN_SHUTTER, True)
            time.sleep(1)
            GPIO.output(r.GPIO_PIN_SHUTTER, False)

        except Exception, e:
            logging.error("Error actuating shutter on pin {}".format(r.GPIO_PIN_SHUTTER))
            logging.error("Error message: {}".format(e))
            return False
        else:
            logging.info("### Camera shutter actuated ###")
            s = SenseHat()
            s.show_message("Camera actuated", scroll_speed=0.05)
            return True

    def test(self):
        ''' Series of tests designed to make sure the InOut methods will work correctly'''

        try:
            GPIO.output(r.GPIO_PIN_SHUTTER, False)  # Pin starts false, resetting it false checks pin can be referenced
        except Exception, e:
            logging.error("Unable to test GPIO pins in Polaroid.test() method")
            logging.error("Error message: {}".format(e))
            raise IOError("Unable to set GPIO pin number {}".format(r.GPIO_PIN_SHUTTER))

        try:
            self.get_acceleration()
        except Exception, e:
            logging.error("Unable to test accelerometer in Polaroid.test() method")
            logging.error("Error message: {}".format(e))
            raise IOError("Unable to get acceleration {}".format(e))

        try:
            self.camera_is_stable()
        except Exception, e:
            logging.error("Unable to test camera stability in Polaroid.test() method")
            logging.error("Error message: {}".format(e))
            raise IOError("Unable to test stability of the camera: {}".format(e))

        return True


class PiCamera(object):
    ''' Controls the onboard Pi camera module'''

    def __init__(self):

        self.save_file_location = None      # The file location of the most recently taken photo
        self.number_of_photos_taken = 0     # The number of photos taken by the camera

    def take_photo(self):
        ''' Takes a photo from the Pi camera'''

        pass

    def download(self):
        ''' Downloads the captured photo'''

        pass
