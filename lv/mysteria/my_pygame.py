import functools

import pyglet

pyglet.lib.load_library('avbin')
pyglet.have_avbin = True

video_mapping = {
    1: {'source': 'idle/camera1.mp4'},
    2: {'source': 'idle/camera2.mp4'},
    3: {'source': 'idle/camera3.mp4'},
    4: {'source': 'idle/camera4.mp4'},
    5: {'source': 'idle/camera5.mp4'}
}

for idx, screen in enumerate(pyglet.window.get_platform().get_default_display().get_screens()):
    if idx in video_mapping:
        if idx == 0:
            video_mapping[idx]['window'] = pyglet.window.Window(screen=screen, width=1280, height=720)
        else:
            video_mapping[idx]['window'] = pyglet.window.Window(screen=screen, fullscreen=True)

        video_mapping[idx]['player'] = pyglet.media.load(video_mapping[idx]['source']).play()
        video_mapping[idx]['player']._set_eos_action = video_mapping[idx]['player'].EOS_LOOP


        def blit_bitmap(my_idx):
            p = video_mapping[my_idx]['player']

            if p.source and p.source.video_format:
                p.get_texture().blit(0, 0)
            else:
                print("nothing to play")


        video_mapping[idx]['window'].set_handler('on_draw', functools.partial(blit_bitmap, idx))

player_background = pyglet.media.Player()
player_background.queue(pyglet.media.load("idle/bg_slow_L.mp3"))
player_background.play()

HUD = pyglet.app

if __name__ == '__main__':
    HUD.run()
