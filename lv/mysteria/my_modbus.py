#!/usr/bin/env python
import logging
import struct
import time
from collections import namedtuple

import schedule
from pymodbus.client.sync import ModbusSerialClient, ModbusTcpClient
from pymodbus.constants import Defaults
from pymodbus.exceptions import ConnectionException, ModbusIOException
from pymodbus.pdu import ExceptionResponse

ACTION_REGISTER = 0

pymodbus_logger = logging.getLogger('pymodbus')
pymodbus_logger.setLevel(logging.INFO)
logging.getLogger('schedule').setLevel(logging.WARNING)


class ModBus(object):
    def __init__(self, port='COM6'):
        self.port = port
        self.action_queue = []

        from pymodbus import __version__
        pymodbus_logger.info("Running version: {}".format(__version__))

        Defaults.Timeout = 0.1
        Defaults.Retries = 1

        self.serialModbus = ModbusSerialClient('rtu', timeout=Defaults.Timeout, port=port, baudrate=31250)

        self.slaves = {}
        self.running = True

    def read_registers(self, slave):
        # Carefully measured artificial pause to make sure everything is processed
        time.sleep(0.02)
        if type(slave.slave_id) is int:
            try:
                return self.serialModbus.read_holding_registers(0, slave.reg_count, unit=slave.slave_id)
            except (IndexError, struct.error) as e:
                logging.error(e)
                slave.errors += 1
                return None

        try:
            tcp_modbus = ModbusTcpClient(slave.slave_id)
            tcp_modbus.connect()
            return tcp_modbus.read_holding_registers(0, slave.reg_count)
        except (ConnectionException, IndexError):
            slave.errors += 1
            return None

    def write_action_register(self, value, slave):
        if type(slave.slave_id) is int:
            try:
                self.serialModbus.write_register(ACTION_REGISTER, value, unit=slave.slave_id)
            except (IndexError, struct.error) as e:
                logging.error(e)
                slave.errors += 1
        else:
            try:
                tcp_modbus = ModbusTcpClient(slave.slave_id)
                tcp_modbus.connect()
                tcp_modbus.write_register(ACTION_REGISTER, value)
            except ConnectionException as e:
                logging.exception(e)
                slave.errors += 1

    def processor(self):
        while self.running:
            schedule.run_pending()

            for slave in self.slaves.values():
                if slave.can_run:
                    self.read_and_react(slave)

            # Process actions if any
            attempted = set()
            for action in self.action_queue[:]:
                slave_id, action_id = action

                if slave_id in attempted:
                    continue  # One attempt per cycle

                attempted.add(slave_id)
                if self._send_action(slave_id, action_id):
                    self.action_queue.remove(action)

            # TODO maybe remove for faster reactions
            # time.sleep(5)

    def read_and_react(self, slave):
        try:
            slave.current_data = self.read_registers(slave)
            if type(slave.current_data) is ModbusIOException \
                    or type(slave.current_data) is ExceptionResponse \
                    or not slave.current_data:
                raise ConnectionException

            if slave.last_data:
                for i in slave.fsm['events'].values():
                    if i.config.triggered_by_register:
                        if slave.current_data.getRegister(i.config.triggered_by_register) and \
                                not slave.last_data.getRegister(i.config.triggered_by_register):
                            # We got a value change to TRUE on a register we monitor
                            event_result = slave.fsm[i.config.name](slave.fsm)
                            logging.info("External event {} - result {}".format(i.config.name, event_result))

            slave.last_data = slave.current_data

        except ConnectionException:
            # logging.debug("Timeout for {}".format(slave.name))
            slave.current_data = None
            slave.errors += 1

        # Disable until timer enables it
        if slave.poll_frequency:
            slave.can_run = False

    def register_slave(self, lua_slave):
        slave_id = lua_slave['slave_id']
        slave = namedtuple(lua_slave['name'] or 'Slave {}'.format(slave_id),
                           ['name', 'slave_id', 'reg_count', 'last_data', 'current_data', 'errors', 'fsm', 'poll_frequency', 'can_run'])
        slave.name = lua_slave['name'] or 'Slave {}'.format(slave_id)
        slave.slave_id = slave_id
        slave.poll_frequency = lua_slave['poll_frequency'] or 0
        slave.reg_count = sum(
            1 for i in lua_slave['events'].values() if i.config.triggered_by_register) + 2  # ACTIONS and TOTAL_ERRORS
        slave.errors = 0
        slave.fsm = lua_slave
        slave.last_data = slave.current_data = None

        def _enable_run(x):
            logging.info(x)
            x.can_run = True

        if slave.poll_frequency:
            schedule.every(int(slave.poll_frequency)).seconds.do(_enable_run, slave)
        else:
            slave.can_run = True
        self.slaves[slave_id] = slave

    def queue_action(self, slave_id, action_id):
        self.action_queue.append((slave_id, action_id))

    def _send_action(self, slave_id, action_id):
        slave = self.slaves[slave_id]
        try:
            if not slave.current_data.getRegister(ACTION_REGISTER) == 0:
                logging.warning(
                    "Sending action {} to {} while it apparently didn't finish processing previous action {}".format(
                        action_id, slave_id, slave.current_data.getRegister(ACTION_REGISTER)))
                return False
        except AttributeError:
            return False

        try:
            self.write_action_register(action_id, slave)
            return True
        except ConnectionException:
            logging.warning("Cannot send {} to {}".format(action_id, slave.name))
            slave.errors += 1

        return False

    @staticmethod
    def get_remote_errors(slave):
        if slave.current_data:
            return slave.current_data.getRegister(slave.reg_count - 1)

    def fire_event(self, slave_id, event):
        return self.slaves[slave_id].fsm[event](self.slaves[slave_id].fsm)
