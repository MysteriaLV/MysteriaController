import threading
import time
import random

import vlc


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


class ZombieBox(object):
    def __init__(self):
        self.idle_media_files = ['idle/1.mp4', 'idle/2.mp4', 'idle/3.mp4', 'idle/4.mp4']
        self.needs_next_video = False

        self.vlc: vlc.Instance = vlc.Instance(
            ['--no-spu', '--no-osd', '--video-on-top', '--video-y=1', '--video-x=3000', '--fullscreen'])
        self.main_player: vlc.MediaPlayer = self.vlc.media_player_new()

        event_manager = self.main_player.event_manager()
        event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.ask_for_more)

        idle_checker = threading.Thread(name='zombie_idler', target=self.processor)
        idle_checker.start()

    # noinspection PyUnusedLocal
    def ask_for_more(self, event):
        self.needs_next_video = True

    def play_next_idle(self):
        self.play(random.choice(self.idle_media_files))

    def register_in_lua(self):
        return self

    def set_idle_files(self, media_files):
        # LUA unpack
        media_files = list(dict(media_files).values())

        self.idle_media_files = media_files

    def start(self):
        if not self.main_player.is_playing():
            self.needs_next_video = True

    def play(self, media_file):
        self.needs_next_video = False

        self.main_player.set_media(self.vlc.media_new(media_file))
        self.main_player.play()

    def processor(self):
        while True:
            time.sleep(0.01)
            if self.needs_next_video:
                self.play_next_idle()


class Sampler(object):
    vlc = vlc.Instance('--no-video')

    def __init__(self):
        self.tag_players = []

    def register_in_lua(self):
        return self

    @staticmethod
    @memoize
    def _get_sound_tag_player(sound_file):
        return Sampler.vlc.media_player_new('idle/{}.mp3'.format(sound_file))

    def play(self, audio_file, loop=False):
        player = self._get_sound_tag_player(audio_file)

        if player.is_playing() == 0:
            player.play()

        self.tag_players.append(player)

    def reset(self):
        for player in self.tag_players:
            player.stop()


if __name__ == '__main__':
    z = ZombieBox()
    z.start()
    time.sleep(4)
    print("GO")
    z.idle_media_files = ['idle/11.mp4', 'idle/12.mp4']
    # z.play('idle/11.mp4')
    time.sleep(200)
