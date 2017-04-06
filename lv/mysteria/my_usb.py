import logging
from Queue import Queue

import usb

pymodbus_logger = logging.getLogger('touchpanel')
pymodbus_logger.setLevel(logging.DEBUG)

RIGHT_TOP = (78, 160)
LEFT_BOTTOM = (1973, 1927)


class TouchPanel(object):
    def __init__(self):
        self.touches = Queue()
        self.running = True
        self.device = usb.core.find(idVendor=0x0eef, idProduct=0x0001)
        # use the first/default configuration
        self.device.set_configuration()

        # first endpoint
        self.endpoint = self.device[0][(0, 0)][0]

    def processor(self):
        if not self.device:
            return

        pressed = False
        while self.running:
            try:
                data = self.device.read(self.endpoint.bEndpointAddress, self.endpoint.wMaxPacketSize)
                if len(data) < 5:
                    continue  # Invalid or useless

                if pressed and data[1] == 129:
                    continue  # Holding

                if data[1] == 128:
                    pressed = False
                    continue

                x = data[1] * 128 + data[2]
                y = data[3] * 128 + data[4]

                logging.debug("x={0}, y={1}, keypress={2}".format(x, y, data[0]))
                self.touches.put((x, y))

            except usb.core.USBError as e:
                if e.args == ('Operation timed out',):
                    continue


if __name__ == '__main__':
    touchpanel = TouchPanel()
    touchpanel.processor()
