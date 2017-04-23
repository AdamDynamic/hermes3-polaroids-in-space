#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Module to handle the environment for developing the film once the photo has been taken
'''

import logging
import os
import time
import subprocess

import RPi.GPIO as GPIO

import Polaroid_Reference as r

# Sets up the external thermometer to get the temperature of the developing bath
# From https://learn.adafruit.com/downloads/pdf/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing.pdf
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = base_dir + r.EXTERNAL_THERMOMETER_ID
device_file = device_folder + '/w1_slave'

class DevelopingTray(object):
    '''
    Object to control the environment into which the film is ejected after the photo has been taken
    '''

    def __init__(self):

        self.temperature = 0
        self.heater_currently_on = False
        self.heater_enabled = True          # Used to disable the heater once photos start to be taken

        # ToDo: Signal that the heater system is working correctly


    def _read_temp_raw(self):
        ''' Reads the temperature data from the internal *.txt file

        :return:
        '''
        try:
            catdata = subprocess.Popen(['cat', device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception, e:
            logging.error("Unable to open file {}".format(device_file))
            logging.error("Error: {}".format(e))
            return False
        else:
            out, err = catdata.communicate()
            out_decode = out.decode('utf-8')
            lines = out_decode.split('\n')
            return lines

    def get_temperature(self):
        ''' Determines the temperature of the environment using the waterproof temperature sensor

        :return: True/False on whether the process worked correctly
        '''

        i = 0
        # External temp sensor is a DS18B20
        lines = self._read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            i += 1                              # Increment the counter to prevent infinite loop
            if i >= 100:
                logging.error("Maximum number of attempts to read temperature exceeded, process aborted")
                break
            lines = self._read_temp_raw()

        equals_pos = lines[1].find('t=')

        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            temp_celsius = float(temp_string) / 1000.0

            self.temperature = temp_celsius
            logging.info("New temperature: {}".format(self.temperature))
            return True
        else:
            logging.error("Unable to determine temperature (can't find 't=' in line of output file")
            return False

    def heater(self, heater_on=False):
        ''' Controls the heating coil for the liquid in the developing tray

        :param heater_on: True/False for whether the heater is turned on or not
        :return:
        '''

        if heater_on:
            GPIO.output(r.GPIO_PIN_DEVELOP_TRAY, True)
        else:
            GPIO.output(r.GPIO_PIN_DEVELOP_TRAY, False)

    def check(self):
        ''' Tests the environment and determines whether the heater needs to be turned on or not

        :return:
        '''

        if self.get_temperature():

            if self.heater_enabled:

                if self.temperature < r.DEVELOP_TRAY_TEMP_MIN:
                    self.heater(heater_on=True)                 # If it's too cold, turn the heater on
                    self.heater_currently_on=True
                    logging.info("Updated heater state: {}".format(self.heater_currently_on))
                elif self.temperature > r.DEVELOP_TRAY_TEMP_MAX:
                    self.heater(heater_on=False)                # If it's too warm, turn the heater off
                    self.heater_currently_on=False
                    logging.info("Updated heater state: {}".format(self.heater_currently_on))
                else:
                    pass                                        # Temperature is currently within normal limit
            else:
                self.heater(heater_on=False)
                logging.debug("Heater disabled, DevelopingTray.check not performed")
        else:
            # ToDo: Error, temperature wasn't determined correctly
            self.heater(heater_on=False)
            logging.error("Unable to get temperature, heater turned to False")


    def test(self):
        ''' Runs diagnostic checks on the developing tray object

        :return:
        '''

        try:
            self._read_temp_raw()
        except Exception, e:
            logging.error("Unable to read file (test): {}".format(device_file))
            logging.error("Error: {}".format(e))
            raise IOError("Unable to read file (test): {}".format(device_file))

        try:
            self.get_temperature()
        except Exception, e:
            logging.error("Unable to get temperature using external sensor (test)")
            logging.error("Error: {}".format(e))
            raise IOError("Unable to get temperature using external sensor (test)")

        try:
            self.heater(heater_on=False)
        except Exception, e:
            logging.error("Unable to turn heater off (test)")
            logging.error("Error: {}".format(e))
            raise IOError("Unable to turn heater off (test)")

        return True