#include "porting_mcu.h"
#include "display_if.h"
#include "config_file.h"
#include <SPI.h>

void MCU_init(){

    // Init SPI communication
    SPI.begin();

    // try to init display
    if(display_init()){
        display_println(0,0,"Display Init ... ",1);
        delay(5000);
        display_clear();
    }

    int serial_tries_count = 0;
    // try to init serial
    Serial.begin(SERIAL_BOUD_RATE); 
    
    while(true){
        if(serial_tries_count >= SERIAL_INIT_COUNT){
            serial_active = false;
            break;
        }
        if(Serial){ 
            display_println(0,10,"Serial init ... ",1);
            serial_active = true;
            break;
        }
        display_clear();
        display_println(0,0,(char*)&serial_tries_count,1);
        serial_tries_count++;
        delay(1000); //
    }

    if(!serial_active) display_println(0,10,"Serial error ... ",1);
    delay(2000);
    display_clear();
}
void MCU_serialPrint(char* str, bool print_line){
    if(serial_active){
        if(print_line){
            Serial.println(str);
        }
        Serial.print(str);
    }
}

void SPI_transfer_buff(uint8_t* data, int size){
    SPI.transfer(data,size);
}

uint8_t SPI_transfer_byte(uint8_t byte){
    return SPI.transfer(byte);
}

void SPI_send_receive(uint8_t * data_tx, uint8_t* data_rx, int size){
    for(int i=0;i<size;i++){
        data_rx[i]=SPI_transfer_byte(data_tx[i]);
    }
}