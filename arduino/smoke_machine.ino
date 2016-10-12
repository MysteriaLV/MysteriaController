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
    case 1 : // Reset
      // Put here code for Reset
      break;
    case 2 : // Turn_on
      // Put here code for Turn_on
      break;
    case 3 : // Turn_off
      // Put here code for Turn_off
      break;
    }

  // Signal that action was processed
  holdingRegs[ACTIONS] = 0;
}

void setup()
{
  /* parameters(long baudrate,
                unsigned char ID,
                unsigned char transmit enable pin,    (RX: 10, TX: 11 hardcoded in code)
                unsigned int holding registers size)
  */

  modbus_configure(57600, 4, 3, TOTAL_REGS_SIZE);
  holdingRegs[ACTIONS] = 0;
  }


void loop()
{
  holdingRegs[TOTAL_ERRORS] = modbus_update(holdingRegs);
  process_actions();

  // Notify main console of local events
  
}