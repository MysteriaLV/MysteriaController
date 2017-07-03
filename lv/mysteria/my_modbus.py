#!/usr/bin/env python
import logging
from collections import namedtuple

from pymodbus.client.sync import ModbusSerialClient, ModbusTcpClient
from pymodbus.exceptions import ConnectionException

ACTION_REGISTER = 0

pymodbus_logger = logging.getLogger('pymodbus')
pymodbus_logger.setLevel(logging.INFO)


class ModBus(object):
    def __init__(self, port='COM5'):
        self.port = port
        self.action_queue = []

        from pymodbus.constants import Defaults
        Defaults.Timeout = 0.5
        Defaults.Retries = 1

        self.serialModbus = ModbusSerialClient('rtu', timeout=Defaults.Timeout, port=port, baudrate=57600)

        self.slaves = {}
        self.running = True

    def read_registers(self, slave):
        if type(slave.slave_id) is int:
            return self.serialModbus.read_holding_registers(0, slave.reg_count, unit=slave.slave_id)

        try:
            tcpModbus = ModbusTcpClient(slave.slave_id)
            tcpModbus.connect()
            return tcpModbus.read_holding_registers(0, slave.reg_count)
        except ConnectionException:
            return None

    def write_action_register(self, value, slave):
        if type(slave.slave_id) is int:
            self.serialModbus.write_register(ACTION_REGISTER, value, unit=slave.slave_id)
        else:
            try:
                tcpModbus = ModbusTcpClient(slave.slave_id)
                tcpModbus.connect()
                tcpModbus.write_register(ACTION_REGISTER, value)
            except ConnectionException:
                pass

    def processor(self):
        while self.running:
            for slave in self.slaves.values():
                try:
                    slave.current_data = self.read_registers(slave)
                except ConnectionException:
                    slave.current_data = None

                if slave.current_data:
                    if slave.last_data:
                        for i in slave.fsm['events'].values():
                            if i.config.triggered_by_register:
                                if slave.current_data.getRegister(i.config.triggered_by_register) and \
                                        not slave.last_data.getRegister(i.config.triggered_by_register):
                                    # We got a value change to TRUE on a register we monitor
                                    logging.info("External event {} - result {}".format(
                                        i.config.name,
                                        slave.fsm[i.config.name](slave.fsm)))
                    slave.last_data = slave.current_data
                else:
                    logging.warn("Timeout for {}".format(slave.name))
                    slave.errors += 1

            # Process actions if any
            attempted = set()
            for action in self.action_queue[:]:
                slave_id, action_id = action

                if slave_id in attempted:
                    continue    # One attempt per cycle

                attempted.add(slave_id)
                if self._send_action(slave_id, action_id):
                    self.action_queue.remove(action)

            # TODO maybe remove for faster reactions
            # time.sleep(5)

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

    def queue_action(self, slave_id, action_id):
        self.action_queue.append((slave_id, action_id))

    def _send_action(self, slave_id, action_id):
        slave = self.slaves[slave_id]
        try:
            if not slave.current_data.getRegister(ACTION_REGISTER) == 0:
                logging.warn(
                    "Sending action {} to {} while it apparently didn't finish processing previous action {}".format(
                        action_id, slave_id, slave.current_data.getRegister(ACTION_REGISTER)))
                return False
        except AttributeError:
            return False

        try:
            self.write_action_register(action_id, slave)
            return True
        except ConnectionException:
            logging.warn("Cannot send {} to {}".format(action_id, slave.name))
            slave.errors += 1

        return False

    @staticmethod
    def get_remote_errors(slave):
        if slave.current_data:
            return slave.current_data.getRegister(slave.reg_count - 1)

    def fire_event(self, slave_id, event):
        return self.slaves[slave_id].fsm[event](self.slaves[slave_id].fsm)
