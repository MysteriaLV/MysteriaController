local machine = require('lua/statemachine')
local rs485_node = require('lua/rs485_node')

main = 2
table = 1
hints = 3
bio = 5
console = 6

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
            zombie:reset()
            zombie_arduino:reset()

            light:full_lights()
            light:unlock_door()
            light:enable_xray()
            zombie_arduino:mirror(true)

            zombie_video:set_idle_files({ 'idle/finish/prepare/1.jpg' })
            zombie_video:start()

            video:play(main, 'idle/finish/prepare/3.jpg')
            video:play(table, 'idle/finish/prepare/4.jpg')
            video:play(hints, 'idle/finish/prepare/6.jpg')
            video:play(bio, 'idle/finish/prepare/2.jpg')
            video:play(console, 'idle/finish/prepare/5.jpg')
        end,
        on_intro = function(self)
            print('People are entering the room')

            light:no_power()
            light:disable_xray()
            zombie_arduino:mirror(false)
            sampler:play('audio/intro', 'background')

            zombie_video:set_idle_files({ 'idle/finish/tv/intro.mp4' })

            video:play(main, 'idle/finish/intro/1600x1200.mp4')
            video:play(table, 'idle/table.jpg')
            video:play(hints, 'idle/finish/intro/text_standby.mp4')
            video:play(bio, 'idle/finish/intro/1024x1280.mp4')
            video:play(console, 'idle/finish/intro/1280x1024.mp4')
        end,
        on_start = function(self)
            print('Game is ON!')
            light:lock_door();

            video:play(hints, 'idle/finish/game/text.mp4')
            self.start_time = os.clock();
        end,
        on_power_console_connected = function(self)
            -- TODO           sampler:play('Church_Organ_Powerup')
            light:power_console_connected()
        end,
        on_powered_on = function(self)
            print('Lights and machinery are on now')
            sampler:play('audio/power', 'background')

            video:play(bio, 'idle/finish/game/5_1024x1280.mp4')
            video:play(main, 'idle/finish/game/3_1600x1200.mp4')

            light:power_active()
            light:enable_xray()
            zombie_arduino:mirror(true)
            magnetic_door:activated()
        end,
        on_laboratory_access = function(self)
            print('We are in Room2 now.')
        end,
        on_zombie_activated = function(self)
            print('They woke the zombie!')
            video:play(hints, 'idle/finish/intro/text_standby.mp4')
            zombie:defrost()
        end,
        on_zombie_translator = function(self)
            zombie:translate()
        end,
        on_self_destruction = function(self)
            print('It\'s the final countdown.')
            sampler:play('audio/alert', 'background')

            video:play(bio, 'idle/finish/alarm/timer_1024x1280.mp4', math.floor(os.clock() - self.start_time))
            video:play(main, 'idle/finish/alarm/timer_1600x1200.mp4', math.floor(os.clock() - self.start_time))
            video:play(hints, 'idle/finish/alarm/timer_1024x1280.mp4', math.floor(os.clock() - self.start_time))
            video:play(console, 'idle/finish/alarm/exit_pass.mp4')

            destruction_console:activated()
            light:alarms()
        end,
        on_victory = function(self)
            print('You won!')
            sampler:play('music1_left', 'background')
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

zombie = machine.create({
    events = {
        { name = 'reset', from = '*', to = 'frozen' },
        { name = 'defrost', from = 'frozen', to = 'defrosting' },
        { name = 'translate', from = 'alien_language', to = 'active' },

        { name = 'code', from = 'alien_language', to = 'gibberish' },
        { name = 'code', from = 'active', to = 'hint' },

        { name = 'ready_for_input', from = 'frozen', to = 'frozen' },
        { name = 'ready_for_input', from = 'defrosting', to = 'alien_language' },
        { name = 'ready_for_input', from = 'gibberish', to = 'alien_language' },
        { name = 'ready_for_input', from = 'hint', to = 'active' },
    },
    callbacks = {
        on_defrost = function()
            zombie_video:set_idle_files({ 'idle/finish/tv/standby.mp4' })
            zombie_video:play('idle/finish/tv/start.mp4')
        end,
        on_gibberish = function()
            zombie_video:play('idle/finish/tv/insert_translator_is.mp4')
        end,
        on_translate = function()
            print('Zombie talks!')
            zombie_video:set_idle_files({ 'idle/finish/tv/standby.mp4', 'idle/finish/tv/joke_1.mp4',  'idle/finish/tv/joke_2.mp4',  'idle/finish/tv/joke_3.mp4' })
            zombie_video:play('idle/finish/tv/hints/TRANSLATOR.mp4')
        end,
        on_code = function(self, event, from, to, code)
            local codes = {
                ['BAC1'] = function()
                    zombie_video:play('idle/finish/tv/hints/1.mp4')
                end,
                ['BAC2'] = function()
                    zombie_video:play('idle/finish/tv/hints/2.mp4')
                end,
                ['BCA1'] = function()
                    zombie_video:play('idle/finish/tv/hints/3.mp4')
                end,
                ['CAC1'] = function()
                    zombie_video:play('idle/finish/tv/hints/5.mp4')
                end,
                ['BCA2'] = function()
                    zombie_video:play('idle/finish/tv/hints/6.mp4')
                end,
                ['CBC1'] = function()
                    zombie_video:play('idle/finish/tv/hints/7.mp4')
                end,
                ['CBC2'] = function()
                    zombie_video:play('idle/finish/tv/hints/8.mp4')
                end,
                ['CBC3'] = function()
                    zombie_video:play('idle/finish/tv/hints/9.mp4')
                end,
                ['ACB1'] = function()
                    zombie_video:play('idle/finish/tv/hints/14.mp4')
                end,
                ['ACB2'] = function()
                    zombie_video:play('idle/finish/tv/hints/15.mp4')
                end,
                ['ACB3'] = function()
                    zombie_video:play('idle/finish/tv/hints/16.mp4')
                end,
                ['CBA1'] = function()
                    zombie_video:play('idle/finish/tv/hints/11.mp4')
                end,
                ['CBA2'] = function()
                    zombie_video:play('idle/finish/tv/hints/12.mp4')
                end,
                ['CBA3'] = function()
                    zombie_video:play('idle/finish/tv/hints/13.mp4')
                end,
                ['ABA1'] = function()
                    zombie_video:play('idle/finish/tv/hints/17.mp4')
                end,
                ['ABA2'] = function()
                    zombie_video:play('idle/finish/tv/hints/18.mp4')
                end,
                ['ABA3'] = function()
                    zombie_video:play('idle/finish/tv/hints/19.mp4')
                end,
                ['BCB1'] = function()
                    zombie_video:play('idle/finish/tv/hints/20.mp4')
                end,
                ['BCB2'] = function()
                    zombie_video:play('idle/finish/tv/hints/21.mp4')
                end,
                ['BCB3'] = function()
                    zombie_video:play('idle/finish/tv/hints/22.mp4')
                end,
            }

            local code_action = codes[code]
            if (code_action) then
                code_action()
            else
                print "Unknown code???"
                zombie_video:play('idle/finish/tv/code_error.mp4')
            end
        end
    }
})

REGISTER_CODE_PANEL(zombie, 20) -- VAR, timeout
REGISTER_STATES("hints", zombie)
sampler = REGISTER_SAMPLER()
zombie_arduino = REGISTER_ZOMBIE_CONTROLLER(quest)
zombie_translator = REGISTER_ZOMBIE_TRANSLATOR(quest)
zombie_video = REGISTER_VLC(zombie, zombie_arduino)
video = REGISTER_POTPLAYER()

--Fire off main initialization machine
quest:restart()
