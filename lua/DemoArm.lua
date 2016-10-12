local machine = require('lua/statemachine')
local rs485_node = require('lua/rs485_node')

--noinspection UnusedDef
quest = machine.create({
    events = {
        { name = 'restart', from = '*', to = 'preparation' },
        { name = 'make_intro', from = 'preparation', to = 'intro' },
        { name = 'start', from = 'intro', to = 'powered_off' },
        { name = 'power_on', from = 'powered_off', to = 'powered_on' },
        { name = 'open_door', from = 'powered_on', to = 'room2' },
    },
    callbacks = {
        on_preparation = function(self)
            print('Resetting everything to inital states, walking around cleaning etc')

            lights:go_normal()
            power_console:reset()
            alien_arm:reset()

            quest.card_is_valid = False
        end,
        on_intro = function(self)
            print('People are entering the room')

            lights:go_dim()
        end,
        on_start = function(self)
            print('Game is ON!')

            -- TODO start timer
        end,
        on_powered_on = function(self)
            print('Lights and machinery are on now')

            -- TODO start timer
        end,
    }
})
REGISTER_STATES("main_quest", quest)


power_console = rs485_node.create({
    name = 'power_console',
    slave_id = 1,
    initial = 'inactive',
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'disconnected' },
        { name = 'connect', triggered_by_register = 1, action_id = 2, from = 'disconnected', to = 'powered_off' },
        { name = 'power_on', triggered_by_register = 2, from = 'powered_off', to = 'completed' },
    },
    callbacks = {
        on_completed = function() quest:power_on() end
    }
})

lights = rs485_node.create({
    name = 'lights',
    slave_id = 2,
    events = {
        { name = 'go_dim', action_id = 1, from = '*', to = 'dimmed' },
        { name = 'go_normal', action_id = 2, from = '*', to = 'normal' },
        { name = 'go_alarms', action_id = 3, from = '*', to = 'alarms' },
    },
})

--room2_door = rs485_node.create({
--    name = 'room2_door',
--    slave_id = 3,
--})
--
--smoke_machine = rs485_node.create({
--    name = 'smoke_machine',
--    slave_id = 4,
--})
--
--dna_case = rs485_node.create({
--    name = 'dna_case',
--    slave_id = 5,
--})
--
--self_destruct_console = rs485_node.create({
--    name = 'self_destruct_console',
--    slave_id = 6,
--})

magnetic_panel = rs485_node.create({
    name = 'magnetic_panel',
    slave_id = 7,
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'empty' },
        { name = 'put_card', triggered_by_register = 1, from = 'empty', to = 'card_present' },
        { name = 'enter_code', triggered_by_register = 2, from = 'card_present', to = 'completed' },
    },
    callbacks = {
        on_completed = function() quest.card_is_valid = True end
    }
})

alien_arm = rs485_node.create({
    name = 'alien_arm',
    slave_id = 8,
    initial = 'inactive',
    events = {
        { name = 'activate', action_id = 1, from = 'inactive', to = 'active' },
        { name = 'deactivate', action_id = 2, from = { 'active', 'completed' }, to = 'inactive' },
        { name = 'complete', triggered_by_register = 1, from = 'active', to = 'completed' },
        { name = 'reset', action_id = 4, from = '*', to = 'inactive' },
    },
    callbacks = {
        on_complete = function() quest:solved_alien_arm() end
    }
})

--Fire off main initialization machine
quest:restart()

