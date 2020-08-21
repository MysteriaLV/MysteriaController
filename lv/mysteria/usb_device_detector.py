import time

import pywintypes
import win32api

from mysteria.state import GameState


class USBDetector(object):
    def __init__(self):
        self.main_quest = None

    def register_in_lua(self, main_quest):
        self.main_quest = main_quest
        return self

    def processor(self):
        while True:
            try:
                usb_drive = win32api.GetVolumeInformation("D:\\")
                if usb_drive[0] == "ALIENVOICE":
                    # print("Device present")

                    if self.main_quest:
                        self.main_quest['on_zombie_translator'](self.main_quest)

                time.sleep(3)
            except pywintypes.error:
                pass
