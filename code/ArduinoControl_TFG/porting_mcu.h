#ifndef PORTING_MCU_H_
#define PORTING_MCU_H_

#include <Arduino.h>

static bool serial_active = false;

void MCU_init();
void MCU_serialPrint(char* str, bool print_line);
void SPI_transfer_buff(uint8_t* data, int size);
uint8_t SPI_transfer_byte(uint8_t byte);    
void SPI_send_receive(uint8_t * data_tx, uint8_t* data_rx, int size); 

#define PRINT_LINE(string)          Serial.println(string)
#define PRINT(string)               Serial.print(string)

#define SET_PIN_INPUT(pin_number)   pinMode(pin_number,INPUT)
#define SET_PIN_OUTPUT(pin_number)  pinMode(pin_number,OUTPUT)
#define SET_PIN(pin_number)         digitalWrite(pin_number,HIGH)
#define CLEAR_PIN(pin_number)       digitalWrite(pin_number,LOW)
#define READ_PIN(pin_number)        digitalRead(pin_number)
#define READ_AN_PIN(pin_number)     analogRead(pin_number) 

#endif