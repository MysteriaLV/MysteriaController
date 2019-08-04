import logging
import time
from collections import deque

import usb


class TouchPanel(object):
    # Calibration data
    MIN = (75, 125)
    MAX = (1980, 1935)

    def __init__(self, rows=2, columns=3):
        self.code_panel = self.code_length = self.code_timeout = None
        self.code_panel_input_start_time = None
        self.touch_panel_pressed = False

        self.x_interval = (TouchPanel.MAX[0] - TouchPanel.MIN[0]) / columns
        self.y_interval = (TouchPanel.MAX[1] - TouchPanel.MIN[1]) / rows
        self.columns = columns

        self.touches = deque()
        self.running = True
        try:
            self.device = usb.core.find(idVendor=0x0eef, idProduct=0x0001)
        except usb.core.NoBackendError:
            self.device = None

        if not self.device:
            logging.error("No USB touch panel was found")
            return

        # use the first/default configuration
        self.device.set_configuration()
        logging.info("Found TouchPanel {} {}, split {}x{}".format(self.device.manufacturer, self.device.product,
                                                                  rows, columns))
        # first endpoint
        self.endpoint = self.device[0][(0, 0)][0]

    def register_code_panel_lua(self, name, code_panel, code_length, timeout):
        self.code_panel = code_panel
        self.code_length = code_length
        self.code_timeout = timeout

    def processor(self):
        if not self.device:
            logging.info("Not running, no TouchPanel was found")
            return

        while self.running:
            self.poll_usb_device()
            if self.code_panel:
                self.process_codes()

    def poll_usb_device(self):
        try:
            data = self.device.read(self.endpoint.bEndpointAddress, self.endpoint.wMaxPacketSize)
            if len(data) < 5 or data[0] not in [128, 129]:
                return  # Invalid or useless

            if self.touch_panel_pressed and data[0] == 129:
                return  # Holding

            if data[0] == 128:
                self.touch_panel_pressed = False
                return

            x, y = data[1] * 128 + data[2], data[3] * 128 + data[4]

            mapped_x, mapped_y = int((x - TouchPanel.MIN[0]) / self.x_interval), \
                                 int((y - TouchPanel.MIN[1]) / self.y_interval)
            absolute = mapped_y * self.columns + mapped_x + 1

            logging.debug(
                "x={0}, y={1}, keypress={2}, mapped to ({3}, {4})={5}".format(x, y, data[0],
                                                                              mapped_x, mapped_y, absolute))

            self.touches.append((mapped_x, mapped_y, absolute))
            self.touch_panel_pressed = True

        except usb.core.USBError as e:
            if not (e.args == ('Operation timed out',) or 'timeout' in str(e.args[1])):
                logging.error(e)

    def process_codes(self):
        if len(self.touches) == 0:
            return

        if not self.code_panel_input_start_time:
            self.code_panel_input_start_time = time.time()

        if time.time() - self.code_panel_input_start_time > self.code_timeout:
            self.code_panel_input_start_time = None
            self.touches.clear()
            return

        if len(self.touches) == self.code_length:
            code = ''.join([str(x[2]) for x in self.touches])
            self.code_panel_input_start_time = None
            self.touches.clear()

            if self.code_panel['code_' + code]:
                self.code_panel['code_' + code](self.code_panel)


if __name__ == '__main__':
    import threading

    logging.basicConfig(
        level=logging.DEBUG,
        format='(%(threadName)-10s) [%(name)s] %(message)s',
    )

    touchpanel = TouchPanel(3, 3)
    t_touchpanel = threading.Thread(name='touchpanel', target=touchpanel.processor)
    t_touchpanel.start()

    touchpanel.register_code_panel_lua("test", "sdf", 2, 10)
