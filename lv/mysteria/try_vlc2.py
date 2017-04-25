import time
import vlc

# --directx-device="\\.\DISPLAY2"
# --video-x=2000
vlc_inst = vlc.Instance('--mouse-hide-timeout=0', '--fullscreen', '--repeat')
media = vlc_inst.media_new('idle/camera1.mp4', '--repeat')

player = vlc_inst.media_player_new()
player.set_fullscreen(True)
player.set_media(media)
player.play()

time.sleep(10)
