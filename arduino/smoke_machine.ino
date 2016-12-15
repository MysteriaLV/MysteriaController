#include <SoftwareSerial.h>
#include <SimpleModbusSlaveSoftwareSerial.h>

//////////////// registers of SMOKE_MACHINE ///////////////////
enum
{
  // The first register starts at address 0
  ACTIONS,      // Always present, used for incoming actions

  // Any registered events, denoted by 'triggered_by_register' in rs485_node of Lua script, 1 and up
  
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
    case 1 : // Put here code for Reset
      Serial.println("[Reset] action fired");
      // gpioWrite(1, LED_BUILTIN);
      break;
    case 2 : // Put here code for Turn_on
      Serial.println("[Turn_on] action fired");
      // gpioWrite(1, LED_BUILTIN);
      break;
    case 3 : // Put here code for Turn_off
      Serial.println("[Turn_off] action fired");
      // gpioWrite(1, LED_BUILTIN);
      break;
    }

  // Signal that action was processed
  holdingRegs[ACTIONS] = 0;
}

// Just debug functions for easy testing. Won't be used probably
/* Holds current button state in register */
void buttonStatus(int reg, int pin) { // LOOP
  holdingRegs[reg] = digitalRead(pin);
}
void buttonStatus_setup(int reg, int pin) { // SETUP
  pinMode(pin, INPUT_PULLUP);
}

/* Outputs register value to pin */
void gpioWrite(int reg, int pin) {
  digitalWrite(pin, holdingRegs[reg]);
}
/////////////////////////////////////////////////////////////////

void setup()
{
  Serial.begin(115200);
  Serial.println("Serial ModBus Slave SMOKE_MACHINE:4 for lua/Aliens.lua");

  /* parameters(long baudrate,
                unsigned char ID,
                unsigned char transmit enable pin,    (RX: 10, TX: 11 hardcoded in code)
                unsigned int holding registers size)
  */

  modbus_configure(57600, 4, 3, TOTAL_REGS_SIZE);
  holdingRegs[ACTIONS] = 0;
  // Sample calls
  // buttonStatus_setup(, <buttonPin>);
}


void loop()
{
  holdingRegs[TOTAL_ERRORS] = modbus_update(holdingRegs);
  process_actions();

  // Notify main console of local events
  

  // Sample calls
  // buttonStatus(, <buttonPin>);
}