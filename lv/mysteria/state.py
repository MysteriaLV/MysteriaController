from lupa import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)


def rs485_read_coil(self, coil_id):
    print "rs485_read_coil {} {}".format(self.slaveId, coil_id)


class GameState(object):
    def __init__(self):
        self.fsms = {}

        lua.globals()['REGISTER_STATES'] = self.register_states
        # lua.globals()['RS485_read_coil'] = rs485_read_coil
        lua.execute(open('Aliens.lua', 'r').read())

        # lua.execute('alarmLights:isButtonPressed()')
        # print lua.eval('quest')

    def register_states(self, name, fsm):
        self.fsms[name] = {}
        for event in fsm.events:
            self.fsms[name][event] = list(fsm.events[event].map)
