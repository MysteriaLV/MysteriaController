local machine = require('lua/statemachine')
local rs485_node = require('lua/rs485_node')

--noinspection UnusedDef
quest = machine.create({
    events = {
        { name = 'restart', from = '*', to = 'preparation' },
        { name = 'make_intro', from = 'preparation', to = 'intro' },
        { name = 'start', from = 'intro', to = 'powered_off' },
        { name = 'power_on', from = 'powered_off', to = 'powered_on' },
        { name = 'open_laboratory', from = 'powered_on', to = 'laboratory_access' },
        { name = 'start_self_destruct', from = 'laboratory_access', to = 'self_destruction' },
        { name = 'win', from = 'self_destruction', to = 'victory' },
        { name = 'lose', from = 'self_destruction', to = 'failure' },
    },
    callbacks = {
        on_preparation = function(self)
            print('Resetting everything to inital states, walking around cleaning etc')

            power_console:reset()
            gestures:reset()
            boxes:reset()
            magnetic_door:reset()
            small_colbs:reset()
            destruction_console:reset()
            sample_transmitter:reset()
            sampler:reset()
            video:reset()
            hints:reset()
            zombie_controller:reset()

            light:full_lights()
            light:unlock_door()
            light:enable_xray()
            zombie_controller:mirror(True)

            zombie_box:set_idle_files({ 'idle/finish/tv/intro.mp4' })
            zombie_box:start()
            video:play(5, 'idle/finish/intro/1024x1280.mp4') -- nad rukavicami (5)
            video:play(1, 'idle/table.jpg') -- stol (2)
            video:play(3, 'idle/finish/intro/text_standby.mp4') -- podskazki (4)
--                video:play(4, 'idle/camera3.mp4') -- telek (3)
            video:play(2, 'idle/finish/intro/1600x1200.mp4') -- osnovnoj (3)
            video:play(6, 'idle/finish/intro/1280x1024.mp4') -- pult (6)
        end,
        on_intro = function(self)
            print('People are entering the room')

            light:no_power()
            light:disable_xray()
            zombie_controller:mirror(False)
--            sampler:play('bg_slow_L')
        end,
        on_start = function(self)
            print('Game is ON!')
            light:lock_door();

            video:play(3, 'idle/finish/game/text.mp4') -- podskazki (4)
            self.start_time = os.clock();
            sampler:play('audio/power2')
        end,
        on_power_console_connected = function(self)
            sampler:play('Church_Organ_Powerup')
            light:power_console_connected()
        end,
        on_powered_on = function(self)
            print('Lights and machinery are on now')
            sampler:play('audio/power')

            video:play(5, 'idle/finish/game/5_1024x1280.mp4') -- nad rukavicami (5)
            video:play(2, 'idle/finish/game/3_1600x1200.mp4') -- osnovnoj (3)
            video:play(6, 'idle/finish/game/5_1024x1280.mp4') -- pult (6)

            light:power_active()
            light:enable_xray()
            zombie_controller:mirror(True)
            magnetic_door:activated()
        end,
        on_laboratory_access = function(self)
            print('We are in Room2 now.')
        end,
        on_zombie_activated = function(self)
            print('They woke the zombie!')
            zombie_box:set_idle_files({ 'idle/finish/tv/standby.mp4' })
            zombie_box:play('idle/finish/tv/start.mp4')
        end,
        on_self_destruction = function(self)
            print('It\'s the final countdown.')
            sampler:play('audio/alarm')

            video:play(5, 'idle/finish/alarm/6_1024x1280.mp4') -- nad rukavicami (5)
            video:play(2, 'idle/finish/alarm/6_1024x1280.mp4') -- osnovnoj (3)
            video:play(6, 'idle/finish/alarm/exit_pass.mp4') -- pult (6)

            destruction_console:activated()
            light:alarms()
        end,
        on_victory = function(self)
            print('You won!')
            sampler:play('music1_left')
            light:full_lights()
            light:unlock_door()
        end,
    }
})
REGISTER_STATES("main_quest", quest)

------------------------------- ROOM 1 -----------------------------------------------

power_console = rs485_node.create({
    name = 'power_console',
    slave_id = 6,
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'disconnected' },
        { name = 'connect', triggered_by_register = 1, action_id = 2, from = 'disconnected', to = 'powered_off' },
        { name = 'power_on', triggered_by_register = 2, action_id = 3, from = 'powered_off', to = 'completed' },
    },
    callbacks = {
        on_powered_off = function()
            print('Power console has wire connected')
            quest:on_power_console_connected()
        end,
        on_completed = function()
            print('Power console blocks are complete, station is powering on')
            quest:power_on()
        end,
    }
})

light = rs485_node.create({
    name = 'light',
    slave_id = 1,
    events = {
        { name = 'full_lights', action_id = 1, from = '*', to = 'idle' },
        { name = 'no_power', action_id = 2, from = '*', to = 'idle' },
        { name = 'power_active', action_id = 3, from = '*', to = 'idle' },
        { name = 'alarms', action_id = 4, from = '*', to = 'idle' },
        { name = 'lock_door', action_id = 5, from = '*', to = 'idle' },
        { name = 'unlock_door', action_id = 6, from = '*', to = 'idle' },
        { name = 'enable_xray', action_id = 7, from = '*', to = 'idle' },
        { name = 'disable_xray', action_id = 8, from = '*', to = 'idle' },
        { name = 'force_lapa', action_id = 9, from = '*', to = 'idle' },
        { name = 'power_console_connected', action_id = 10, from = '*', to = 'idle' },
    },
})

boxes = rs485_node.create({
    name = 'boxes',
    slave_id = 2,
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'idle' },
        { name = 'minor_failure', triggered_by_register = 1, from = 'idle', to = 'idle' },
        { name = 'major_failure', triggered_by_register = 2, from = 'idle', to = 'idle' },
        { name = 'complete', triggered_by_register = 3, action_id = 2, from = '*', to = 'completed' },
    },
})

gestures = rs485_node.create({
    name = 'gestures',
    slave_id = 3,
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'idle' },
        { name = 'complete', triggered_by_register = 1, action_id = 2, from = 'idle', to = 'completed' },
        { name = 'left', triggered_by_register = 2, from = 'idle', to = 'idle' },
        { name = 'right', triggered_by_register = 3, from = 'idle', to = 'idle' },
        { name = 'up', triggered_by_register = 4, from = 'idle', to = 'idle' },
        { name = 'down', triggered_by_register = 5, from = 'idle', to = 'idle' },
    },
    callbacks = {
        on_completed = function()
            print('Gestures are resolved')
        end,
    }
})

small_colbs = rs485_node.create({
    name = 'small_colbs',
    slave_id = 4,
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'idle' },
        { name = 'complete', triggered_by_register = 1, from = 'idle', to = 'completed' },
    },
    callbacks = {
        on_completed = function()
            print('Gestures are resolved')
        end,
    }
})

magnetic_door = rs485_node.create({
    name = 'magnetic_door',
    slave_id = 5,
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'idle' },
        { name = 'activated', action_id = 2, from = 'idle', to = 'active' },
        { name = 'opened', triggered_by_register = 1, from = 'active', to = 'completed' },
        { name = 'force_complete', action_id = 3, from = '*', to = 'completed' },
    },
    callbacks = {
        on_completed = function()
            print('People entered second room')
            quest:open_laboratory()
        end,
    }
})

destruction_console = rs485_node.create({
    name = 'destruction_console',
    slave_id = 7,
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'idle' },
        { name = 'activated', action_id = 2, from = 'idle', to = 'active' },
        { name = 'force_step', action_id = 2, from = '*', to = 'active' },
        { name = 'complete', triggered_by_register = 1, from = 'active', to = 'completed' },
    },
    callbacks = {
        on_completed = function()
            print('They entered correct code in a console!')
            quest:win()
        end,
    }
})

sample_transmitter = rs485_node.create({
    name = 'sample_transmitter',
    slave_id = '192.168.1.50',
    poll_frequency = '2',
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'idle' },
        { name = 'force_step', action_id = 2, from = '*', to = 'idle' },
        { name = 'complete', triggered_by_register = 1, from = '*', to = 'completed' },
        { name = 'empty_upload', triggered_by_register = 2, from = '*', to = 'idle' },
        { name = 'incomplete_upload', triggered_by_register = 3, from = '*', to = 'idle' },
    },
    callbacks = {
        on_completed = function()
            print('Samples are transmitted. Sound the alarm!')
            quest:start_self_destruct()
        end,
    }
})

hints = machine.create({
    events = {
        { name = 'reset', from = '*', to = 'idle' },
        { name = 'ready_for_input', from = '*', to = 'idle' },
        { name = 'code_BAC1', from = 'idle', to = 'hint_1' },
        { name = 'code_BAC2', from = 'idle', to = 'hint_2' },
        { name = 'code_BCA1', from = 'idle', to = 'hint_3' },
        { name = 'code_CAC1', from = 'idle', to = 'hint_4' },
        { name = 'code_BCA2', from = 'idle', to = 'hint_5' },
        { name = 'code_CBC1', from = 'idle', to = 'hint_6' },
        { name = 'code_CBC2', from = 'idle', to = 'hint_7' },
        { name = 'code_CBC3', from = 'idle', to = 'hint_8' },
        { name = 'code_ACB1', from = 'idle', to = 'hint_9' },
        { name = 'code_ACB2', from = 'idle', to = 'hint_10' },
        { name = 'code_ACB3', from = 'idle', to = 'hint_11' },
        { name = 'code_CBA1', from = 'idle', to = 'hint_12' },
        { name = 'code_CBA2', from = 'idle', to = 'hint_13' },
        { name = 'code_CBA3', from = 'idle', to = 'hint_14' },
        { name = 'code_ABA1', from = 'idle', to = 'hint_15' },
        { name = 'code_ABA2', from = 'idle', to = 'hint_16' },
        { name = 'code_ABA3', from = 'idle', to = 'hint_17' },
        { name = 'code_BCB1', from = 'idle', to = 'hint_18' },
        { name = 'code_BCB2', from = 'idle', to = 'hint_19' },
        { name = 'code_BCB3', from = 'idle', to = 'hint_20' },
    },
    callbacks = {
        on_hint_1 = function()
            zombie_box:play('idle/finish/tv/hints/1.mp4')
        end,
        on_hint_2 = function()
            zombie_box:play('idle/finish/tv/hints/2.mp4')
        end,
        on_hint_3 = function()
            zombie_box:play('idle/finish/tv/hints/3.mp4')
        end,
        on_hint_4 = function()
            zombie_box:play('idle/finish/tv/hints/5.mp4')
        end,
        on_hint_5 = function()
            zombie_box:play('idle/finish/tv/hints/6.mp4')
        end,
        on_hint_6 = function()
            zombie_box:play('idle/finish/tv/hints/7.mp4')
        end,
        on_hint_7 = function()
            zombie_box:play('idle/finish/tv/hints/8.mp4')
        end,
        on_hint_8 = function()
            zombie_box:play('idle/finish/tv/hints/9.mp4')
        end,
        on_hint_9 = function()
            zombie_box:play('idle/finish/tv/hints/14.mp4')
        end,
        on_hint_10 = function()
            zombie_box:play('idle/finish/tv/hints/15.mp4')
        end,
        on_hint_11 = function()
            zombie_box:play('idle/finish/tv/hints/16.mp4')
        end,
        on_hint_12 = function()
            zombie_box:play('idle/finish/tv/hints/11.mp4')
        end,
        on_hint_13 = function()
            zombie_box:play('idle/finish/tv/hints/12.mp4')
        end,
        on_hint_14 = function()
            zombie_box:play('idle/finish/tv/hints/13.mp4')
        end,
        on_hint_15 = function()
            zombie_box:play('idle/finish/tv/hints/17.mp4')
        end,
        on_hint_16 = function()
            zombie_box:play('idle/finish/tv/hints/18.mp4')
        end,
        on_hint_17 = function()
            zombie_box:play('idle/finish/tv/hints/19.mp4')
        end,
        on_hint_18 = function()
            zombie_box:play('idle/finish/tv/hints/20.mp4')
        end,
        on_hint_19 = function()
            zombie_box:play('idle/finish/tv/hints/21.mp4')
        end,
        on_hint_20 = function()
            zombie_box:play('idle/finish/tv/hints/22.mp4')
        end,
    }
})

REGISTER_CODE_PANEL(hints, 20) -- VAR, timeout
REGISTER_STATES("hints", hints)
sampler = REGISTER_SAMPLER()
zombie_controller = REGISTER_ZOMBIE_CONTROLLER(quest)
zombie_box = REGISTER_VLC(hints, zombie_controller)
video = REGISTER_POTPLAYER()

--Fire off main initialization machine
quest:restart()
