local machine = require('lua/statemachine')
local rs485_node = require('lua/rs485_node')

local GAME_TIME_MAX = 3600

local DISPLAY_MAIN = 1
local DISPLAY_CIRCUIT = 2
local DISPLAY_HINTS = 3
local DISPLAY_BIO = 6
local DISPLAY_CONSOLE = 5

local LANGUAGE = 'ru'

--noinspection UnusedDef
quest = machine.create({
    events = {
        { name = 'restart', from = '*', to = 'preparation' },
        { name = 'make_intro', from = 'preparation', to = 'intro' },
        { name = 'start', from = 'intro', to = 'powered_off' },
        { name = 'power_on', from = 'powered_off', to = 'powered_on' },
        { name = 'open_laboratory', from = 'powered_on', to = 'laboratory_access' },
        { name = 'process_dna_samples', from = 'laboratory_access', to = 'destruction_console_access' },
        { name = 'start_self_destruct', from = 'destruction_console_access', to = 'self_destruction' },
        { name = 'win', from = 'self_destruction', to = 'victory' },
        { name = 'lose', from = { 'powered_on', 'laboratory_access', 'destruction_console_access', 'self_destruction', }, to = 'failure' },
    },
    callbacks = {
        on_preparation = function(self)
            print('Resetting everything to inital states, walking around cleaning etc')
            self.start_time = os.clock();

            language:reset()
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

            zombie_video:set_idle_files({ 'video/prepare/1.jpg' })
            zombie_video:start()

            video:play(DISPLAY_MAIN, 'video/prepare/3.jpg')
            video:play(DISPLAY_CIRCUIT, 'video/prepare/4.jpg')
            video:play(DISPLAY_HINTS, 'video/prepare/6.jpg')
            video:play(DISPLAY_BIO, 'video/prepare/2.jpg')
            video:play(DISPLAY_CONSOLE, 'video/prepare/5.jpg')
        end,
        on_intro = function(self)
            print('People are entering the room')

            light:no_power()
            light:disable_xray()
            zombie_arduino:mirror(false)
            sampler:play('audio/intro', 'background')

            zombie_video:set_idle_files({ 'video/zombie_sleeping.mp4' })

            video:play(DISPLAY_MAIN, 'video/displays/1600x1200.mp4')
            video:play(DISPLAY_CIRCUIT, 'video/table.jpg')
            video:play(DISPLAY_HINTS, 'video/displays/text_standby.mp4')
            video:play(DISPLAY_BIO, 'video/displays/1024x1280.mp4')
            video:play(DISPLAY_CONSOLE, 'video/displays/1280x1024.mp4')
        end,
        on_start = function(self)
            print('Game is ON!')
            light:lock_door();

            video:play(DISPLAY_HINTS, 'video/' .. LANGUAGE .. '/room1_hints.mp4')
            self.start_time = os.clock();
        end,
        on_power_console_connected = function(self)
            sampler:play('audio/' .. LANGUAGE .. '/power_cable_connected')
            light:power_console_connected()
            -- 20 50 90 70
        end,
        on_powered_on = function(self)
            print('Lights and machinery are on now')
            sampler:play('audio/power', 'background')
            sampler:play('audio/' .. LANGUAGE .. '/system_power_on')

            video:play(DISPLAY_BIO, 'video/displays/5_1024x1280.mp4')
            video:play(DISPLAY_MAIN, 'video/displays/3_1600x1200.mp4')

            zombie_arduino:mirror(true)
            magnetic_door:activated()
            light:power_active()
        end,
        on_laboratory_access = function(self)
            print('We are in Room2 now.')
        end,
        on_zombie_activated = function(self)
            print('They woke the zombie!')
            video:play(DISPLAY_HINTS, 'video/displays/text_standby.mp4')
            zombie:defrost()
        end,
        on_zombie_translator = function(self)
            zombie:translate()
        end,
        on_destruction_console_access = function(self)
            print('Opening destruction console.')
            destruction_console:activated()
            sampler:play('audio/' .. LANGUAGE .. '/data_transmitted')
        end,
        on_self_destruction = function(self)
            print('It\'s the final countdown.')
            sampler:play('audio/alert', 'background')

            video:play(DISPLAY_BIO, 'video/alarm/timer_1024x1280.mp4', math.floor(os.clock() - self.start_time))
            video:play(DISPLAY_MAIN, 'video/alarm/timer_1600x1200.mp4', math.floor(os.clock() - self.start_time))
            video:play(DISPLAY_HINTS, 'video/alarm/timer_1024x1280.mp4', math.floor(os.clock() - self.start_time))
            video:play(DISPLAY_CONSOLE, 'video/alarm/exit_pass.mp4')

            light:alarms()
            light:disable_xray()
        end,
        on_victory = function(self)
            print('You won!')
            sampler:play('audio/intro', 'background')
            light:full_lights()
            light:unlock_door()
        end,
        on_failure = function(self)
            print('You\'ve lost!')
            sampler:reset()
            sampler:play('audio/LongExplosion')
            light:off()
            light:unlock_door()
        end,
        on_tick = function(self)
            if (math.floor(os.clock() - self.start_time) > GAME_TIME_MAX) then
                print('Time\'s up')
                self:lose()
            end
        end,
        get_game_time = function(self)
            return math.floor(os.clock() - self.start_time)
        end
    }
})

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

boxes = rs485_node.create({
    name = 'boxes',
    slave_id = 2,
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'idle' },
        { name = 'minor_failure', triggered_by_register = 1, from = 'idle', to = 'idle' },
        { name = 'major_failure', triggered_by_register = 2, from = 'idle', to = 'idle' },
        { name = 'complete', triggered_by_register = 3, action_id = 2, from = '*', to = 'completed' },
    },
    callbacks = {
        on_completed = function()
            sampler:play('audio/' .. LANGUAGE .. '/finish_boxes')
        end,
    }
})

------------------------------- ROOM 2 -----------------------------------------------
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
        { name = 'lab_light_on', action_id = 11, from = '*', to = 'idle' },
        { name = 'off', action_id = 12, from = '*', to = 'idle' },
    },
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
            quest:start_self_destruct()
        end,
    }
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
            print('Samples are transmitted.')
            quest:process_dna_samples()
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
        on_defrosting = function()
            zombie_video:set_idle_files({ 'video/zombie_standby.mp4' })
            zombie_video:play('video/zombie_defrosting.mp4')
        end,
        on_gibberish = function()
            zombie_video:play('video/zombie_translator_missing.mp4')
        end,
        on_translate = function()
            print('Zombie talks!')
            zombie_video:set_idle_files({ 'video/zombie_standby.mp4', 'video/' .. LANGUAGE .. '/idle/joke_1.mp4', 'video/' .. LANGUAGE .. '/idle/joke_2.mp4', 'video/' .. LANGUAGE .. '/idle/joke_3.mp4' })
            zombie_video:play('video/' .. LANGUAGE .. '/translator_ready.mp4')
        end,
        on_hint = function(self, event, from, to, code)
            local codes = {
                ['AAA1'] = function()
                    light:enable_xray()
                    zombie_video:play('video/' .. LANGUAGE .. '/AAA1.mp4')
                end,
                ['BBB1'] = function()
                    light:lab_light_on()
                    zombie_video:play('video/' .. LANGUAGE .. '/BBB1.mp4')
                end,
                ['BAC1'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/BAC1.mp4')
                end,
                ['BAC2'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/BAC2.mp4')
                end,
                ['BCA1'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/BCA1.mp4')
                end,
                ['CAC1'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/CAC1.mp4')
                end,
                ['BCA2'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/BCA2.mp4')
                end,
                ['CBC1'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/CBC1.mp4')
                end,
                ['CBC2'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/CBC2.mp4')
                end,
                ['CBC3'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/CBC3.mp4')
                end,
                ['ACB1'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/ACB1.mp4')
                end,
                ['ACB2'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/ACB2.mp4')
                end,
                ['ACB3'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/ACB3.mp4')
                end,
                ['CBA1'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/CBA1.mp4')
                end,
                ['CBA2'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/CBA2.mp4')
                end,
                ['CBA3'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/CBA3.mp4')
                end,
                ['ABA1'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/ABA1.mp4')
                end,
                ['ABA2'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/ABA2.mp4')
                end,
                ['ABA3'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/ABA3.mp4')
                end,
                ['BCB1'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/BCB1.mp4')
                end,
                ['BCB2'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/BCB2.mp4')
                end,
                ['BCB3'] = function()
                    zombie_video:play('video/' .. LANGUAGE .. '/BCB3.mp4')
                end,
                ['31'] = function()
                    -- 3175
                    zombie_video:play('video/' .. LANGUAGE .. '/31_exit_code.mp4')
                end,
            }

            local code_action = codes[code]
            if (code_action) then
                code_action()
            else
                print "Unknown code???"
                zombie_video:play('video/' .. LANGUAGE .. '/code_error.mp4')
            end
        end
    }
})

language = machine.create({
    events = {
        { name = 'reset', from = '*', to = 'russian' },
        { name = 'set_russian', from = '*', to = 'russian' },
        { name = 'set_latvian', from = '*', to = 'latvian' },
        { name = 'set_english', from = '*', to = 'english' },
    },
    callbacks = {
        on_russian = function()
            LANGUAGE = 'ru'
        end,
        on_latvian = function()
            LANGUAGE = 'lv'
        end,
        on_english = function()
            LANGUAGE = 'en'
        end,
    }
})

REGISTER_STATES("main_quest", quest)
REGISTER_STATES("hints", zombie)
REGISTER_CODE_PANEL(zombie, 7) -- VAR, timeout
sampler = REGISTER_SAMPLER()
zombie_arduino = REGISTER_ZOMBIE_CONTROLLER(quest)
zombie_translator = REGISTER_ZOMBIE_TRANSLATOR(quest)
zombie_video = REGISTER_VLC(zombie, zombie_arduino)
video = REGISTER_POTPLAYER()

--Fire off main initialization machine
quest:restart()
