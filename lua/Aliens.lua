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
        { name = 'open_laboratory', from = 'powered_on', to = 'laboratory_access' },
        { name = 'start_self_destruct', from = 'laboratory_access', to = 'self_destruction' },
        { name = 'win', from = 'self_destruction', to = 'victory' },
        { name = 'lose', from = 'self_destruction', to = 'failure' },
    },
    callbacks = {
        on_preparation = function(self)
            print('Resetting everything to inital states, walking around cleaning etc')

            lights:full_lights()
            lights:unlock_door()
            lights:enable_xray()

            power_console:reset()
            gestures:reset()
            boxes:reset()
            magnetic_door:reset()
            small_colbs:reset()
            destruction_console:reset()
            sample_transmitter:reset()
            sampler:reset()
        end,
        on_intro = function(self)
            print('People are entering the room')

            lights:no_power()
            lights:disable_xray()
            sampler:play('bg_slow_L')
        end,
        on_start = function(self)
            print('Game is ON!')
            lights:lock_door();

            -- TODO start timer
            sampler:play('MA_SFX_StartRamp_1')
        end,
        on_power_console_connected = function(self)
            sampler:play('Church_Organ_Powerup')
            lights:power_console_connected()
        end,
        on_powered_on = function(self)
            print('Lights and machinery are on now')
            sampler:play('ascending_organ')

            light:power_active()
            light:enable_xray()
            magnetic_door:activated()
        end,
        on_laboratory_access = function(self)
            print('We are in Room2 now.')
        end,
        on_self_destruction = function(self)
            print('It\'s the final countdown.')

            destruction_console:activated()
            light:alarms()
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
            quest:laboratory_access()
        end,
    }
})

destruction_console = rs485_node.create({
    name = 'destruction_console',
    slave_id = 7,
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'idle' },
        { name = 'activated', action_id = 2, from = 'idle', to = 'active' },
        { name = 'entered_code', triggered_by_register = 1, from = 'active', to = 'completed' },
        { name = 'force_complete', action_id = 3, from = '*', to = 'completed' },
    }
})

sample_transmitter = rs485_node.create({
    name = 'sample_transmitter',
    slave_id = '192.168.118.8',
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'idle' },
        { name = 'force_complete', action_id = 2, from = 'idle', to = 'completed' },
        { name = 'INCOMPLETE_UPLOAD', triggered_by_register = 1, from = '*', to = 'idle' },
        { name = 'EMPTY_UPLOAD', triggered_by_register = 2, from = '*', to = 'idle' },
        { name = 'COMPLETE', triggered_by_register = 3, from = 'idle', to = 'completed' },
    },
    callbacks = {
        on_completed = function()
            print('Samples are transmitted. Sound the alarm!')
            quest:start_self_destruct()
        end,
    }
})

--Fire off main initialization machine
quest:restart()
