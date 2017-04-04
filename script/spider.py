#!/usr/bin/env python
#-*- coding: utf-8 -*-

import thread

import eyelib
# Eyelib can be managed by following global variables:
#    blinking : If True start a blink animation (1 cycle)
#    blinkspd : Speed of blinking
#    eye : Eye image
#    lid : Lid base image

import dewarp
# Last dewarped frame can be accessed by using global variable "panorama"
# A copy should be used to access data in order to avoid in-between garbage

# Main program
if __name__ == '__main__':
    thread.start_new_thread(Eye, ()) # Eye thread
    thread.start_new_thread(UnWarp, ()) # Unwarping thread
    while True: # Loop forever
        pass
