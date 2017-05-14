import vlc
from dotmap import DotMap


class HUD(object):
    default_bg_video_options = ['--no-audio', '--video-y=1']

    video_mappings = {
        1: DotMap({'source': 'idle/camera1.mp4', 'offset': 0}),
        2: DotMap({'source': 'idle/camera2.mp4', 'offset': 2000}),
        3: DotMap({'source': 'idle/camera3.mp4', 'offset': 3000}),
        4: DotMap({'source': 'idle/camera4.mp4', 'offset': 4000}),
        5: DotMap({'source': 'idle/camera5.mp4', 'offset': 5000}),
    }

    @staticmethod
    def _get_mlp(vlc_instance, media_url):
        main_player = vlc_instance.media_player_new()
        # main_player.set_fullscreen(True)

        media_list_player = vlc_instance.media_list_player_new()
        media_list_player.set_media_player(main_player)

        media_list = vlc_instance.media_list_new()
        media_item = vlc_instance.media_new(media_url)
        media_list.add_media(media_item)

        media_list_player.set_media_list(media_list)

        media_list_player.set_playback_mode(vlc.PlaybackMode.loop)
        return media_list_player

    def processor(self):
        for key, mapping in self.video_mappings.items():
            mapping.vlc = vlc.Instance(self.default_bg_video_options + ['--video-x=%s' % mapping.offset])
            mapping.mlp = self._get_mlp(mapping.vlc, mapping.source)

            mapping.mlp.play()


if __name__ == '__main__':
    HUD().processor()
