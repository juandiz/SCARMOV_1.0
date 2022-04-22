
#ifndef LSR_SENSOR_H_
#define LSR_SENSOR_H_

#include <stdint.h>

int LS_init();
uint8_t LS_read();
void LS_task();
int LS_getSignal(int pin_id);

#endif