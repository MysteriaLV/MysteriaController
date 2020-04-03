import random
import shlex
import subprocess
import threading
import time
from typing import Dict

import vlc
from vlc import MediaPlayer, Instance

from mysteria.firmata import ZombieController


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
        self.idle_media_files = ['idle/nothing.jpg']
        self.needs_next_video = False
        self.zombie_fsm = None
        self.sparkler = None

        self.vlc: Instance = vlc.Instance(
            ['--no-spu', '--no-osd', '--video-on-top', '--video-y=1', '--video-x=-1200', '--fullscreen'])
        self.main_player: vlc.MediaPlayer = self.vlc.media_player_new()
        self.main_player.set_fullscreen(True)

        event_manager = self.main_player.event_manager()
        event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.ask_for_more)

        idle_checker = threading.Thread(name='zombie_idler', target=self.processor)
        idle_checker.start()

    # noinspection PyUnusedLocal
    def ask_for_more(self, event):
        self.needs_next_video = True

    def play_next_idle(self):
        self.play(random.choice(self.idle_media_files))

    def register_in_lua(self, hints_fsm, sparkler):
        self.sparkler: ZombieController = sparkler
        self.zombie_fsm = hints_fsm
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
        if self.sparkler:
            self.sparkler.sparkle()

    def processor(self):
        while True:
            time.sleep(0.01)
            if self.needs_next_video:
                # Inform code panel that we done playing current video
                if self.zombie_fsm:
                    self.zombie_fsm['ready_for_input'](self.zombie_fsm)

                self.play_next_idle()


class Sampler(object):
    vlc: Instance = vlc.Instance('--no-video')

    def __init__(self):
        self.tag_players = []
        self.player_groups: Dict[str, MediaPlayer] = {}

    def register_in_lua(self):
        return self

    @staticmethod
    @memoize
    def _get_sound_tag_player(sound_file) -> MediaPlayer:
        return Sampler.vlc.media_player_new('{}.mp3'.format(sound_file))

    def play(self, audio_file, group=None):
        # Stop previous audio if any
        if group and group in self.player_groups:
            self.player_groups[group].stop()

        player = self._get_sound_tag_player(audio_file)

        if player.is_playing() == 0:
            player.play()

        self.tag_players.append(player)
        if group:
            self.player_groups[group] = player

    def reset(self):
        for player in self.tag_players:
            player.stop()


class PotPlayer(object):

    def __init__(self):
        self.pot_players = dict()
        self.PLAYER_EXE = "PotPlayer_DISPLAY{display_number}.exe"
        self.PLAYER_RUN_CMD = '"C:\\Program Files\\DAUM\PotPlayer\\PotPlayer_DISPLAY{display_number}.exe" "{media_file}" /seek={offset} /new'
        # self.PLAYER_RUN_CMD = '"C:\\Program Files\\DAUM\PotPlayer\\PotPlayerMini64.exe" "{media_file}" /new /seek={offset}'
        self.DISPLAYS = [2, 3, 4, 5, 6]

    def register_in_lua(self):
        return self

    def stop(self, display_number):
        subprocess.run(f"taskkill /im {self.PLAYER_EXE.format(display_number=display_number)} /f")

    def play(self, display_number, media_file, offset=0):
        self.stop(display_number)
        cmd = self.PLAYER_RUN_CMD.format(display_number=display_number, media_file=media_file, offset=offset)
        print(cmd)

        try:
            subprocess.Popen(shlex.split(cmd))
        except FileNotFoundError:
            pass

    def reset(self):
        for i in self.DISPLAYS:
            self.stop(i)


if __name__ == '__main__':
    # z = ZombieBox()
    # z.start()
    # time.sleep(4)
    # print("GO")
    # z.idle_media_files = ['idle/11.mp4', 'idle/12.mp4']
    # # z.play('idle/11.mp4')
    # time.sleep(200)

    p = PotPlayer()
    p.play(2, 'idle/timer_1024x1280.mp4')
    # time.sleep(4)
    # p.play(2, 'idle/12.mp4')
    time.sleep(10)
