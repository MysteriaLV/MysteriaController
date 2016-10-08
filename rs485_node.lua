local node = {}
node.__index = node

local function call_handler(handler, params)
    if handler then
        return handler(unpack(params))
    end
end

local function create_action(name, slave_id, action_id)
    local function action(self, ...)
        print(self.name .. ":" .. name, slave_id, action_id)
    end
    return action
end

local function create_transition(name)
    local can, to, from, params

    local function transition(self, ...)
        if self.asyncState == NONE then
            can, to = self:can(name)
            from = self.current
            params = { self, name, from, to, ... }

            if not can then return false end
            self.currentTransitioningEvent = name

            local beforeReturn = call_handler(self["onbefore" .. name], params)
            local leaveReturn = call_handler(self["onleave" .. from], params)

            if beforeReturn == false or leaveReturn == false then
                return false
            end

            self.asyncState = name .. "WaitingOnLeave"

            if leaveReturn ~= ASYNC then
                transition(self, ...)
            end

            return true
        elseif self.asyncState == name .. "WaitingOnLeave" then
            self.current = to

            local enterReturn = call_handler(self["onenter" .. to] or self["on" .. to], params)

            self.asyncState = name .. "WaitingOnEnter"

            if enterReturn ~= ASYNC then
                transition(self, ...)
            end

            return true
        elseif self.asyncState == name .. "WaitingOnEnter" then
            call_handler(self["onafter" .. name] or self["on" .. name], params)
            call_handler(self["onstatechange"], params)
            self.asyncState = NONE
            self.currentTransitioningEvent = nil
            return true
        else
            if string.find(self.asyncState, "WaitingOnLeave") or string.find(self.asyncState, "WaitingOnEnter") then
                self.asyncState = NONE
                transition(self, ...)
                return true
            end
        end

        self.currentTransitioningEvent = nil
        return false
    end

    return transition
end

local function add_to_map(map, event)
    if type(event.from) == 'string' then
        map[event.from] = event.to
    else
        for _, from in ipairs(event.from) do
            map[from] = event.to
        end
    end
end

function node.create(options)

    local my_node = {}
    setmetatable(my_node, node)

    my_node.slave_id = options.slave_id
    my_node.name = options.name
    my_node.actions = {}

    for _, action in ipairs(options.actions or {}) do
        local name = action.name
        my_node[name] = my_node[name] or create_action(name, my_node.slave_id, action.action_id)
        --        my_node.events[name] = my_node.events[name] or { map = {} }
        --        add_to_map(my_node.events[name].map, action)
    end

    for name, callback in pairs(options.callbacks or {}) do
        my_node[name] = callback
    end

    return my_node
end

return node