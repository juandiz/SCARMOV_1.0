
#include "frameManager.h"

/* strcpy */
#include <stdio.h>

#include "control_cmd.h"
#include "porting_mcu.h"
#include "config_file.h"

////////////////////////// SEND DATA VALUES STRUCTURE

int send_pointer_write  = 0; // pointer of send data buffer
int send_pointer_read   = 0;
int read_string_number  = 0;

typedef struct{
  char  data_string[MAX_SETRING_SIZE];
  int   size;
}SEND_dataType;

SEND_dataType send_data[MAX_SEND_BUFF];

void SEND_newString(char* data, int size){
  if(read_string_number < MAX_SEND_BUFF){
    char * new_string = send_data[send_pointer_write].data_string;
    memcpy(new_string,data,size);

    #if DEBUG_LEVEL > 2
    PRINT_LINE("----------------------- SEND FUNCTION FRAME MANAGER ----------------------------");
    PRINT("size: ");
    PRINT_LINE(size);
    PRINT("Data to send:");
    PRINT_LINE(send_data[send_pointer_write].data_string);
    PRINT_LINE("--------------------------------------------------------------------------------");
    #endif

    send_data[send_pointer_write++].size = size;
    read_string_number ++;
    if(send_pointer_write >= MAX_SEND_BUFF)
      send_pointer_write=0;
  }
}

int SEND_getNewString(char *dataout){

  int size_cpy = 0;

  if(send_pointer_read >= MAX_SEND_BUFF){
    send_pointer_read = 0;
  }
  if (read_string_number > 0){
    read_string_number --;

    #if DEBUG_LEVEL > 1
    PRINT_LINE("-------------------------------------------------------------");
    PRINT_LINE(send_data[send_pointer_read].data_string);
    #endif

    memcpy(dataout,send_data[send_pointer_read].data_string,send_data[send_pointer_read].size);
    memset(send_data[send_pointer_read].data_string,'\0',MAX_SETRING_SIZE);
    size_cpy = send_data[send_pointer_read].size;
    send_data[send_pointer_read++].size = 0;
    return size_cpy;
  }
  dataout = NULL;
  return 0; // there is no new msg
}


void  __attribute__ ((weak)) JSON_readyCallBack(){
  ;
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////// FUNCTIONS //////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

int ATDec(int ascii){
  if(ascii>='0'&& ascii<='9'){
    return (ascii-'0');
  }
  return -1;
}

int intToString(char* dataout,uint16_t value){
  int length = snprintf( NULL, 0, "%d", value );
  char* str =(char*) malloc( length + 1 );
  snprintf( str, length + 1, "%d", value );
  strcpy(dataout,str);
  free(str);
  return length;
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////// JSON MANAGEMEN //////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#define BUFF_INPU_BYTES_MAX     1000

#define VAL_SEPARATION_CHAR     ','
#define INIT_LEVEL_CHAR         '{'
#define END_LEVEL_CHAR          '}'
#define INIT_VALUE_CHAR         ':'
#define INIT_STRING_VALUE_CHAR  '"'
#define INIT_ARRAY_CHAR         '['
#define END_ARRAY_CHAR          ']'

typedef enum{
  JSON_LOOKING_START_MSG,
  JSON_READ_ERROR,
  JSON_READING_MSG
}JSON_readStringStt;

typedef struct{

  // data variables
  char                    dataInput[BUFF_INPU_BYTES_MAX];// data frame
  int                     numberOfDatavalues;// data frame size

  // json string management
  int                     JSON_counter;// pointer that increments when using readJson 
  int                     sizeOfMSG;
  int                     levelNumber;
  int                     pointerReceived;

  //Json patrser state
  JSON_readStringStt      ReadingCharState;
  int                     JSONactiveFlag = 0;

}JSON_Type;

JSON_Type jsonStringsInput;
uint32_t numberOfmsgRead = 0;

int JSON_getReadState(){
  return jsonStringsInput.ReadingCharState;
}

// This function reset the JSON struct for the reading
void resetJSONStruct(){
  jsonStringsInput.pointerReceived  = 0;
  jsonStringsInput.JSON_counter     = 0;
  jsonStringsInput.sizeOfMSG        = 0;
  memset(jsonStringsInput.dataInput,0,BUFF_INPU_BYTES_MAX);
}

// this function reads the next byte of the sringInput from JSON strcut and increase the counter
char readJSON(){
    char data=jsonStringsInput.dataInput[jsonStringsInput.JSON_counter++];
    if(jsonStringsInput.JSON_counter>=BUFF_INPU_BYTES_MAX)
      jsonStringsInput.JSON_counter=0;
    return data;
}

char readJSONoffset(uint32_t offset){
    return jsonStringsInput.dataInput[offset];
}

void JSONactiveProcess(){
  PRINT_LINE("JSON active");
  jsonStringsInput.JSONactiveFlag=1;
}

void JSONfinishProcess(){
  PRINT_LINE("JSON finish");
  jsonStringsInput.JSONactiveFlag=0;
}

int JSON_getOffsetCharValue(uint32_t init_offset, char charval){
  int dataOffset=0;
  while(readJSONoffset(init_offset++) != charval){
    if(dataOffset>BUFF_INPU_BYTES_MAX) return -1;
    }
  return init_offset;
}

int JSON_readStringValueFromOffset(uint32_t* offset, char* dataout){
  int dataValue=0;
  int size = 0;
  char data[20];
  int j = 1;

  uint32_t offcopy = *offset;

  for (int i =0;i<20;i++){
    data[i]=readJSONoffset(offcopy);
    if(data[i] == INIT_STRING_VALUE_CHAR)
      break;
    else{
      offcopy++;
      size++;
    }
  }
  memcpy((char*)dataout,data,size);// the size is calculated in char size
  *offset = offcopy;
  return size;
}

int JSON_readIntValueFromOffset(uint32_t* offset){
  int dataValue=0;
  int size = 0;
  char data[10];
  int j = 1;

  uint32_t offcopy = *offset;

  for (int i =0;i<10;i++){
    data[i]=readJSONoffset(offcopy);
    if(data[i] == VAL_SEPARATION_CHAR || data[i]== END_LEVEL_CHAR || data[i]== END_ARRAY_CHAR)
      break;
    else
      offcopy++;
    size++;
  }

  // PRINT_String("Data: ");
  // PRINT_String_ln(data);
  // PRINT_String_ln(", Size: ");
  // PRINT_Int_ln(size);

  for (int i =0;i<size;i++){
    if (data[size-i-1] != '-'){
      dataValue += ATDec(data[size-i-1])*j;
      j*=10;
    }
  }

  if (data[0] == '-')//negative number 
    dataValue = -dataValue;

  *offset = offcopy;
  return dataValue;
}

int JSON_lookForAttrInLevel(uint8_t attr_offset, int offset_init){

  char data;
  int inner_levels_count = 0;
  uint8_t leveloffset = 0;

  while(leveloffset < attr_offset){

    data = readJSONoffset(offset_init++);

    if(data == INIT_LEVEL_CHAR){
      inner_levels_count++;
    }
    if(data == END_LEVEL_CHAR){
      inner_levels_count--;
    }

    if(inner_levels_count == 1){// if we are in the same level check offset
      if(data == VAL_SEPARATION_CHAR){
        leveloffset++;
      }
    }
    if(offset_init>BUFF_INPU_BYTES_MAX) return -1;// break. Error in string
  }

  return offset_init;
}

// this function receive the main offset and the level to read the corresponding value
// @return if the value is int return the int number. Otherwise returns the values array.
// coordenates: coordenates[i*2] -> level, coordenates[i*2] ->offset in level

int JSON_readIntValueOffset(uint8_t* offsets,uint8_t level,int* dataout){
  uint32_t offset_char = 0;
  char next_data;
  int value_int = 0;
  
  // look the offset of the atributte
  for(int i=0;i<(level+1);i++){
    offset_char = JSON_lookForAttrInLevel(offsets[i],offset_char);
  }

  // look the offset of the begenning of data 
  offset_char = JSON_getOffsetCharValue(offset_char,INIT_VALUE_CHAR);

  // read next data to operate
  next_data = readJSONoffset(offset_char);

  if(next_data == INIT_STRING_VALUE_CHAR)
    return -1;// the value in this offset corresponds to an char array
  
  if(next_data == INIT_ARRAY_CHAR){ // we have an array value
    //PRINT_LINE("Integer array...");
    int datapointer = 0;
    char data;

    next_data = readJSONoffset(offset_char);

    if(next_data == INIT_STRING_VALUE_CHAR)
      return -1;// the value in this offset corresponds to an string array
  
    while(1){// read all integers
      offset_char++;
      dataout[datapointer++] = JSON_readIntValueFromOffset(&offset_char);
      data = readJSONoffset(offset_char);
      if(data == END_ARRAY_CHAR){
        //PRINT_LINE("End of array");
        break;
      }
    }
    return datapointer;// returns length of data array
  }
  else if(next_data != VAL_SEPARATION_CHAR){ // we have a single int value
    //PRINT_LINE("Single int data...");
    value_int = JSON_readIntValueFromOffset(&offset_char);
  }
  return value_int;
}

// this function receive the main offset and the level to read the corresponding value
// @return if the value is as char return the int number. Otherwise returns the char array.

int JSON_readStringValueOffset(uint8_t* offset,uint8_t level, char* dataout){
  uint32_t offset_char = 0;
  char next_data;
  int size = 0;
  int array_flag = 0;
  
  // look the offset of the atributte
  for(int i=0;i<(level+1);i++){
    offset_char = JSON_lookForAttrInLevel(offset[i],offset_char);
  }

  // look the offset of the begenning of data 
  offset_char = JSON_getOffsetCharValue(offset_char,INIT_VALUE_CHAR);

  // read next data to operate
  next_data = readJSONoffset(offset_char++);

  if(next_data == INIT_ARRAY_CHAR){

  }
  else if(next_data == INIT_STRING_VALUE_CHAR){ // we have a single int value
    //PRINT_LINE("Single string data...");
    size = JSON_readStringValueFromOffset(&offset_char,dataout);
    //PRINT_LINE("DATA: ");
    PRINT_LINE(dataout);
  }
  else
    return -1;// not an int 
  return size;
}

/*******************************************************************************************************
 This function starts to load new data to the JSON array until it finds the ending char
 */

void readNewStringInput(uint8_t* readChar, int size){
  for(int m = 0;m<size;m++){ // read all pckg
    switch(jsonStringsInput.ReadingCharState){
      case JSON_LOOKING_START_MSG:
        if(readChar[m] == INIT_LEVEL_CHAR){// init reading string. level = 1
          resetJSONStruct();  
          PRINT_LINE("-----------------------------------------------------------------------------------------------------------------------");
          PRINT_LINE("Init MSG");
          PRINT_LINE("-----------------------------------------------------------------------------------------------------------------------");
          jsonStringsInput.ReadingCharState = JSON_READING_MSG;
          jsonStringsInput.pointerReceived  = 0;
          jsonStringsInput.dataInput[jsonStringsInput.pointerReceived++] = readChar[m];
          jsonStringsInput.levelNumber++;
        }
        break;
      case JSON_READING_MSG:
        jsonStringsInput.dataInput[jsonStringsInput.pointerReceived] = readChar[m];
        if (readChar[m] == END_LEVEL_CHAR){
          jsonStringsInput.levelNumber--;
          if(jsonStringsInput.levelNumber == 0){ // if we have read all the msg we start the parsing proccess 
          
            jsonStringsInput.sizeOfMSG = jsonStringsInput.pointerReceived;
            jsonStringsInput.ReadingCharState = JSON_READING_MSG;

            JSONactiveProcess();
            JSON_readyCallBack();
            PRINT("Mesage number:");
            PRINT_LINE(numberOfmsgRead++);
            JSONfinishProcess();
            // PRINT_LINE("-------------------------------------------------------");
            // PRINT_LINE(jsonStringsInput.pointerReceived);
            // PRINT_LINE("-------------------------------------------------------");

            jsonStringsInput.pointerReceived=0;
            jsonStringsInput.levelNumber = 0;
            jsonStringsInput.ReadingCharState = JSON_LOOKING_START_MSG;
          }
        }
        else{
          if (readChar[m] == INIT_LEVEL_CHAR)
            jsonStringsInput.levelNumber++;// we have another level
          jsonStringsInput.ReadingCharState = JSON_READING_MSG;
        }
        jsonStringsInput.pointerReceived++;
        if (jsonStringsInput.pointerReceived >= BUFF_INPU_BYTES_MAX){
          PRINT_LINE("-----------------------------------------------------------------------------------------------------------------");
          PRINT_LINE(" BUFFER OVERFLOW");
          PRINT_LINE("-----------------------------------------------------------------------------------------------------------------");
          jsonStringsInput.ReadingCharState = JSON_LOOKING_START_MSG;
          jsonStringsInput.pointerReceived = 0;
        }
        break;
      default:
        jsonStringsInput.pointerReceived=0;
        jsonStringsInput.ReadingCharState = JSON_LOOKING_START_MSG;
        break;
   }
  }
  jsonStringsInput.pointerReceived=0;
  jsonStringsInput.ReadingCharState = JSON_LOOKING_START_MSG;
}
