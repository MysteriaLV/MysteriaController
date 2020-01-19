import logging
from lupa import LuaRuntime

from mysteria.media_players import Sampler, ZombieBox

LUA_SCENARIO = 'lua/Aliens.lua'
lua = LuaRuntime(unpack_returned_tuples=True)


class GameState(object):
    def __init__(self, modbus, touchpanel):
        self.touchpanel = touchpanel
        self.modbus = modbus
        self.sampler = Sampler()
        self.zombie_box = ZombieBox()
        self.fsms = {}

        lua.globals()['REGISTER_STATES'] = self.register_fsm
        lua.globals()['REGISTER_MODBUS_SLAVE'] = self.register_slave_lua
        lua.globals()['REGISTER_CODE_PANEL'] = self.touchpanel.register_code_panel_lua
        lua.globals()['REGISTER_SAMPLER'] = self.sampler.register_in_lua
        lua.globals()['REGISTER_VLC'] = self.zombie_box.register_in_lua
        lua.globals()['MODBUS_ACTION'] = self.modbus.queue_action
        lua.globals()['print'] = logging.getLogger('lua').info
        lua.execute(open(LUA_SCENARIO, 'r').read())

    # @lupa.unpacks_lua_table_method
    def register_slave_lua(self, slave):
        self.modbus.register_slave(slave)

    def register_fsm(self, name, fsm):
        self.fsms[name] = fsm

    def fire_event(self, fsm_name, event):
        return self.fsms[fsm_name][event](self.fsms[fsm_name])
