#!/usr/bin/env python
import logging
from collections import namedtuple

import minimalmodbus

ACTION_REGISTER = 1


class ModBus(object):
    def __init__(self, port='COM3'):
        self.port = port
        minimalmodbus.BAUDRATE = 57600
        # instrument.debug = True

        self.slaves = {}

    def processor(self):
        for slave in self.slaves.values():
            slave.last_data = slave.current_data
            try:
                slave.current_data = slave.modbus.read_registers(0, slave.reg_count)
            except IOError:
                logging.warn("Timeout for {}".format(slave.modbus.address))
                slave.errors = + 1

    def register_slave(self, slave_id, reg_count):
        slave = namedtuple('Slave {}'.format(slave_id), ['modbus', 'reg_count', 'last_data', 'current_data', 'errors'])
        slave.modbus = minimalmodbus.Instrument(self.port, slave_id)
        slave.reg_count = reg_count
        slave.errors = 0
        slave.last_data = slave.current_data = []
        self.slaves[slave_id] = slave

    def register_event(self, slave_id, register_id, fn_callback):
        pass

    def send_action(self, slave_id, action_id):
        if not self.slaves[slave_id].current_data[ACTION_REGISTER] == 0:
            logging.warn(
                "Sending action {} to {} while it apparently didn't finish processing previous action {}".format(
                    action_id, slave_id, self.slaves[slave_id].current_data[ACTION_REGISTER]))

        self.slaves[slave_id].modbus.write_register(ACTION_REGISTER, action_id, functioncode=6)
