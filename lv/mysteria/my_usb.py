import logging
from Queue import Queue

import usb


class TouchPanel(object):
    MIN = (75, 125)
    MAX = (1980, 1935)

    def __init__(self, rows=3, columns=2):
        self.x_interval = (TouchPanel.MAX[0] - TouchPanel.MIN[0]) / rows
        self.y_interval = (TouchPanel.MAX[1] - TouchPanel.MIN[1]) / columns

        self.touches = Queue()
        self.running = True
        self.device = usb.core.find(idVendor=0x0eef, idProduct=0x0001)
        # use the first/default configuration
        self.device.set_configuration()
        logging.info("Found TouchPanel {} {}, split {}x{}".format(self.device.manufacturer, self.device.product,
                                                                  rows, columns))
        # first endpoint
        self.endpoint = self.device[0][(0, 0)][0]

    def processor(self):
        if not self.device:
            logging.info("Not running, no TouchPanel was found")
            return

        pressed = False
        while self.running:
            try:
                data = self.device.read(self.endpoint.bEndpointAddress, self.endpoint.wMaxPacketSize)
                if len(data) < 5 or data[0] not in [128, 129]:
                    continue  # Invalid or useless

                if pressed and data[0] == 129:
                    continue  # Holding

                if data[0] == 128:
                    pressed = False
                    continue

                x, y = data[1] * 128 + data[2], data[3] * 128 + data[4]

                mapped_x, mapped_y = int((x - TouchPanel.MIN[0]) / self.x_interval), \
                                     int((y - TouchPanel.MIN[1]) / self.y_interval)

                logging.debug(
                    "x={0}, y={1}, keypress={2}, mapped to ({3}, {4})".format(x, y, data[0], mapped_x, mapped_y))

                self.touches.put((mapped_x, mapped_y))
                pressed = True

            except usb.core.USBError as e:
                if not (e.args == ('Operation timed out',) or 'timeout' in e.args[1]):
                    logging.error(e)
                continue


if __name__ == '__main__':
    import threading

    logging.basicConfig(
        level=logging.DEBUG,
        format='(%(threadName)-10s) [%(name)s] %(message)s',
    )

    touchpanel = TouchPanel()
    t_touchpanel = threading.Thread(name='touchpanel', target=touchpanel.processor)
    t_touchpanel.start()

    print touchpanel.touches.get()
