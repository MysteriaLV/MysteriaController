import vlc
from dotmap import DotMap


class HUD(object):
    default_bg_video_options = ['--no-audio', '--video-y=1', '--vout=direct3d11', '--avcodec-hw=any']

    # video_mappings = {
    #     # 1: DotMap({'source': 'idle/camera1.mp4', 'offset': 0}),
    #     2: DotMap({'source': 'idle/1360x768.mov',    'offset': 1280}),
    #     3: DotMap({'source': 'idle/1280x1024.mov',   'offset': 1280+768}),
    #     4: DotMap({'source': 'idle/1280x1024-2.mov', 'offset': 1280+768+1280}),
    #     5: DotMap({'source': 'idle/1280x1024.mov',   'offset': 1280+768+1280+1280}),
    #     6: DotMap({'source': 'idle/1360x768.mov',    'offset': 1280+768+1280+1280+768}),
    # }

    video_mappings = {
        # 1: DotMap({'source': 'idle/camera1.mp4', 'offset': 0}),
        2: DotMap({'source': 'idle/1360x768.mov',    'offset': 1280}),
        3: DotMap({'source': 'idle/1280x1024.mov',   'offset': 1280+768}),
        4: DotMap({'source': 'idle/1280x1024-2.mov', 'offset': 1280+768+1280}),
        5: DotMap({'source': 'idle/1280x1024.mov',   'offset': 1280+768+1280+1280}),
        6: DotMap({'source': 'idle/1360x768.mov',    'offset': 1280+768+1280+1280+768}),
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
