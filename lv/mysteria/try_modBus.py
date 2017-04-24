import time

import dotmap

import my_modbus


# logging.basicConfig(
#     level=logging.DEBUG,
#     format='(%(threadName)-10s) [%(name)s] %(message)s',
# )

def BasicConnectivity():
    modbus = my_modbus.ModBus(port='COM5')
    slave1 = dotmap.DotMap(slave_id=1, reg_count=1)
    slave2 = dotmap.DotMap(slave_id=2, reg_count=1)

    while True:
        print "Slave1 {} Slave2 {}".format(
            modbus.read_registers(slave1) is not None,
            modbus.read_registers(slave2) is not None
        )

        modbus.write_action_register(1, slave2)
        modbus.write_action_register(1, slave1)
        time.sleep(0.1)
        modbus.write_action_register(2, slave1)
        modbus.write_action_register(2, slave2)
        time.sleep(0.1)


BasicConnectivity()
