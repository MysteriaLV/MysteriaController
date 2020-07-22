import random

from pyfirmata2 import Arduino, Pin, INPUT
import logging


class ZombieController(object):
    PIN_MIRROR = 2
    PIN_BUTTON = 0
    PIN_SPARKS = 13

    PIN_DATA_MIRROR_ON = 0
    PIN_DATA_MIRROR_OFF = 1

    def __init__(self):
        self.main_quest = None
        # noinspection PyBroadException
        try:
            self.board = Arduino('COM11')
            self.board.samplingOn(50)

            self.mirror_pin: Pin = self.board.digital[ZombieController.PIN_MIRROR]
            self.sparks_pin: Pin = self.board.digital[ZombieController.PIN_SPARKS]

            self.button_pin: Pin = self.board.analog[ZombieController.PIN_BUTTON]
            self.button_pin.mode = INPUT
            self.button_pin.register_callback(self.big_red_button_pressed)
            self.button_pin.enable_reporting()
            self.board_missing = False
        except Exception:
            logging.error("Arduino in ZombieBox is not responding!!!")
            self.board_missing = True

    def reset(self):
        if self.board_missing:
            return

        self.button_pin.enable_reporting()

    def mirror(self, turn_on=True):
        if self.board_missing:
            return

        self.mirror_pin.write(0 if turn_on else 1)

    def blink(self):
        if self.board_missing:
            return

        self.sparks_pin.write(1)
        self.board.pass_time(0.05)
        self.sparks_pin.write(0)

    def sparkle(self):
        if self.board_missing:
            return

        for i in range(20):
            self.sparks_pin.write(random.randint(0, 1))
            self.board.pass_time(0.02)
        self.sparks_pin.write(0)

    def register_in_lua(self, main_quest):
        self.main_quest = main_quest
        return self

    def big_red_button_pressed(self, data):
        if data > 0.02:
            print(f"Activated on {data}")
            # self.button_pin.disable_reporting()
            if self.main_quest:
                self.main_quest['on_zombie_activated'](self.main_quest)


if __name__ == "__main__":
    ZombieController()
    import time

    while True:
        time.sleep(1)
