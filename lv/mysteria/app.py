import logging
import threading

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from mysteria.my_modbus import ModBus
from mysteria.state import GameState
from mysteria.touchpanel import TouchPanel
from mysteria.usb_device_detector import USBDetector
from mysteria.web import app as flask, eternal_flask_app

logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-7s) %(asctime)s [%(name)s] %(message)s',
    datefmt='%M:%S'
)

# Set up Sentry to IGNORE logging.error() from being reported
sentry_logging = LoggingIntegration(
    level=logging.INFO,           # Capture INFO and above as breadcrumbs
    event_level=logging.CRITICAL  # Only send CRITICAL logs to Sentry
)

sentry_sdk.init(
    dsn="https://XXX@eu.glitchtip.com/3",
    integrations=[sentry_logging],
    shutdown_timeout=30
)

def main():
    modbus = ModBus(port='COM19')
    touchpanel = TouchPanel()
    usb_detector = USBDetector()
    flask.game_state = GameState(modbus, touchpanel, usb_detector)
    t_modbus = threading.Thread(name='modbus', target=modbus.processor)
    t_touchpanel = threading.Thread(name='touchpanel', target=touchpanel.processor)
    t_usb_detector = threading.Thread(name='usb_detector', target=usb_detector.processor)
    t_flask = threading.Thread(name='flask', target=eternal_flask_app,
                               kwargs={'port': 5555, 'host': '0.0.0.0', 'debug': True, 'use_reloader': False})

    t_modbus.start()
    t_touchpanel.start()
    t_usb_detector.start()
    t_flask.start()


if __name__ == '__main__':
    main()



