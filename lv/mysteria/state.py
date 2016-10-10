import logging

from lupa import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)


class GameState(object):
    def __init__(self, modbus):
        self.modbus = modbus
        self.fsms = {}

        lua.globals()['REGISTER_STATES'] = self.register_fsm
        lua.globals()['REGISTER_MODBUS_SLAVE'] = self.register_slave_lua
        lua.globals()['MODBUS_ACTION'] = self.modbus.send_action
        lua.globals()['print'] = logging.getLogger('lua').info
        lua.execute(open('lua/DemoArm.lua', 'r').read())

        # lua.execute('alien_arm.complete()')
        # print lua.eval('quest')

    # @lupa.unpacks_lua_table_method
    def register_slave_lua(self, slave):
        self.modbus.register_slave(slave)

    def register_fsm(self, name, fsm):
        self.fsms[name] = fsm

    def fire_event(self, fsm_name, event):
        return self.fsms[fsm_name][event](self.fsms[fsm_name])
