import time

import dotmap

import my_modbus


# logging.basicConfig(
#     level=logging.DEBUG,
#     format='(%(threadName)-10s) [%(name)s] %(message)s',
# )

def BasicConnectivity():
    modbus = my_modbus.ModBus(port='COM19')
    slave1 = dotmap.DotMap(slave_id=1, reg_count=1)
    slave2 = dotmap.DotMap(slave_id=2, reg_count=1)
    slave3 = dotmap.DotMap(slave_id=3, reg_count=1)

    last_time = time.time()
    s1_errors = s2_errors = s3_errors = 0

    while True:
        # s1 = None
        s1 = modbus.read_registers(slave1) is not None
        # s2 = None # modbus.read_registers(slave2) is not None
        s2 = modbus.read_registers(slave2) is not None
        # s3 = None # modbus.read_registers(slave3) is not None
        s3 = modbus.read_registers(slave3) is not None

        if not s1: s1_errors += 1
        if not s2: s2_errors += 1
        if not s3: s3_errors += 1

        print "[{:5.5}] Slave1 {} {!r:5} Slave2 {} {!r:5} Slave3 {} {!r:5}".format(
            time.time() - last_time,
            s1_errors, s1, s2_errors, s2, s3_errors,s3,
            )
        last_time = time.time()

        modbus.write_action_register(1, slave1)
        modbus.write_action_register(1, slave2)
        modbus.write_action_register(1, slave3)
        # time.sleep(0.1)
        modbus.write_action_register(3, slave1)
        modbus.write_action_register(2, slave2)
        modbus.write_action_register(2, slave3)
        # time.sleep(0.1)


BasicConnectivity()
