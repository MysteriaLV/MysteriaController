local machine = require('lua/statemachine')
local rs485_node = require('lua/rs485_node')
local SECONDS_BETWEEN_HINTS = 10

sampler = REGISTER_SAMPLER()

--noinspection UnusedDef
quest = machine.create({
    events = {
        { name = 'restart', from = '*', to = 'preparation' },
        { name = 'make_intro', from = 'preparation', to = 'intro' },
        { name = 'start', from = 'intro', to = 'powered_off' },
        { name = 'power_on', from = 'powered_off', to = 'powered_on' },
        { name = 'open_door', from = 'powered_on', to = 'lab' },
        { name = 'deliver_dna', from = 'lab', to = 'aliens_coming' },
        { name = 'enable_self_destruct', from = 'aliens_coming', to = 'ready_to_self_destruct' },
        { name = 'timeout', from = { 'aliens_coming', 'ready_to_self_destruct' }, to = 'game_lost' },
        { name = 'exit', from = 'ready_to_self_destruct', to = 'game_won' },
    },
    callbacks = {
        on_preparation = function(self)
            print('Resetting everything to inital states, walking around cleaning etc')

            --            sampler.play('bg_slow_L')
            power_console:reset()
            lights:go_normal()
            magnetic_panel:reset()
            lab_door:reset()
            smoke_machine:reset()
            dna_case:reset()
            self_destruct_console:reset()
            alien_arm:reset()
            hints:reset()
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

            lights:go_normal()
            magnetic_panel:power_on()
        end,
        on_open_door = function(self)
            print('Opening the door')

            smoke_machine:turn_on()
        end,
        on_aliens_coming = function(self)
            print('Alarm! Aliens are coming!')

            lights:go_alarms()
            -- TODO sounds:countdown()
        end,
        on_ready_to_self_destruct = function(self)
            print('Self desctuct active')

            -- TODO sounds:countdown_with_self_desctruct()
        end,
        on_game_lost = function(self)
            print('Aliens are feasting on your corpses')

            lights:go_dim()
            -- TODO sounds:explosion()
        end,
        on_game_won = function(self)
            print('Aliens are found their death in fire')

            lights:go_dim()
            -- TODO sounds:happy_explosion()
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
        on_completed = function() quest:power_on() end
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
        { name = 'reset', action_id = 1, from = '*', to = 'active' },
        { name = 'something_else', action_id = 2, from = '*', to = 'active' },
        { name = 'solve', triggered_by_register = 1, from = 'active', to = 'completed' },
        { name = 'left', triggered_by_register = 2, from = 'active', to = 'active' },
        { name = 'right', triggered_by_register = 3, from = 'active', to = 'active' },
        { name = 'up', triggered_by_register = 4, from = 'active', to = 'active' },
        { name = 'down', triggered_by_register = 5, from = 'active', to = 'active' },
    },
    callbacks = {
        on_left = function() lights:go_dim() end,
        on_right = function() lights:go_alarm() end,
        on_up = function() lights:go_normal() end,
        on_down = function() lights:go_off() end,
    }
})

magnetic_panel = rs485_node.create({
    name = 'magnetic_panel',
    slave_id = '192.168.14.17',
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'powered_off' },
        { name = 'power_on', action_id = 2, from = 'powered_off', to = 'empty' },
        { name = 'put_card', triggered_by_register = 1, from = 'empty', to = 'card_present' },
        { name = 'enter_code', triggered_by_register = 2, from = 'card_present', to = 'completed' },
    },
    callbacks = {
        on_completed = function()
            lab_door:validate_card()
        end
    }
})

lab_door = rs485_node.create({
    name = 'room2_door',
    slave_id = '192.168.14.13',
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'locked' },
        { name = 'validate_card', action_id = 2, from = 'empty', to = 'card_validated' },
        { name = 'accept_card', triggered_by_register = 1, from = 'card_validated', to = 'completed' },
    },
    callbacks = {
        on_completed = function()
            quest:open_door()
        end
    }
})

smoke_machine = rs485_node.create({
    name = 'smoke_machine',
    slave_id = '192.168.14.14',
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'off' },
        { name = 'turn_on', action_id = 2, from = 'off', to = 'on' },
        { name = 'turn_off', action_id = 3, from = 'on', to = 'off' },
    }
})

------------------------------- ROOM 2 -----------------------------------------------
dna_case = rs485_node.create({
    name = 'dna_case',
    slave_id = '192.168.14.15',
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'active' },
        { name = 'deliver_dna', triggered_by_register = 1, from = 'active', to = 'completed' },
    },
    callbacks = {
        on_completed = function()
            quest:deliver_dna()
        end
    }
})

self_destruct_console = rs485_node.create({
    name = 'self_destruct_console',
    slave_id = '192.168.14.16',
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'closed' },
        { name = 'open', action_id = 2, from = 'closed', to = 'open' },
        { name = 'solve', triggered_by_register = 1, from = 'open', to = 'completed' },
    },
    callbacks = {
        on_completed = function()
            quest:enable_self_destruct()
        end
    }
})

alien_arm = rs485_node.create({
    name = 'alien_arm',
    slave_id = '192.168.14.18',
    events = {
        { name = 'reset', action_id = 1, from = '*', to = 'active' },
        { name = 'complete', triggered_by_register = 1, from = 'active', to = 'completed' },
    },
})

hints = machine.create({
    events = {
        { name = 'reset', from = '*', to = 'idle' },
        { name = 'ready_for_input', from = '*', to = 'idle' },
        { name = 'code_14', from = 'idle', to = 'alien_arm_1' },
        { name = 'code_15', from = 'idle', to = 'alien_arm_2' },
        { name = 'code_16', from = 'idle', to = 'alien_arm_3' }
    },
    callbacks = {
        on_code_14 = function(self)
            self.time_alien_arm_1 = self.time_alien_arm_1 or os.clock()
        end,
        onbeforecode_15 = function(self)
            if (os.clock() - self.time_alien_arm_1) < SECONDS_BETWEEN_HINTS then return false end
            self.time_alien_arm_2 = self.time_alien_arm_2 or os.clock()
        end,
        onbeforecode_16 = function(self)
            if (os.clock() - self.time_alien_arm_2) < SECONDS_BETWEEN_HINTS then return false end
        end,
    }
})
-- name, VAR, code length, timeout
REGISTER_CODE_PANEL("cryobox", hints, 2, 10)

--Fire off main initialization machine
quest:restart()