import logging
import time
from collections import deque

import usb


class TouchPanel(object):
    # Calibration data
    MIN = (75, 125)
    MAX = (1980, 1935)

    LETTERS = ['X', 'C', 'B', 'A',
               'X', '3', '2', '1']

    def __init__(self, rows=2, columns=4):
        self.code_panel = self.code_timeout = None
        self.code_panel_input_start_time = None
        self.touch_panel_pressed = False

        self.x_interval = (TouchPanel.MAX[0] - TouchPanel.MIN[0]) / columns
        self.y_interval = (TouchPanel.MAX[1] - TouchPanel.MIN[1]) / rows
        self.columns = columns

        self.touches = list()
        self.incoming_data = deque()
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

    def register_code_panel_lua(self, code_panel, timeout):
        self.code_panel = code_panel
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
            read = self.device.read(self.endpoint.bEndpointAddress, self.endpoint.wMaxPacketSize)
            self.incoming_data.extendleft(read)

            if len(self.incoming_data) < 5:
                return  # Not enough data yet

            data = [
                self.incoming_data.pop(),
                self.incoming_data.pop(),
                self.incoming_data.pop(),
                self.incoming_data.pop(),
                self.incoming_data.pop()
            ]

            if data[0] not in [128, 129]:
                return  # Invalid or useless

            if self.touch_panel_pressed and data[0] == 129:
                return  # Holding

            if data[0] == 128:
                self.touch_panel_pressed = False
                return

            x, y = data[1] * 128 + data[2], data[3] * 128 + data[4]

            mapped_x, mapped_y = int((x - TouchPanel.MIN[0]) / self.x_interval), \
                                 int((y - TouchPanel.MIN[1]) / self.y_interval)

            absolute = mapped_y * self.columns + mapped_x
            letter = self.LETTERS[absolute]

            logging.debug(
                "x={0}, y={1}, keypress={2}, mapped to ({3}, {4})={5}".format(x, y, data[0],
                                                                              mapped_x, mapped_y, letter))

            self.touches.append(letter)
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

        if self.touches[-1:][0] == 'X':
            code = ''.join(self.touches[:-1])
            self.code_panel_input_start_time = None
            self.touches.clear()

            logging.info(f"Executing hint {code}")
            self.code_panel['code'](self.code_panel, code)


if __name__ == '__main__':
    import threading

    logging.basicConfig(
        level=logging.DEBUG,
        format='(%(threadName)-10s) [%(name)s] %(message)s',
    )

    touchpanel = TouchPanel(3, 3)
    t_touchpanel = threading.Thread(name='touchpanel', target=touchpanel.processor)
    t_touchpanel.start()

    touchpanel.register_code_panel_lua("test", 10)
