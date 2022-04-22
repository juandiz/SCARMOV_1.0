
#ifndef DISPLAY_H_
#define DISPLAY_H_

#include "stdint.h"

int display_init();
void display_clear();
void display_draw_line(uint16_t x_0, uint16_t y_0,uint16_t x_1, uint16_t y_1);
void display_println(uint16_t x,uint16_t y,char* text, int size);
void display_scroll(int direction);
void display_stop_scroll();

#endif