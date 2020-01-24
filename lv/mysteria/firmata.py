import random

from pyfirmata2 import Arduino, Pin, INPUT


class ZombieController(object):
    PIN_MIRROR = 2
    PIN_BUTTON = 0
    PIN_SPARKS = 13

    PIN_DATA_MIRROR_ON = 0
    PIN_DATA_MIRROR_OFF = 1

    def __init__(self):
        self.main_quest = None
        self.board = Arduino(Arduino.AUTODETECT)
        self.board.samplingOn(100)

        self.mirror_pin: Pin = self.board.digital[ZombieController.PIN_MIRROR]
        self.sparks_pin: Pin = self.board.digital[ZombieController.PIN_SPARKS]

        self.button_pin: Pin = self.board.analog[ZombieController.PIN_BUTTON]
        self.button_pin.mode = INPUT
        self.button_pin.register_callback(self.big_red_button_pressed)
        self.button_pin.enable_reporting()

    def reset(self):
        self.button_pin.enable_reporting()

    def mirror(self, turn_on=True):
        self.mirror_pin.write(0 if turn_on else 1)

    def sparkle(self):
        for i in range(200):
            self.sparks_pin.write(random.randint(0, 1))
            self.board.pass_time(0.02)

    def register_in_lua(self, main_quest):
        self.main_quest = main_quest
        return self

    def big_red_button_pressed(self, data):
        if data == 1:
            self.button_pin.disable_reporting()
            print(data)
