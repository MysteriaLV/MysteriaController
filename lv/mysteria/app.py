import threading

from my_modbus import ModBus
from state import GameState
from web import app as Flask

flask = Flask
modbus = ModBus()
# hud = HUD
flask.game_state = game_state = GameState()

system_running = True

t_modbus = threading.Thread(name='modbus', target=modbus.processor)
t_flask = threading.Thread(name='flask', target=flask.run, kwargs={'port': 5555, 'debug': True, 'use_reloader': False})

t_modbus.start()
t_flask.start()
# HUD.run()

# noinspection PyRedeclaration
system_running = False
