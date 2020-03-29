import os

import flask_sijax
from flask import Flask, render_template, g

app = Flask(__name__)
app.game_state = None

app.config["SIJAX_STATIC_PATH"] = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
flask_sijax.Sijax(app)


@flask_sijax.route(app, '/')
def index():
    def fire_event_fsm(obj_response, fsm, event):
        if app.game_state.fire_event(fsm, event):
            obj_response.html('#flash', f'{fsm} {event} fired')

    def fire_event_modbus_fsm(obj_response, slave_id, event):
        try:
            slave_id = int(slave_id)
        except:
            pass

        if app.game_state.modbus.fire_event(slave_id, event):
            obj_response.html('#flash', f'{slave_id} {event} fired')

    if g.sijax.is_sijax_request:
        g.sijax.register_callback('fire_event_fsm', fire_event_fsm)
        g.sijax.register_callback('fire_event_modbus_fsm', fire_event_modbus_fsm)
        return g.sijax.process_request()

    return render_template('page.html', state=app.game_state)


@flask_sijax.route(app, '/pc_controls')
def pc_controls():
    def _controls(obj_response, action):
        if action == 'reboot':
            os.system('shutdown /r /t 0 /f')
        elif action == 'shutdown':
            os.system('shutdown /s /t 0 /f')

        obj_response.html('#flash', f'Executing {action}')

    if g.sijax.is_sijax_request:
        g.sijax.register_callback('pc', _controls)
        return g.sijax.process_request()

    return 400


def eternal_flask_app(**kwargs):
    while True:
        app.run(**kwargs)
