--RS485 interface functions

RS485_read_coil_latching = function(self, coilId) print("RS485_read_register_latching ", self.slaveId, coilId) end;
RS485_write_coil = function(self, coilId) print("RS485_write_coil ", self.slaveId, coilId) end;

codePanel = {
    slaveId = 1;
    isButtonPressed = function(self) RS485_read_coil(self, 2) end;
    isCodeEntered = function(self) RS485_read_coil_latching(self, 3) end;
}

alarmLights = {
    slaveId = 2;
    isButtonPressed = function(self) RS485_read_coil(self, 3) end;
    doTurnOn = function(self) RS485_write_coil(self, 5) end;
}

local machine = require('statemachine')

fsm = machine.create({
    initial = 'hungry',
    events = {
        { name = 'eat', from = 'hungry', to = 'satisfied' },
        { name = 'eat', from = 'satisfied', to = 'full' },
        { name = 'eat', from = 'full', to = 'sick' },
        { name = 'rest', from = { 'hungry', 'satisfied', 'full', 'sick' }, to = 'hungry' },
    }
})

fsm:eat()
print(fsm.current)
fsm:eat()
