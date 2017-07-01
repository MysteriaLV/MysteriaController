import ipaddress
import jinja2
import lupa
import os
from lupa import LuaRuntime

from state import LUA_SCENARIO

TEMPLATE_SERIAL = 'arduino/_template_serial.ino.j2'
TEMPLATE_TCP = 'arduino/_template_serial.ino.j2'
# TEMPLATE_TCP = 'arduino/_template_tcp.ino.j2'


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
    if not os.path.exists('arduino/{}_modbus'.format(slave.name.lower())):
        os.mkdir('arduino/{}_modbus'.format(slave.name.lower()))

    with open('arduino/{0}_modbus/{0}_modbus.ino'.format(slave.name.lower()), 'w') as f:
        def get_template(slave_id):
            if type(slave_id) is int:
                return TEMPLATE_SERIAL

            assert ipaddress.ip_address(slave_id)
            return TEMPLATE_TCP

        f.write(render(get_template(slave.slave_id), {
            'game': LUA_SCENARIO,
            'slave_name': slave.name.upper(),
            'slave_id': slave.slave_id,
            'events': events,
            'actions': actions,

            'wifi_sid': os.environ.get('WIFI_SID', 'ENTER_WIFI_SID'),
            'wifi_pass': os.environ.get('WIFI_PASS', 'ENTER_WIFI_PASS'),

            'MODBUS_DEBUG': os.environ.get('MODBUS_DEBUG', False),
        }))


lua.globals()['REGISTER_STATES'] = _dummy
lua.globals()['REGISTER_CODE_PANEL'] = _dummy
lua.globals()['REGISTER_SAMPLER'] = _dummy
lua.globals()['REGISTER_MODBUS_SLAVE'] = register_slave_lua
lua.globals()['MODBUS_ACTION'] = _dummy
lua.execute(open(LUA_SCENARIO, 'r').read())
