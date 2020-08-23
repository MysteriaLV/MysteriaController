import logging
import threading
import time

from lupa import LuaRuntime

from mysteria.firmata import ZombieController
from mysteria.media_players import Sampler, ZombieBox, PotPlayer
from mysteria.touchpanel import TouchPanel

LUA_SCENARIO = 'lua/Aliens.lua'
lua = LuaRuntime(unpack_returned_tuples=True)


class GameState(object):
    def __init__(self, modbus, touchpanel, usb_detector):
        self.touchpanel: TouchPanel = touchpanel
        self.modbus = modbus
        self.usb_detector = usb_detector
        self.sampler = Sampler()
        self.zombie_box = ZombieBox(self.sampler)
        self.zombie_controller = ZombieController()
        self.pot_player = PotPlayer()
        self.fsms = {}

        self.touchpanel.register_blinker(self.zombie_controller)

        lua.globals()['REGISTER_STATES'] = self.register_fsm
        lua.globals()['REGISTER_MODBUS_SLAVE'] = self.register_slave_lua
        lua.globals()['REGISTER_CODE_PANEL'] = self.touchpanel.register_code_panel_lua
        lua.globals()['REGISTER_SAMPLER'] = self.sampler.register_in_lua
        lua.globals()['REGISTER_VLC'] = self.zombie_box.register_in_lua
        lua.globals()['REGISTER_ZOMBIE_CONTROLLER'] = self.zombie_controller.register_in_lua
        lua.globals()['REGISTER_ZOMBIE_TRANSLATOR'] = self.usb_detector.register_in_lua
        lua.globals()['REGISTER_POTPLAYER'] = self.pot_player.register_in_lua
        lua.globals()['MODBUS_ACTION'] = self.modbus.queue_action
        lua.globals()['print'] = logging.getLogger('lua').info
        lua.execute(open(LUA_SCENARIO, 'r').read())

        t_ticker = threading.Thread(name='lua_ticker', target=GameState.processor)
        t_ticker.start()

    @classmethod
    def processor(cls):
        while True:
            time.sleep(1)
            lua.globals()['quest']['on_tick'](lua.globals()['quest'])

    def register_slave_lua(self, slave):
        self.modbus.register_slave(slave)

    def register_fsm(self, name, fsm):
        self.fsms[name] = fsm

    def fire_event(self, fsm_name, event):
        return self.fsms[fsm_name][event](self.fsms[fsm_name])

    @property
    def game_time(self):
        return time.strftime('%H:%M:%S', time.gmtime(self.fsms["main_quest"]['get_game_time']))
