local machine = require('statemachine')
local rs485_node = require('rs485_node')

quest = machine.create({
    events = {
        { name = 'start', from = 'preparation', to = 'room1' },
        { name = 'unlocked_door', from = 'room1', to = 'room2' },
        { name = 'entered_code', from = 'room2', to = 'auto_destroy' },
        { name = 'failed_to_exit', from = 'auto_destroy', to = 'game_lost' },
        { name = 'managed_to_exit', from = 'auto_destroy', to = 'game_won' },
        { name = 'restart', from = { 'none', 'game_won', 'game_lost' }, to = 'preparation' },
    },
    callbacks = {
        on_preparation = function(self)
            print('Resetting everything to inital states')

            lights:full_lights()
        end,
        on_start = function(self)
            print('Game is OOOON! ')

            lights:ambient_lights()
            door:activate()
        end,
        on_unlocked_door = function(self)
            print('The unlocked the DOOR!')

            lights:focus_on_door()
            door:deactivate()

            --TODO timer lights:ambient_lights()
        end,
        on_entered_code = function(self)
            print('Code was entered! 10 seconds to leave the room!')

            lights:alarms()
        end,
    }
})
REGISTER_STATES("main_quest", quest)

lights = rs485_node.create({
    name = 'lights',
    slave_id = 1,
    actions = {
        { name = 'full_lights', action_id = 1 },
        { name = 'ambient_lights', action_id = 2 },
        { name = 'focus_on_door', action_id = 3 },
        { name = 'alarms', action_id = 4 },
    }
})

door = rs485_node.create({
    name = 'door',
    slave_id = 2,
    actions = {
        { name = 'activate', action_id = 2 },
        { name = 'deactivate', action_id = 3 },
    },
    events = {
        { name = 'door_was_unlocked', register_id = 101 }
    },
    callbacks = {
        on_door_was_unlocked = quest:unlocked_door,
    }
})

destruction_code_panel = rs485_node.create({
    name = 'destruction_code_panel',
    slave_id = 3,
    actions = {
        { name = 'activate', action_id = 2 },
        { name = 'deactivate', action_id = 3 },
    },
    events = {
        { name = 'correct_code_entered', register_id = 101 },
        { name = 'incorrect_code_entered', register_id = 102 }
    },
    callbacks = {
        on_correct_code_entered = quest:entered_code,
        on_incorrect_code_entered = function(self)
            --TODO play sound
        end,
    }
})

--Fire off main initialization machine
quest:restart()
