
#ifndef TIMER_H_
#define TIMER_H_

#include "stdint.h"

void IT_Loop_ms(); // weak function called by OVF interruot of timer
void check_HW();
void initTimers();
uint32_t getTicksCount();
uint32_t setTimerLoad(uint32_t load);
int isTimerExpired(uint32_t timerLoad);

#endif // TIMER_H_