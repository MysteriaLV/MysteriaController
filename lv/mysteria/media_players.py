import configparser
import os
import random
import shlex
import subprocess
import threading
import time
from typing import Dict, List

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
    def __init__(self, sampler):
        self.sampler = sampler
        self.idle_media_files = ['idle/nothing.jpg']
        self.needs_next_video = False
        self.zombie_fsm = None
        self.sparkler = None

        self.vlc: Instance = vlc.Instance(
            ['--no-volume-save', '--no-spu', '--no-osd', '--video-on-top', '--video-y=1', '--video-x=-3000',
             '--fullscreen'])
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
        self.sampler.resume_backgroud()

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

        self.sampler.pause_backgroud()

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
    vlc: Instance = vlc.Instance('--no-video --no-volume-save')

    def __init__(self):
        self.tag_players: List[MediaPlayer] = []
        self.player_groups: Dict[str, MediaPlayer] = {}

    def register_in_lua(self):
        return self

    @staticmethod
    @memoize
    def _get_sound_tag_player(sound_file) -> MediaPlayer:
        return Sampler.vlc.media_player_new('{}.mp3'.format(sound_file))

    # noinspection PyUnusedLocal
    def pause_backgroud(self, *args):
        if 'background' in self.player_groups:
            self.player_groups['background'].pause()

    # noinspection PyUnusedLocal
    def resume_backgroud(self, *args):
        if 'background' in self.player_groups:
            self.player_groups['background'].play()

    def play(self, audio_file, group=None):
        # Stop previous audio if any
        if group and group in self.player_groups:
            self.player_groups[group].stop()

        player = self._get_sound_tag_player(audio_file)

        if player.is_playing() == 0:
            player.stop()
            player.play()

        if not group:
            # For one-shot samples quiet the other sounds
            self.pause_backgroud()
            player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, self.resume_backgroud)

        self.tag_players.append(player)
        if group:
            self.player_groups[group] = player

    def reset(self):
        for player in self.tag_players:
            player.stop()

        self.tag_players.clear()
        self.player_groups.clear()


import configparser
import os
import subprocess
import shlex

class PotPlayer(object):
    SETTINGS_TO_UPDATE = {
        "Settings": {
            "AutoDownloadFile": "0",
            "CheckAutoUpdate": "0",
            "RestoreLastState": "1",
            "StartScreenSize": "5",
            "RepeatPlay2": "2"
        },
        "Positions": {
            "IsZoomFull": "1",
            "MainWindowState": "129",
            "VideoWindowHeight": "-1",
            "VideoWindowWidth": "-1",
            "MainY": "0"
        }
    }

    def __init__(self):
        self.pot_players = dict()

        self.DISPLAYS = [2, 3, 4, 5, 6]

        self.APPDATA_ROAMING_PATH = r"C:\Users\Mysteria\AppData\Roaming"
        self.MAIN_X_VALUES = {
            2: "-768",
            3: "0",
            4: "1280",
            5: "2560",
            6: "3840"
        }

        self.POT_PLAYER_PATH = r"C:\Program Files\DAUM\PotPlayer"
        self.PLAYER_EXE_NAME_TEMPLATE = "PotPlayer_DISPLAY{display_number}.exe"
        self.PLAYER_RUN_CMD = f'"{os.path.join(self.POT_PLAYER_PATH, self.PLAYER_EXE_NAME_TEMPLATE)}"' + ' "{media_file}" /seek={offset} /new'

    def register_in_lua(self):
        return self

    def stop(self, display_number):
        exe_name = self.PLAYER_EXE_NAME_TEMPLATE.format(display_number=display_number)
        subprocess.run(["taskkill", "/im", exe_name, "/f"], stderr=subprocess.PIPE)

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
            self.update_ini_file(i)

    def update_ini_file(self, display_number):
        file_path = os.path.join(self.APPDATA_ROAMING_PATH, f"PotPlayer_DISPLAY{display_number}", f"PotPlayer_DISPLAY{display_number}.ini")

        config = configparser.ConfigParser()
        config.optionxform = str    # make it case sensitive
        config.read(file_path, encoding='utf-16')

        # Удаляем секцию 'SimpleOpen', если она есть
        config.remove_section('SimpleOpen')

        # Обновляем значения в соответствующих секциях
        for section, settings in self.SETTINGS_TO_UPDATE.items():
            if not config.has_section(section):
                config.add_section(section)
            for key, value in settings.items():
                config.set(section, key, value)

        # Устанавливаем соответствующее значение MainX
        config.set("Positions", "MainX", str(self.MAIN_X_VALUES[display_number]))

        # Сохраняем изменения
        with open(file_path, "w", encoding='utf-16') as configfile:
            config.write(configfile, space_around_delimiters=False)

        print(f"File {file_path} updated successfully!")


if __name__ == '__main__':
    pass
    # z = ZombieBox()
    # z.start()
    # time.sleep(4)
    # print("GO")
    # z.idle_media_files = ['idle/11.mp4', 'idle/12.mp4']
    # # z.play('idle/11.mp4')
    # time.sleep(200)
    #
    # p = PotPlayer()
    # p.reset()
    # p.play(2, 'idle/timer_1024x1280.mp4')
    # # time.sleep(4)
    # # p.play(2, 'idle/12.mp4')
    # time.sleep(10)
    #
    # s = Sampler()
    # s.reset()
    #
    # s.play('audio/alert', "background")
    # time.sleep(2)
    # print(1)
    # s.play('audio/ru/power_cable_connected')
    # time.sleep(11)
    # print(2)
    # s.play('audio/ru/power_cable_connected')
    # time.sleep(1000)
