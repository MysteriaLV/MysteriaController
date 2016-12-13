#!/usr/bin/env python
import logging
from collections import namedtuple

import time
from pymodbus.client.sync import ModbusSerialClient, ModbusUdpClient
from pymodbus.exceptions import ConnectionException

ACTION_REGISTER = 0

pymodbus_logger = logging.getLogger('pymodbus.transaction')
pymodbus_logger.setLevel(logging.INFO)


class ModBus(object):
    def __init__(self, port='COM3'):
        self.port = port
        # minimalmodbus.BAUDRATE = 57600

        self.serialModbus = ModbusSerialClient('rtu', timeout=0.2, port=port, baudrate=57600)
        self.udpModbus = ModbusUdpClient('localhost', port=502)
        # https://github.com/andresarmento/modbus-esp8266/  TCP

        self.slaves = {}
        self.running = True

    def processor(self):
        while self.running:
            for slave in self.slaves.values():
                slave.last_data = slave.current_data

                try:
                    slave.current_data = self.serialModbus.read_holding_registers(0, slave.reg_count,
                                                                                  unit=slave.slave_id)
                except ConnectionException:
                    slave.current_data = None

                if slave.current_data:
                    if slave.last_data:
                        for i in slave.fsm['events'].values():
                            if i.config.triggered_by_register:
                                if slave.current_data.getRegister(i.config.triggered_by_register) and \
                                        not slave.last_data.getRegister(i.config.triggered_by_register):
                                    # We got a value change to TRUE on a register we monitor
                                    slave.fsm['on_' + i.config.name](
                                        slave.current_data.getRegister(i.config.triggered_by_register))
                else:
                    logging.warn("Timeout for {}".format(slave.name))
                    slave.errors += 1

            # TODO maybe remove for faster reactions
            time.sleep(1)

    def register_slave(self, lua_slave):
        slave_id = lua_slave['slave_id']
        slave = namedtuple(lua_slave['name'] or 'Slave {}'.format(slave_id),
                           ['name', 'slave_id', 'reg_count', 'last_data', 'current_data', 'errors', 'fsm'])
        slave.name = lua_slave['name'] or 'Slave {}'.format(slave_id)
        slave.slave_id = slave_id
        slave.reg_count = sum(
            1 for i in lua_slave['events'].values() if i.config.triggered_by_register) + 2  # ACTIONS and TOTAL_ERRORS
        slave.errors = 0
        slave.fsm = lua_slave
        slave.last_data = slave.current_data = None
        self.slaves[slave_id] = slave

    def send_action(self, slave_id, action_id):
        slave = self.slaves[slave_id]
        try:
            if not slave.current_data.getRegister(ACTION_REGISTER) == 0:
                logging.warn(
                    "Sending action {} to {} while it apparently didn't finish processing previous action {}".format(
                        action_id, slave_id, slave.current_data.getRegister(ACTION_REGISTER)))
        except AttributeError:
            pass

        try:
            self.serialModbus.write_register(ACTION_REGISTER, action_id, unit=slave.slave_id)
        except ConnectionException:
            # TODO add to retry queue?
            logging.error("Cannot send {} to {}".format(action_id, slave.name))
            slave.errors += 1

    @staticmethod
    def get_remote_errors(slave):
        if slave.current_data:
            return slave.current_data.getRegister(slave.reg_count - 1)

    def fire_event(self, slave_id, event):
        return self.slaves[slave_id].fsm[event](self.slaves[slave_id].fsm)
