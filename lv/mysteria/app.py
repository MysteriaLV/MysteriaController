import logging
import threading

from my_modbus import ModBus
from state import GameState
from web import app as Flask

logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s',
)


def main():
    flask = Flask
    modbus = ModBus()
    # hud = HUD
    flask.game_state = GameState(modbus)
    t_modbus = threading.Thread(name='modbus', target=modbus.processor)
    t_flask = threading.Thread(name='flask', target=flask.run,
                               kwargs={'port': 5555, 'debug': True, 'use_reloader': False})
    t_modbus.start()
    t_flask.start()
    # HUD.run()

    # noinspection PyRedeclaration
    # modbus.running = False


if __name__ == '__main__':
    main()

