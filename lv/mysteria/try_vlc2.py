import time

import vlc

vlc_inst = vlc.Instance('--video-x=2030', '--video-y=1')
vlc_inst2 = vlc.Instance('--video-x=0', '--video-y=1')


def play(vlc_instance, media_url):
    main_player = vlc_instance.media_player_new()
    main_player.set_fullscreen(True)

    vlc_player = vlc_instance.media_list_player_new()
    vlc_player.set_media_player(main_player)

    media_list = vlc_instance.media_list_new()
    media_item = vlc_instance.media_new(media_url)
    media_list.add_media(media_item)

    vlc_player.set_media_list(media_list)

    vlc_player.set_playback_mode(vlc.PlaybackMode.loop)
    vlc_player.play()


play(vlc_inst, 'idle/11.mp4')
play(vlc_inst2, 'idle/12.mp4')

time.sleep(10)
