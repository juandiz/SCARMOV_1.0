

/*
 * TRINAMIC_PORTING.c
 *
 *  Created on: Nov 8, 2018
 *      Author: pasto
 */

#include "TRINAMIC_PORTING.h"

#include "config_file.h"

#include "porting_mcu.h"

int cs_pin[MOTOR_NUMBER] = MOTORS_CS_PINS;

void tcm5160_init(){

  // Must have SPI init before

  //Enable de los drivers
  SET_PIN_OUTPUT(ENABLE_DRV_PIN);
  CLEAR_PIN(ENABLE_DRV_PIN);

  //definir el CS del motor
  for (int i=0; i<MOTOR_NUMBER;i++){
    SET_PIN_OUTPUT(cs_pin[i]);
    SET_PIN(cs_pin[i]);
  }
}

// TMC5160 SPI wrapper
void tmc5160_writeDatagram(uint8 motor, uint8 address, uint8 x1, uint8 x2, uint8 x3, uint8 x4)
{
  int value = x1;
  value <<= 8;
  value |= x2;
  value <<= 8;
  value |= x3;
  value <<= 8;
  value |= x4;

  tmc40bit_writeInt(motor, address, value);
}

void tmc5160_writeInt(uint8 motor, uint8 address, int value)
{
  tmc40bit_writeInt(motor, address, value);
}

int tmc5160_readInt(u8 motor, uint8 address)
{
    tmc40bit_readInt(motor, address);
    return tmc40bit_readInt(motor, address);
}

// General SPI decription
void tmc40bit_writeInt(u8 motor, uint8 address, int value)
{
  char tbuf[5];

  for (int i = 0; i < 5; i++)
  {
    tbuf[i] = 0;
  }

  tbuf[0] = address | 0x80;
  tbuf[1] = 0xFF & (value>>24);
  tbuf[2] = 0xFF & (value>>16);
  tbuf[3] = 0xFF & (value>>8);
  tbuf[4] = 0xFF & value;
  
  CLEAR_PIN(cs_pin[motor]);
  SPI_transfer_buff((uint8_t*)tbuf,5);
  SET_PIN(cs_pin[motor]);
}

int tmc40bit_readInt(u8 motor, uint8 address)
{
  char tbuf[5], rbuf[5];
  int value;
  // clear write bit
  value = 0;
  for (int i = 0; i < 5; i++)
  {
    tbuf[i] = 0;
    rbuf[i] = 0;
  }

	tbuf[0] = address & 0x7F;

  CLEAR_PIN(cs_pin[motor]);
  for(int i=0;i<5;i++){
    rbuf[i]=SPI_transfer_byte((uint8_t)tbuf[i]);
  }
  SET_PIN(cs_pin[motor]);

	value =rbuf[1];
	value <<= 8;
	value |= rbuf[2];
	value <<= 8;
	value |= rbuf[3];
	value <<= 8;
	value |= rbuf[4];

	return value;
}
