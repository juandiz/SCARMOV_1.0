#ifndef FSR_H
#define FSR_H

#include "stdint.h"

void FSR_init();
void FSR_task();
float FSR_getForce_N(int FSR_id);

#endif