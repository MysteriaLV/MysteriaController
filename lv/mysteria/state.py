import logging

import vlc
from lupa import LuaRuntime

LUA_SCENARIO = 'lua/Aliens.lua'

lua = LuaRuntime(unpack_returned_tuples=True)


class GameState(object):
    def __init__(self, modbus, touchpanel):
        self.touchpanel = touchpanel
        self.modbus = modbus
        self.sampler = Sampler()
        self.fsms = {}

        lua.globals()['REGISTER_STATES'] = self.register_fsm
        lua.globals()['REGISTER_MODBUS_SLAVE'] = self.register_slave_lua
        lua.globals()['REGISTER_CODE_PANEL'] = self.touchpanel.register_code_panel_lua
        lua.globals()['REGISTER_SAMPLER'] = self.sampler.register_sampler
        lua.globals()['MODBUS_ACTION'] = self.modbus.send_action
        lua.globals()['print'] = logging.getLogger('lua').info
        lua.execute(open(LUA_SCENARIO, 'r').read())

        # lua.execute('alien_arm.complete()')
        # print lua.eval('quest')

    # @lupa.unpacks_lua_table_method
    def register_slave_lua(self, slave):
        self.modbus.register_slave(slave)

    def register_fsm(self, name, fsm):
        self.fsms[name] = fsm

    def fire_event(self, fsm_name, event):
        return self.fsms[fsm_name][event](self.fsms[fsm_name])


def memoize(f):
    """ Memoization decorator for functions taking one or more arguments. """

    class memodict(dict):
        def __init__(self, f):
            self.f = f

        def __call__(self, *args):
            return self[args]

        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret

    return memodict(f)


class Sampler(object):
    vlc = vlc.Instance('--no-video')

    def __init__(self):
        self.tag_players = {}

    mappings = {
        'startup': 'Kalinin3'
    }

    def register_sampler(self):
        return self

    @staticmethod
    @memoize
    def _get_sound_tag_player(tag, sound_file):
        return Sampler.vlc.media_player_new('idle/{}.mp3'.format(sound_file))

    def play(self, sound_tag, loop=False):
        player = self._get_sound_tag_player(sound_tag, self.mappings.get(sound_tag, sound_tag))

        if player.is_playing() == 0:
            player.play()
