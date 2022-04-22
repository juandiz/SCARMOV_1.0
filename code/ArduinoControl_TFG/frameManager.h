#ifndef FRAME_MAN_H_
#define FRAME_MAN_H

#include "stdint.h"

//********************************************************************************************************************
//***  Este archivo se encarga de gestionar las cadenas de texto y convertirlas a valores numericos:
//      Tambien lee paquetes JSON y devuelve el valor por corrdenada del mismo, sea array o no. ******************
//********************************************************************************************************************

int ATDec(int ascii);                          //Convierte el valor en ASCII de la cadena a un numero decimal
int intToString(char* dataout,uint16_t value);

// Porting layer
int JSON_getReadState();
int JSON_readIntValueOffset(uint8_t* offsets,uint8_t level,int* dataout);
int JSON_readStringValueOffset(uint8_t* offset,uint8_t level,char* dataout);
void readNewStringInput(uint8_t* readChar,int size); 
int isFrameManagerActive();
int isReadOk();

// write data strunct 
void SEND_newString(char* data, int size);
int SEND_getNewString(char *dataout);

#endif