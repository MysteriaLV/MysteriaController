import logging
import random
import time

import dotmap
from pymodbus.register_read_message import ReadHoldingRegistersResponse

import my_modbus

logging.basicConfig(
    # level=logging.DEBUG,
    level=logging.INFO,
    format='[%(name)s] %(message)s',
)


def _ok(resp):
    return type(resp) is ReadHoldingRegistersResponse


SLAVE_COUNT = 6
SPLAY = True
# SPLAY = False


def BasicConnectivity():
    slaves = []
    modbus = my_modbus.ModBus(port='COM6')

    for slave_id in range(1, SLAVE_COUNT + 1):
        slaves.append(dotmap.DotMap(slave_id=slave_id, reg_count=1, is_ok=True, errors=0))

    last_time = time.time()

    while True:
        for slave in slaves:
            if SPLAY: time.sleep(random.random() / 10)
            res = modbus.read_registers(slave)
            if not _ok(res):
                slave.is_ok = False
                slave.errors += 1
            else:
                slave.is_ok = True

        logging.info("[{:5.5}] ".format(time.time() - last_time) +
                     "[alive {:2}] ".format(sum([1 for slave in slaves if slave.is_ok])) +
                     str(["S{} {} {!r:5}".format(slave.slave_id, slave.is_ok, slave.errors) for slave in slaves]))

        last_time = time.time()

        # if SPLAY: time.sleep(0.1)
        # for slave in slaves:
        #     modbus.write_action_register(1, slave)
        #
        # if SPLAY: time.sleep(0.1)
        # for slave in slaves:
        #     modbus.write_action_register(2, slave)


BasicConnectivity()
