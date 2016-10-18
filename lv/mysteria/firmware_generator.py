import os

import jinja2
import lupa
from lupa import LuaRuntime

from state import LUA_SCENARIO


def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)


lua = LuaRuntime(unpack_returned_tuples=True)


def _dummy(*args):
    pass


@lupa.unpacks_lua_table_method
def register_slave_lua(slave):
    # TODO make sure the are no gaps
    events = {i.config.triggered_by_register: i.config.name.upper()
              for i in slave['events'].values() if i.config.triggered_by_register}

    actions = {i.config.action_id: i.config.name.capitalize()
               for i in slave['events'].values() if i.config.action_id}

    # TODO basic validation for identical event/action ids
    with open('arduino/{}.ino'.format(slave.name.lower()), 'w') as f:
        f.write(render('arduino/_template.ino.j2', {
            'name': slave.name.upper(),
            'slave_id': slave.slave_id,
            'events': events,
            'actions': actions,
        }))


lua.globals()['REGISTER_STATES'] = _dummy
lua.globals()['REGISTER_MODBUS_SLAVE'] = register_slave_lua
lua.globals()['MODBUS_ACTION'] = _dummy
lua.execute(open(LUA_SCENARIO, 'r').read())
