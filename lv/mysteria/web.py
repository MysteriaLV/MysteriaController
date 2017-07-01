import flask_sijax
import os
from flask import Flask, render_template, g

app = Flask(__name__)
app.game_state = None

app.config["SIJAX_STATIC_PATH"] = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
flask_sijax.Sijax(app)


@flask_sijax.route(app, '/')
def index():
    def fire_event_fsm(obj_response, fsm, event):
        if app.game_state.fire_event(fsm, event):
            obj_response.html('#flash', '{} {} fired'.format(fsm, event))

    def fire_event_modbus_fsm(obj_response, slave_id, event):
        try:
            slave_id = int(slave_id)
        except:
            pass

        if app.game_state.modbus.fire_event(slave_id, event):
            obj_response.html('#flash', '{} {} fired'.format(slave_id, event))

    if g.sijax.is_sijax_request:
        g.sijax.register_callback('fire_event_fsm', fire_event_fsm)
        g.sijax.register_callback('fire_event_modbus_fsm', fire_event_modbus_fsm)
        return g.sijax.process_request()

    return render_template('page.html', state=app.game_state)


def eternal_flask_app(**kwargs):
    while True:
        app.run(**kwargs)
