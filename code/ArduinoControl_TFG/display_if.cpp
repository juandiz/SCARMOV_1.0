#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "display_if.h"

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 32 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
// The pins for I2C are defined by the Wire-library. 
// On an arduino UNO:       A4(SDA), A5(SCL)
// On an arduino MEGA 2560: 20(SDA), 21(SCL)
// On an arduino LEONARDO:   2(SDA),  3(SCL), ...
#define OLED_RESET     4 // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

bool display_active = false;

int display_init(){
     // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    return 0; // error
  }
  display.clearDisplay();
  display_active = true;
  return 1;
}

void display_clear(){
  if (display_active) {
    display.clearDisplay(); 
  }
}

void display_draw_line(uint16_t x_0, uint16_t y_0,uint16_t x_1, uint16_t y_1){
  if (display_active) {
    display.drawLine(x_0, y_0,x_1, y_1,SSD1306_WHITE);
    display.display(); // Update screen with each newly-drawn line
  }
}

void display_scroll(int direction){
  if (display_active) {
    if (!direction)
      display.startscrollleft(0,7);
    else
      display.startscrollright(0,7);
  }
}

void display_stop_scroll(){
  if (display_active) {
    display.stopscroll();
  }
}

void display_println(uint16_t x,uint16_t y,char* text, int size){ 
  if (display_active) {
    display.setCursor(x,y);
    display.setTextSize(size);
    display.setTextColor(WHITE);
    display.println(text);
    display.display();
  }
}