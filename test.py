#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pirc522 import RFID
import time
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
LED_GREEN = 36
LED_RED = 38
GPIO_MOTOR = 7

rc522 = RFID()

def turn_high (gpio) :
    GPIO.setup(gpio, GPIO.OUT)
    GPIO.output(gpio, GPIO.HIGH)

def turn_low (gpio) :
    GPIO.setup(gpio, GPIO.OUT)
    GPIO.output(gpio, GPIO.LOW)

def degree_to_duty (degree) :
    return 1/18 * degree + 2

def motor (gpio):
    turn_high(LED_GREEN)
    GPIO.setup(gpio, GPIO.OUT)
    pwm = GPIO.PWM(gpio, 50)
    pwm.start(degree_to_duty(0))
    pwm.ChangeDutyCycle(degree_to_duty(180))
    time.sleep(5)
    pwm.ChangeDutyCycle(degree_to_duty(2))
    time.sleep(1)
    pwm.stop()
    turn_low(LED_GREEN)


while True :
    rc522.wait_for_tag()
    (error, tag_type) = rc522.request()

    if not error :
        (error, uid) = rc522.anticoll()

        if uid == [67, 159, 44, 131, 115] :
            print('Bon')
            motor(GPIO_MOTOR)
        else:
            print('Mauvais')
            turn_high(LED_RED)
            time.sleep(1)
            turn_low(LED_RED)
