#!/usr/bin/python
# -*- coding: utf-8 -*-

''' Controls the screen of the SenseHAT
'''

import logging
import time
import random
import datetime

from sense_hat import SenseHat

import Polaroid_Reference as r

class Payload(object):
    ''' Controls the payload capsule '''

    def __init__(self):

        self.current_pressure = 0
        self.sense = SenseHat()
        self.launch_time = datetime.datetime.now()
        self.flight_duration = 0
        self.sea_level_pressure = 0

    def get_pressure(self):

        self.sense.clear()

        try:
            self.current_pressure = self.sense.get_pressure()
        except Exception, e:
            logging.error("Unable to determine atmospheric current_pressure")
            logging.error("Error message: {}".format(e))
            raise e
        else:
            logging.info("Current pressure: {}".format(self.current_pressure))

    def set_sea_level_pressure(self):
        ''' Calibrates the payload by setting the current_pressure at sea level '''

        try:
            self.get_pressure()
        except:
            logging.error("Unable to determine sea_level atmospheric current_pressure")
            self.sea_level_pressure = r.DEFAULT_SEA_LEVEL_PRESSURE
        else:
            logging.info("Sealevel pressure set as {}".format(r.DEFAULT_SEA_LEVEL_PRESSURE))
            self.sea_level_pressure = r.DEFAULT_SEA_LEVEL_PRESSURE # (self.current_pressure * 1.0)

    def get_flight_time(self):
        ''' Measures the flight time of the payload in seconds'''
        time_now = datetime.datetime.now()
        time_elapsed = (time_now - self.launch_time).total_seconds()
        self.flight_duration = time_elapsed

    def test(self):
        ''' Runs test diagnostics on the payload object'''
        pass

class Screen(object):
    ''' Controls the screen of the Sense HAT
    '''

    def __init__(self):

        self.previous_state = []    # A list of the pixels on-screen used to revert to previous image
        self.current_state = []     # The current array of pixels on the screen
        self.sense = SenseHat()

    def _fade_in_logo(self, fade_in_time = 1.0, number_of_fade_steps = 25, max_brightness = 255):
        '''
        Fades in the e3 logo

        fade_in_time = duration of fade-in in seconds

        '''

        for i in range(number_of_fade_steps):
            brightness=(max_brightness/number_of_fade_steps)*i
            w = [0,0,0]
            b = [brightness,brightness,brightness]

            e3_logo = [
                    w,w,b,b,b,b,w,w,
                    w,b,w,w,w,b,b,w,
                    b,w,b,b,b,w,b,b,
                    b,w,w,w,w,w,b,b,
                    b,w,b,b,b,b,b,b,
                    b,b,w,w,w,w,b,b,
                    w,b,b,b,b,b,b,b,
                    w,w,b,b,b,b,b,b,
                    ]

            self.sense.set_pixels(e3_logo)
            time.sleep(fade_in_time / number_of_fade_steps)

    def _fade_out_logo(self, fade_out_time = 1.0, number_of_fade_steps = 25,initial_brightness=255):
        '''
        Fades in the e3 logo

        fade_in_time = duration of fade-in in seconds

        '''

        for i in range(number_of_fade_steps,0,-1):
            brightness=int((initial_brightness/number_of_fade_steps)*i)
            w = [0,0,0]
            b = [brightness,brightness,brightness]

            e3_logo = [
                    w,w,b,b,b,b,w,w,
                    w,b,w,w,w,b,b,w,
                    b,w,b,b,b,w,b,b,
                    b,w,w,w,w,w,b,b,
                    b,w,b,b,b,b,b,b,
                    b,b,w,w,w,w,b,b,
                    w,b,b,b,b,b,b,b,
                    w,w,b,b,b,b,b,b,
                    ]

            self.sense.set_pixels(e3_logo)
            time.sleep(fade_out_time / number_of_fade_steps)

    def _sweep_diagonal(self, dim_ratio=0.5):
        '''
        Sweeps diagnoally over the screen, dimming each pixel on the diagonal
        '''
        diagonal_lines = [
                    [[0, 0]],
                    [[0, 1], [1, 0]],
                    [[0, 2], [1, 1], [2, 0]],
                    [[0, 3], [1, 2], [2, 1], [3, 0]],
                    [[0, 4], [1, 3], [2, 2], [3, 1], [4, 0]],
                    [[0, 5], [1, 4], [2, 3], [3, 2], [4, 1], [5, 0]],
                    [[0, 6], [1, 5], [2, 4], [3, 3], [4, 2], [5, 1], [6, 0]],
                    [[0, 7], [1, 6], [2, 5], [3, 4], [4, 3], [5, 2], [6, 1], [7, 0]],
                    [[1, 7], [2, 6], [3, 5], [4, 4], [5, 3], [6, 2], [7, 1]],
                    [[2, 7], [3, 6], [4, 5], [5, 4], [6, 3], [7, 2]],
                    [[3, 7], [4, 6], [5, 5], [6, 4], [7, 3]],
                    [[4, 7], [5, 6], [6, 5], [7, 4]],
                    [[5, 7], [6, 6], [7, 5]],
                    [[6, 7], [7, 6]],
                    [[7, 7]]
                    ]

        for i, pixel_row in enumerate(diagonal_lines):

            # Convert the leading diagonal row
            for pixel in pixel_row:
                old_colour = self.sense.get_pixel(pixel[0],pixel[1])
                new_pixel_colour = [int(a*dim_ratio) for a in old_colour]
                self.sense.set_pixel(pixel[0], pixel[1], new_pixel_colour)

            # Convert the following diagonal row
            if i > 0:
                for pixel in diagonal_lines[i-1]:
                    old_colour = self.sense.get_pixel(pixel[0],pixel[1])
                    new_pixel_colour = [int(a/dim_ratio) for a in old_colour]
                    self.sense.set_pixel(pixel[0], pixel[1], new_pixel_colour)


            time.sleep(0.05)

    def _flare_display(self):

        # Dim the pixels in the logo
        for i in range(200,150,-1):
            brightness=i
            w = [0,0,0]
            b = [brightness,brightness,brightness]

            e3_logo = [
                w,w,b,b,b,b,w,w,
                w,b,w,w,w,b,b,w,
                b,w,b,b,b,w,b,b,
                b,w,w,w,w,w,b,b,
                b,w,b,b,b,b,b,b,
                b,b,w,w,w,w,b,b,
                w,b,b,b,b,b,b,b,
                w,w,b,b,b,b,b,b,
                ]
            self.sense.set_pixels(e3_logo)

        # Increase the brightness of pixels in the logo
        for i in range(150,255,1):
            brightness=i
            w = [0,0,0]
            b = [brightness,brightness,brightness]

            e3_logo = [
                w,w,b,b,b,b,w,w,
                w,b,w,w,w,b,b,w,
                b,w,b,b,b,w,b,b,
                b,w,w,w,w,w,b,b,
                b,w,b,b,b,b,b,b,
                b,b,w,w,w,w,b,b,
                w,b,b,b,b,b,b,b,
                w,w,b,b,b,b,b,b,
                ]
            self.sense.set_pixels(e3_logo)

    def _shimmer(self):

        for t in range(0,50):

            black_max = 255
            black_min = 200

            r1 = random.randint(black_min,black_max)
            r2 = random.randint(black_min,black_max)
            r3 = random.randint(black_min,black_max)
            r4 = random.randint(black_min,black_max)

            a = [r1,r1,r1]
            b = [r2,r2,r2]
            c = [r3,r3,r3]
            d = [r4,r4,r4]
            w = [0,0,0]

            e3_logo = [
                        w,w,a,b,c,d,w,w,
                        w,c,w,w,w,b,a,w,
                        d,w,b,a,b,w,c,b,
                        a,w,w,w,w,w,c,d,
                        b,w,c,b,b,d,a,b,
                        b,a,w,w,w,w,d,c,
                        w,b,b,c,d,a,c,b,
                        w,w,b,d,c,b,a,b,
                        ]

            self.sense.set_pixels(e3_logo)
            time.sleep(0.1)

    def display_splash(self):
        ''' Displays a splash screen on the Sense HAT display

        :return:
        '''

        self._fade_in_logo(fade_in_time=2, number_of_fade_steps = 50, max_brightness=200)
        self._sweep_diagonal(0.7)
        time.sleep(0.2)
        self._flare_display()
        self._shimmer()
        self._fade_out_logo(fade_out_time=2, number_of_fade_steps = 50, initial_brightness=255)
        self.sense.clear()

    def save_current_screen(self):
        ''' Saves the current screen to memory so that it can be restored later

        :return:
        '''

        screen_pixels = []
        for y in range(0,8):
            for x in range(0,8):
                pixel = self.sense.get_pixel(x,y)
                screen_pixels.append(pixel)
        self.previous_state = screen_pixels

    def restore_previous_screen(self):
        ''' Writes the stored previous screen to the screen

        :return:
        '''

        if self.previous_state:
            self.sense.set_pixels(self.previous_state)

    def write(self, message, save_previous_screen=True):
        ''' Outputs a message to the screen

        :return:
        '''

        if save_previous_screen:
            self.save_current_screen()

        self.sense.show_message(message, scroll_speed = 0.05)

        if save_previous_screen:
            self.restore_previous_screen()

    def set_pixel(self, x=0, y=0, colour={255,255,255}):

        self.sense.set_pixel(x,y,colour)



