import random

from pymata_aio.constants import Constants
from pymata_aio.pymata3 import PyMata3


class ZombieController(object):
    PIN_MIRROR = 2
    PIN_BUTTON = 0
    PIN_SPARKS = 13

    PIN_DATA_MIRROR_ON = 0
    PIN_DATA_MIRROR_OFF = 1

    def __init__(self):
        self.main_quest = None
        self.board = PyMata3()

        self.board.set_pin_mode(self.PIN_BUTTON, Constants.ANALOG)
        self.board.set_pin_mode(self.PIN_MIRROR, Constants.OUTPUT)
        self.board.set_pin_mode(self.PIN_SPARKS, Constants.OUTPUT)

    def reset(self):
        self.board.set_analog_latch(self.PIN_BUTTON, Constants.LATCH_GT, 99, self.big_red_button_pressed)

    def mirror(self, turn_on=True):
        self.board.digital_write(self.PIN_MIRROR, 0 if turn_on else 1)

    def sparkle(self):
        for i in range(200):
            self.board.digital_write(self.PIN_SPARKS, random.randint(0, 1))
            self.board.sleep(0.02)

    def register_in_lua(self, main_quest):
        self.main_quest = main_quest
        return self

    def big_red_button_pressed(data):
        print(data)
