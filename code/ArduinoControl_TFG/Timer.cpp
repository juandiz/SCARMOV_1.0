#include "Timer.h"
#include <Arduino.h>
#include "stdint.h"

uint32_t ticks_counter = 0;

////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// weak functions to be used outside this library if needed
void __attribute__((weak)) IT_Loop_ms(){
  // this function is used to have ms ticks for temporization features
}

void __attribute__((weak)) IT_5ms(){
  // this function is used to have an extra loop that works with the reception proccess
}


////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// TIMER IMPLEMENTATIONS 
uint32_t getTicksCount(){
  return ticks_counter;
}

uint32_t setTimerLoad(uint32_t load){
  return (getTicksCount() + load);
}

int isTimerExpired(uint32_t timerLoad){
  uint32_t actual_count = getTicksCount();
  if(actual_count >= timerLoad )
    return 1;
  return 0;
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// HW SET UP FOR TIMERS
void setUP_timerHW(){
    
  GCLK->CLKCTRL.reg = GCLK_CLKCTRL_CLKEN |                 // Enable GCLK0 for TC4 and TC5
                      GCLK_CLKCTRL_GEN_GCLK0 |             // Select GCLK0 at 48MHz
                      GCLK_CLKCTRL_ID_TC4_TC5;             // Feed GCLK0 output to TC4 and TC5
  while (GCLK->STATUS.bit.SYNCBUSY);                       // Wait for synchronization

  TC5->COUNT16.CC[0].reg = 3750;                          // Set the TC4 CC0 register as the TOP value in match frequency mode
  while (TC5->COUNT16.STATUS.bit.SYNCBUSY);                // Wait for synchronization

  NVIC_SetPriority(TC5_IRQn, 0);    // Set the Nested Vector Interrupt Controller (NVIC) priority for TC4 to 0 (highest)
  NVIC_EnableIRQ(TC5_IRQn);         // Connect TC4 to Nested Vector Interrupt Controller (NVIC)

  TC5->COUNT16.INTENSET.reg = TC_INTENSET_OVF;             // Enable TC4 overflow (OVF) interrupts

  TC5->COUNT16.CTRLA.reg |= TC_CTRLA_PRESCSYNC_PRESC |     // Reset timer on the next prescaler clock
                            TC_CTRLA_PRESCALER_DIV64 |      // Set prescaler to 64, 48MHz/64 = 750KHz
                            TC_CTRLA_WAVEGEN_MFRQ |        // Put the timer TC4 into match frequency (MFRQ) mode 
                            TC_CTRLA_MODE_COUNT16;         // Set the timer to 16-bit mode      
  while (TC5->COUNT16.STATUS.bit.SYNCBUSY);                // Wait for synchronization

  TC5->COUNT16.CTRLA.bit.ENABLE = 1;                       // Enable the TC4 timer
  while (TC5->COUNT16.STATUS.bit.SYNCBUSY);                // Wait for synchronization
}

void setUP_timerIT(){
    
   GCLK->CLKCTRL.reg = GCLK_CLKCTRL_CLKEN |                 // Enable GCLK0 for TC4 and TC5
                      GCLK_CLKCTRL_GEN_GCLK0 |             // Select GCLK0 at 48MHz
                      GCLK_CLKCTRL_ID_TCC2_TC3;             // Feed GCLK0 output to TC4 and TC5
  while (GCLK->STATUS.bit.SYNCBUSY);                       // Wait for synchronization

  TC3->COUNT16.CC[0].reg = 750;                          // Set the TC4 CC0 register as the TOP value in match frequency mode
  while (TC3->COUNT16.STATUS.bit.SYNCBUSY);                // Wait for synchronization

  NVIC_SetPriority(TC3_IRQn, 1);    // Set the Nested Vector Interrupt Controller (NVIC) priority for TC4 to 0 (highest)
  NVIC_EnableIRQ(TC3_IRQn);         // Connect TC4 to Nested Vector Interrupt Controller (NVIC)

  TC3->COUNT16.INTENSET.reg = TC_INTENSET_OVF;             // Enable TC4 overflow (OVF) interrupts

  TC3->COUNT16.CTRLA.reg |= TC_CTRLA_PRESCSYNC_PRESC |     // Reset timer on the next prescaler clock
                            TC_CTRLA_PRESCALER_DIV64 |      // Set prescaler to 8, 48MHz/8 = 6MHz
                            TC_CTRLA_WAVEGEN_MFRQ |        // Put the timer TC4 into match frequency (MFRQ) mode 
                            TC_CTRLA_MODE_COUNT16;         // Set the timer to 16-bit mode      
  while (TC3->COUNT16.STATUS.bit.SYNCBUSY);                // Wait for synchronization

  TC3->COUNT16.CTRLA.bit.ENABLE = 1;                       // Enable the TC4 timer
  while (TC3->COUNT16.STATUS.bit.SYNCBUSY);                // Wait for synchronization
}

void initTimers(){
  setUP_timerHW();
  setUP_timerIT();
}

void TC3_Handler(){
    ticks_counter++;
    IT_Loop_ms();   
    TC3->COUNT16.INTFLAG.reg = TC_INTFLAG_OVF;             // Clear the OVF interrupt flag
}

void TC5_Handler(){
    IT_5ms();  
    TC5->COUNT16.INTFLAG.reg = TC_INTFLAG_OVF;             // Clear the OVF interrupt flag
}