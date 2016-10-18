import serial as serial

ser = serial.Serial(
    port='COM3',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0)

print("connected to: " + ser.portstr)
count = 1

while True:
    for line in ser.read():
        print(str(count) + str(': ') + str(line))
        count += 1
        ser.write(line)

ser.close()
