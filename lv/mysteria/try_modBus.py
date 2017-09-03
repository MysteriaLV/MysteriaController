import random
import time

import dotmap
import logging

from pymodbus.register_read_message import ReadHoldingRegistersResponse

import my_modbus


logging.basicConfig(
    # level=logging.DEBUG,
    level=logging.INFO,
    format='[%(name)s] %(message)s',
)

def _ok(resp):
    return type(resp) is ReadHoldingRegistersResponse

def BasicConnectivity():
    modbus = my_modbus.ModBus(port='COM6')
    slave1 = dotmap.DotMap(slave_id=1, reg_count=1)
    slave2 = dotmap.DotMap(slave_id=3, reg_count=1)
    slave3 = dotmap.DotMap(slave_id=4, reg_count=1)

    last_time = time.time()
    s1_errors = s2_errors = s3_errors = 0

    while True:
        s1 = modbus.read_registers(slave1) # is not None
        # s1 = None

        time.sleep(random.random()/10)
        s2 = modbus.read_registers(slave2) # is not None
        # s2 = None

        time.sleep(random.random()/10)
        s3 = modbus.read_registers(slave3)# is not None
        # s3 = None

        if not _ok(s1): s1_errors += 1
        if not _ok(s2): s2_errors += 1
        if not _ok(s3):
            s3_errors += 1

        logging.info("[{:5.5}] Slave1 {} {!r:5} Slave2 {} {!r:5} Slave3 {} {!r:5}".format(
            time.time() - last_time,
            s1_errors, _ok(s1), s2_errors, _ok(s2), s3_errors, _ok(s3)
        ))
        last_time = time.time()

        time.sleep(0.1)
        modbus.write_action_register(1, slave1)
        modbus.write_action_register(1, slave2)
        modbus.write_action_register(1, slave3)
        time.sleep(0.1)
        modbus.write_action_register(2, slave1)
        modbus.write_action_register(2, slave2)
        modbus.write_action_register(2, slave3)
        time.sleep(0.1)


BasicConnectivity()
