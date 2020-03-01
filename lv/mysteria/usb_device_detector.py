import time

import pywintypes
import win32api

from mysteria.state import GameState


class USBDetector(object):
    def __init__(self, game_state):
        self.game_state: GameState = game_state

    def processor(self):
        while True:
            try:
                usb_drive = win32api.GetVolumeInformation("D:\\")
                if usb_drive[0] == "MULTIBOOT":
                    print("Device present")
                time.sleep(3)
            except pywintypes.error:
                pass
