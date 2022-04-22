
// CONFIG
#include "config_file.h"

//Librerias
#include "Timer.h"
#include "FSR.h"
#include "LimSwitch.h"
#include "control_cmd.h"
#include "status_task.h"
#include "userMotorControl.h"
#include "wifi_if.h"

// debug
#include "porting_mcu.h"

//variables de tiempo
uint32_t control_timer  = 0;
uint32_t status_timer   = 0;
uint32_t fsr_timer      = 0;

bool connection_state = false;

void setup() {
  // put your setup code here, to run once:
  MCU_init();
  WIFI_init();
  MOTOR_init(); 
  initTimers();
  FSR_init();
  CONTROL_init();
  LS_init();
}

void loop() {
  if (WIFI_loop()){// this is the principal thas that has priority 

    if(!connection_state){
      connection_state = true;
      init_connection_message();
    }

    // read sensors and state 
    if (isTimerExpired(control_timer)){
      control_timer = setTimerLoad(CMD_TASK_DELAY);
      CONTROL_loop();
    }
    // read sensors and state 
    if (isTimerExpired(status_timer)){
      status_timer = setTimerLoad(STATUS_TASK_DELAY);
      state_function();
    }
    // read sensors and state 
    if (isTimerExpired(fsr_timer)){
      FSR_task();
      fsr_timer = setTimerLoad(FSR_TASK_DELAY);
    }
  }
  else if (connection_state){
    connection_state = false;
  }
}
