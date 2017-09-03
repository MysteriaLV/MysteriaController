local machine = require('lua/statemachine')
local rs485_node = require('lua/rs485_node')

sampler = REGISTER_SAMPLER()

--noinspection UnusedDef
quest = machine.create({
    events = {
        { name = 'restart', from = '*', to = 'preparation' },
        { name = 'make_intro', from = 'preparation', to = 'intro' },
        { name = 'start', from = 'intro', to = 'powered_off' },
        { name = 'power_on', from = 'powered_off', to = 'powered_on' },
    },
    callbacks = {
        on_preparation = function(self)
            print('Resetting everything to inital states, walking around cleaning etc')

            lights:go_max()
            relay_box:unlock_exit_door()
            relay_box:enable_top_lights1()
            relay_box:enable_top_lights2()
            power_console:reset()
            boxes:reset()
            sampler:reset()
        end,
        on_intro = function(self)
            print('People are entering the room')

            lights:go_dim()
            sampler:play('bg_slow_L')
            relay_box:disable_top_lights1()
            relay_box:disable_top_lights2()
        end,
        on_start = function(self)
            print('Game is ON!')
            relay_box:lock_exit_door();

            -- TODO start timer
            sampler:play('Kalinin1')
        end,
        on_power_console_connected = function(self)
            sampler:play('Kalinin2')
        end,
        on_powered_on = function(self)
            print('Lights and machinery are on now')
            sampler:play('Kalinin3')

            relay_box:enable_top_lights1()
        end,
        on_second_room_opened = function(self)
            print('We are in Room2 now. Sprint2')

            relay_box:activate_smoke()
            relay_box:enable_top_lights2()
            lights:go_normal()
            relay_box:unlock_exit_door()
        end,
    }
})
REGISTER_STATES("main_quest", quest)

------------------------------- ROOM 1 -----------------------------------------------

power_console = rs485_node.create({
    name = 'power_console',
    slave_id = '192.168.14.11',
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'disconnected' },
        { name = 'connect', triggered_by_register = 1, action_id = 2, from = 'disconnected', to = 'powered_off' },
        { name = 'power_on', triggered_by_register = 2, from = 'powered_off', to = 'completed' },
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

lights = rs485_node.create({
    name = 'lights',
    slave_id = 1,
    events = {
        { name = 'go_dim', action_id = 1, from = '*', to = 'dimmed' },
        { name = 'go_normal', action_id = 2, from = '*', to = 'normal' },
        { name = 'go_alarms', action_id = 3, from = '*', to = 'alarms' },
        { name = 'go_off', action_id = 4, from = '*', to = 'off' },
        { name = 'go_max', action_id = 5, from = '*', to = 'normal' },
        { name = 'power_console_connected', action_id = 6, from = 'dimmed', to = 'dimmed' },
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
        on_left = function() lights:go_dim() end,
        on_right = function() lights:go_alarm() end,
        on_up = function() lights:go_normal() end,
        on_down = function() lights:go_off() end,
        on_completed = function()
            print('Gestures are resolved')
        end,
    }
})

relay_box = rs485_node.create({
    name = 'relay_box',
    slave_id = 4,
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'idle' },
        { name = 'enable_top_lights1', action_id = 2, from = '*', to = 'idle' },
        { name = 'enable_top_lights2', action_id = 3, from = '*', to = 'idle' },
        { name = 'disable_top_lights1', action_id = 4, from = '*', to = 'idle' },
        { name = 'disable_top_lights2', action_id = 5, from = '*', to = 'idle' },
        { name = 'unlock_exit_door', action_id = 6, from = '*', to = 'idle' },
        { name = 'lock_exit_door', action_id = 7, from = '*', to = 'idle' },
        { name = 'activate_smoke', action_id = 8, from = '*', to = 'idle' },
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
        on_opened = function()
            print('People entered second room')
            quest:on_second_room_opened()
        end,
    }
})

--Fire off main initialization machine
quest:restart()
