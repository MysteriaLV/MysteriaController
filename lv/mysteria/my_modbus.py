#!/usr/bin/env python
import logging
import struct
import time
from collections import namedtuple

import schedule
from pymodbus.client.sync import ModbusSerialClient, ModbusTcpClient
from pymodbus.constants import Defaults
from pymodbus.exceptions import ConnectionException, ModbusException

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
        try:
            if type(slave.slave_id) is int:
                return None
                response = self.serialModbus.read_holding_registers(0, slave.reg_count, unit=slave.slave_id)
            else:
                logging.debug(f'++ Requesting data from {slave.slave_id}')
                tcp_modbus = ModbusTcpClient(slave.slave_id)
                tcp_modbus.connect()
                response = tcp_modbus.read_holding_registers(0, slave.reg_count)

            if issubclass(type(response), ModbusException):
                raise response

            logging.debug(f'++ Got data from {slave.slave_id}')
            return response

        except (IndexError, struct.error, ModbusException, ConnectionException) as e:
            logging.exception(e, exc_info=False)
            slave.errors += 1
            return None

    def write_action_register(self, value, slave):
        logging.debug(f'-- Sending action {value} to {slave.slave_id}')
        try:
            if type(slave.slave_id) is int:
                response = self.serialModbus.write_register(ACTION_REGISTER, value, unit=slave.slave_id)
            else:
                tcp_modbus = ModbusTcpClient(slave.slave_id)
                tcp_modbus.connect()
                response = tcp_modbus.write_register(ACTION_REGISTER, value)

            if issubclass(type(response), ModbusException):
                raise response

            logging.debug(f'-- Action ok from {slave.slave_id}')

            return True
        except (IndexError, struct.error, ModbusException, ConnectionException) as e:
            logging.exception(e, exc_info=False)
            slave.errors += 1
            return False

    def processor(self):
        while self.running:
            schedule.run_pending()

            # Process actions if any
            attempted = set()
            for action in self.action_queue[:]:
                slave_id, action_id = action

                if slave_id in attempted:
                    continue  # One attempt per cycle

                attempted.add(slave_id)
                if self._send_action(slave_id, action_id):
                    self.action_queue.remove(action)
                # else:
                # logging.debug(f"Failure to send action. Will requeue, actions in queue {len(self.action_queue)}")

            # Read values
            for slave in self.slaves.values():
                if slave.can_run:
                    self.read_and_react(slave)

            # TODO maybe remove for faster reactions
            # time.sleep(5)

    def read_and_react(self, slave):
        try:
            slave.current_data = self.read_registers(slave)
            if not slave.current_data:
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
            # logging.debug(f'Resetting run timer for {x}')
            x.can_run = True

        if slave.poll_frequency:
            schedule.every(int(slave.poll_frequency)).seconds.do(_enable_run, slave)
            slave.can_run = False
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

        # Mark this attempt as spent
        slave.can_run = False
        return self.write_action_register(action_id, slave)

    @staticmethod
    def get_remote_errors(slave):
        if slave.current_data:
            return slave.current_data.getRegister(slave.reg_count - 1)

    def fire_event(self, slave_id, event):
        return self.slaves[slave_id].fsm[event](self.slaves[slave_id].fsm)
