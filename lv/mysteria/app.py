import logging
import threading

from my_modbus import ModBus
from state import GameState
from web import app as flask, eternal_flask_app


logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) [%(levelname)-7s] %(message)s - %(funcName)s',
)


def main():
    modbus = ModBus()
    # hud = HUD
    flask.game_state = GameState(modbus)
    t_modbus = threading.Thread(name='modbus', target=modbus.processor)
    t_flask = threading.Thread(name='flask', target=eternal_flask_app,
                               kwargs={'port': 5555, 'debug': True, 'use_reloader': False})
    t_modbus.start()
    t_flask.start()
    # HUD.run()

    # noinspection PyRedeclaration
    # modbus.running = False


if __name__ == '__main__':
    main()