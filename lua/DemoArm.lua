local machine = require('lua/statemachine')
local rs485_node = require('lua/rs485_node')

--noinspection UnusedDef
quest = machine.create({
    events = {
        { name = 'start', from = 'preparation', to = 'room1' },
        { name = 'solved_alien_arm', from = 'room1', to = 'game_won' },
        { name = 'restart', from = '*', to = 'preparation' },
    },
    callbacks = {
        on_preparation = function(self)
            print('Resetting everything to inital states')

            alien_arm:reset()
        end,
        on_start = function(self)
            print('Game is OOOON! ')

            alien_arm:activate()
        end,
        on_solved_alien_arm = function(self)
            print('Arm solved, thanks')

            alien_arm:deactivate()
        end,
    }
})
REGISTER_STATES("main_quest", quest)

alien_arm = rs485_node.create({
    name = 'alien_arm',
    slave_id = 1,
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

