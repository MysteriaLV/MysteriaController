import lupa
from lupa import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)


def rs485_read_coil(self, coil_id):
    print "rs485_read_coil {} {}".format(self.slaveId, coil_id)


class GameState(object):
    def __init__(self, modbus):
        self.modbus = modbus
        self.fsms = {}

        lua.globals()['REGISTER_STATES'] = self.register_states
        lua.globals()['REGISTER_MODBUS_SLAVE'] = self.register_slave_lua
        # lua.globals()['RS485_read_coil'] = rs485_read_coil
        lua.execute(open('lua/DemoArm.lua', 'r').read())

        lua.execute('alien_arm.complete()')
        print lua.eval('quest')

    @lupa.unpacks_lua_table_method
    def register_slave_lua(self, **slave):
        self.modbus.register_slave(slave['slave_id'], len(slave['events']), name=slave['name'])

    def register_states(self, name, fsm):
        self.fsms[name] = fsm
        # for event in fsm.events:
        #     self.fsms[name][event] = list(fsm.events[event].map)
