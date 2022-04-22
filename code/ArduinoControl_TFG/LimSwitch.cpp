#include "LimSwitch.h"

#include "porting_mcu.h"

#include "config_file.h"

int LS_pinNumber[LS_NUMBER]       = LS_PINS_SELECTION;// define pins for LS sensors 

/*This function init the pin number pass as atribute and check if this pin is already set.
returns 1 if it goes well otherwise return 0;*/

int LS_init(){
  for(int i=0; i<LS_NUMBER;i++){
    SET_PIN_INPUT(LS_pinNumber[i]);// defined as input 
  }
  return 1;
}

/**This function retunrs the reads of each sensor in 1 byte.
Each bit corresponds to one sensor where the sensor number 0 will
be the LSB of the half word*/
uint8_t LS_read(){
  uint8_t val=0;
  for (int i=0 ; i<LS_NUMBER; i++ ){
    val = (uint8_t)((val) | (READ_PIN(LS_pinNumber[i])<<i));
  }
  return val; 
}

// this function returs the actual state of the ls sensor
int LS_getSignal(int pin_id){
  return (READ_PIN(LS_pinNumber[pin_id]));
}
