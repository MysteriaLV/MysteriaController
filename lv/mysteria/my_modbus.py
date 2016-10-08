#!/usr/bin/env python
import time

import minimalmodbus

minimalmodbus.BAUDRATE = 57600
# minimalmodbus.TIMEOUT = 0.5
instrument = minimalmodbus.Instrument('COM3', 1)  # port name, slave address (in decimal)
# instrument.debug = True

a = int(time.time())
count = 0
while True:
    if a < int(time.time()):
        print count
        count = 0
        a = int(time.time())

    count += 1

    try:
        button1 = instrument.read_registers(0, 4)
    except IOError as e:
        print e
        # print button1

        # instrument.write_register(3, button1, functioncode=6)
