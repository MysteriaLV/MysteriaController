#include <SoftwareSerial.h>
#include <SimpleModbusSlaveSoftwareSerial.h>

//////////////// registers of your slave ///////////////////
enum
{
  // The first register starts at address 0
  ACTIONS,      // Always present, used for incoming actions

  // Any registered events, denoted by 'triggered_by_register' in rs485_node of Lua script, 1 and up
  QUEST_COMPLETE,


  TOTAL_ERRORS,     // leave this one, error counter
  TOTAL_REGS_SIZE   // INTERNAL: total number of registers for function 3 and 16 share the same register array
};

unsigned int holdingRegs[TOTAL_REGS_SIZE]; // function 3 and 16 register array
////////////////////////////////////////////////////////////

// Action handler. Add all your actions mapped by action_id in rs485_node of Lua script
void process_actions() {
  if (holdingRegs[ACTIONS] == 0)
    return;

  switch (holdingRegs[ACTIONS]) {
    case 1: // Activate
      digitalWrite(LED_BUILTIN, HIGH);
      break;
    case 2: // Deactivate
      digitalWrite(LED_BUILTIN, LOW);
      break;
    case 4: // Reset
      digitalWrite(LED_BUILTIN, LOW);
      break;
  }

  // Signal that action was processed
  holdingRegs[ACTIONS] = 0;
}

/* Holds current button state in register */
void buttonStatus(int reg, int pin) { // LOOP
  holdingRegs[reg] = digitalRead(pin);
}
void buttonStatus_setup(int reg, int pin) { // SETUP
  pinMode(pin, INPUT_PULLUP);
}

/* // not used: Outputs register value to pin */
void gpioWrite(int reg, int pin) {
  digitalWrite(pin, holdingRegs[reg]);
}



void setup()
{
  /* parameters(long baudrate,
                unsigned char ID,
                unsigned char transmit enable pin,    (RX: 10, TX: 11 hardcoded in code)
                unsigned int holding registers size)
  */

  modbus_configure(57600, 1, 3, TOTAL_REGS_SIZE);
  holdingRegs[ACTIONS] = 0;
  buttonStatus_setup(QUEST_COMPLETE, 4);
}


void loop()
{
  holdingRegs[TOTAL_ERRORS] = modbus_update(holdingRegs);
  process_actions();
  buttonStatus(QUEST_COMPLETE, 4);
  // not used: gpioWrite(SOME_OTHER, LED_BUILTIN);
}
