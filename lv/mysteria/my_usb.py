import usb


# x=78, y=160
# x=1973, y=1927

def main():
    device = usb.core.find(idVendor=0x0eef, idProduct=0x0001)
    # use the first/default configuration
    device.set_configuration()

    # first endpoint
    endpoint = device[0][(0, 0)][0]
    lastX, lastY = 0, 0
    # read a data packet
    data = None
    while True:
        try:
            data = device.read(endpoint.bEndpointAddress,
                               endpoint.wMaxPacketSize)
            x = data[1] * 128 + data[2]
            y = data[3] * 128 + data[4]
            print "x={0}, y={1}, keypress={2}, d {3}:{4}".format(x, y, data[0], lastX - x, lastY - y)
            lastX, lastY = x, y

        except usb.core.USBError as e:
            data = None
            if e.args == ('Operation timed out',):
                continue


if __name__ == '__main__':
    main()
