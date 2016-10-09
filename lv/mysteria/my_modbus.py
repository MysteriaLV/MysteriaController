#!/usr/bin/env python
import logging
import time
from collections import namedtuple

import minimalmodbus

ACTION_REGISTER = 1


class ModBus(object):
    def __init__(self, port='COM3'):
        self.port = port
        minimalmodbus.BAUDRATE = 57600
        # instrument.debug = True

        self.slaves = {}
        self.running = True

    def processor(self):
        while self.running:
            for slave in self.slaves.values():
                slave.last_data = slave.current_data
                try:
                    slave.current_data = slave.modbus.read_registers(0, slave.reg_count)
                except IOError:
                    logging.warn("Timeout for {}".format(slave.name))
                    slave.errors += 1

            time.sleep(1)

    def register_slave(self, lua_slave):
        slave_id = lua_slave['slave_id']
        slave = namedtuple(lua_slave['name'] or 'Slave {}'.format(slave_id),
                           ['name', 'modbus', 'reg_count', 'last_data', 'current_data', 'errors', 'fsm'])
        slave.name = lua_slave['name'] or 'Slave {}'.format(slave_id)
        slave.modbus = minimalmodbus.Instrument(self.port, slave_id)
        slave.reg_count = sum(
            1 for i in lua_slave['events'] if i is 'triggered_by_register') + 2  # ACTIONS and TOTAL_ERRORS
        slave.errors = 0
        slave.fsm = lua_slave
        slave.last_data = slave.current_data = []
        self.slaves[slave_id] = slave

    def send_action(self, slave_id, action_id):
        try:
            if not self.slaves[slave_id].current_data[ACTION_REGISTER] == 0:
                logging.warn(
                    "Sending action {} to {} while it apparently didn't finish processing previous action {}".format(
                        action_id, slave_id, self.slaves[slave_id].current_data[ACTION_REGISTER]))
        except IndexError:
            pass

        # self.slaves[slave_id].modbus.debug = True
        self.slaves[slave_id].modbus.write_register(ACTION_REGISTER, action_id, functioncode=6)
        # self.slaves[slave_id].modbus.debug = False

    @staticmethod
    def get_remote_errors(slave):
        return slave.current_data[slave.reg_count - 1]

    def fire_event(self, slave_id, event):
        return self.slaves[slave_id].fsm[event](self.slaves[slave_id].fsm)
