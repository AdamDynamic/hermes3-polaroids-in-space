#!/usr/bin/python
# -*- coding: utf-8 -*-

# from https://aykutakin.wordpress.com/2013/08/06/logging-to-console-and-file-in-python/

import logging
import os.path

def initialize_logger(output_dir, logging_level="DEBUG"):
    ''' Initiatlises logging that writes to disk and console when run from the command line

    :param output_dir: The directory that the *.log files are written to
    :param logging_level: The logging level that the user wants to capture messages for
    :return: Outputs to output.log and error_log.log
    '''
    logger = logging.getLogger()

    # ToDo: Check that the logging level selection actually works

    # Set the logging level depending on the user-passed value
    if logging_level == "INFO":
        logger.setLevel(logging.INFO)
    elif logging_level == "WARNING":
        logger.setLevel(logging.WARNING)
    elif logging_level == "ERROR":
        logger.setLevel(logging.ERROR)
    elif logging_level == "CRITICAL":
        logger.setLevel(logging.CRITICAL)
    else:
        logger.setLevel(logging.DEBUG)

    # create console handler and set level to info
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s ｜ %(levelname)s ｜ %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create error file handler and set level to error
    handler = logging.FileHandler(os.path.join(output_dir, "error_log.log"),"w", encoding=None, delay="true")
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s ｜ %(levelname)s ｜ %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create debug file handler and set level to debug
    handler = logging.FileHandler(os.path.join(output_dir, "output.log"),"w")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s ｜ %(levelname)s ｜ %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

