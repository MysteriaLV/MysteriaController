import os

import flask_sijax
from flask import Flask, render_template, g
from state import GameState

app = Flask(__name__)

app.config["SIJAX_STATIC_PATH"] = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
flask_sijax.Sijax(app)


@flask_sijax.route(app, '/')
def index():
    def say_hi(obj_response):
        obj_response.alert('Hi there!')

    if g.sijax.is_sijax_request:
        g.sijax.register_callback('sayHi', say_hi)
        return g.sijax.process_request()

    return render_template('page.html', state=app.game_state)


if __name__ == '__main__':
    app.game_state = GameState()

    app.run(debug=True, port=5555)
