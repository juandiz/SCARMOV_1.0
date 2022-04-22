
#include "control_cmd.h"
/* strcpy */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "stdint.h"
#include "frameManager.h"
#include "Timer.h"
#include "LimSwitch.h"

#include "porting_mcu.h"
#include "userMotorControl.h"

#include "status_task.h"

#include "config_file.h"

#define   CONTROL_RESET_MOTORS    5000
#define   CONTROL_VELOCITY_CMD    5004
#define   CONTROL_POSITION_CMD    5002
#define   CONTROL_ARRAY_CMD       5008
#define   CONTROL_EMER_STOP       5005
#define   CONTROL_SET_HOME        5006
#define   CONTROL_ROBOT_NAME      5007
#define   CONTROL_CONNECTION      5010
#define   MOTOR_DISABLE           5011
#define   MOTOR_ENABLE            5012
#define   SET_ACTUAL_POS          5020
#define   SET_CURRENT_REG         5030

typedef enum{
    CONTROL_BUSY_LOADING,
    CONTROL_FREE_LOADING
}CONTROL_loadState;

typedef enum{
    CONTROL_BUFF_FULL,
    CONTROL_BUFF_EMPTY,
    CONTROL_BUFF_LOADED
}CONTROL_buffState;

typedef struct{
    int                     cmd;
    int                     control_motors_id[MOTOR_NUMBER];// array of motors to be controled
    uint8_t                 motor_number;
    int                     dataValues[MAX_DATA_VALUES];
    uint32_t                size;
}CONTROL_packageStruct;

typedef struct{
    char                    robotName[20];
    int                     motor_pos[MOTOR_NUMBER];
    int                     motor_target_pos[MOTOR_NUMBER];
    int                     motor_last_target_pos[MOTOR_NUMBER];
    uint32_t                timer_motor[MOTOR_NUMBER];// velocity command is timed
    uint32_t                control_timer;// used in case of not moving
    int                     total_movement[MOTOR_NUMBER];// get the number of motors that have completed any command

    //packages management
    CONTROL_packageStruct   package[MAX_PACKAGE_NUMBER];// connection variables to load the package 

    // reading data values variables
    int                     read_dataval_pointer[MOTOR_NUMBER];// each motor could have diferen reding velocities

    // buffer packages management
    CONTROL_loadState       loadState;
    CONTROL_buffState       buffState;
    int                     packagesWritePointer;
    int                     packagesReadPointer;
    uint32_t                timer_tout;
    int                     tout_init;
    int                     buff_length; // number of data in buffer
}CONTROL_typeDef;

CONTROL_typeDef CONTROL;// management of all data receive as a circular buffer

// variables coordenates for json reading 
uint8_t command_coord[4]    = {0}; // 
uint8_t mnumber_coord[4]    = {1}; //
uint8_t values_coord[4]     = {2}; // 
uint8_t rname_coord[4]      = {1}; // 

///////////////////////////////////////////////////////////////////////////////////////

void JSON_readyCallBack(){
    CONTROL_readNewPackage();
}

// check if we can write on buffer or buffer is full
int CONTROL_isPossibleToWritePackage(){
    if(CONTROL.buff_length < MAX_PACKAGE_NUMBER){
        if(CONTROL.buff_length == 0) CONTROL.buffState = CONTROL_BUFF_EMPTY;
        else CONTROL.buffState = CONTROL_BUFF_LOADED;
        return 1;
    }
    CONTROL.buffState = CONTROL_BUFF_FULL;
    return 0;
}

int CONTROL_getBufferLoad(){
    return CONTROL.buff_length;
}

// If the counter ar not the same that meas that we need to read
int CONTROL_isNecessaryToreadBuffer(){
  if(CONTROL.packagesWritePointer != CONTROL.packagesReadPointer){
      return 1;
  }
  return 0;
}

// update read counter and check buffer state
void CONTROL_updateReadLoading(){
    CONTROL.packagesReadPointer++;

    if( CONTROL.packagesReadPointer>=MAX_PACKAGE_NUMBER){// reset package counter
        CONTROL.packagesReadPointer = 0;
    }

    // read next package
    if(!CONTROL_isNecessaryToreadBuffer()){
        CONTROL.buffState = CONTROL_BUFF_EMPTY;
        PRINT_LINE("Buff empty ");
    }

    // reduce buffer buff_length
    if(CONTROL.buff_length>0){
        CONTROL.buff_length --;
    }
}

// Reset all variables from Control type struct
void CONTROL_init(){ 
    PRINT_LINE("Init Control ...  ");
    for(int i=0; i<MOTOR_NUMBER;i++) {
        CONTROL.motor_pos[i] = MOTOR_getActualPosition(i);
    }
    memset(CONTROL.total_movement,0,MOTOR_NUMBER*sizeof(int));
    memset(CONTROL.motor_last_target_pos,0,MOTOR_NUMBER*sizeof(int));
    memset(CONTROL.motor_pos,0,MOTOR_NUMBER*sizeof(int));
    memset(CONTROL.motor_target_pos,0,MOTOR_NUMBER*sizeof(int));
    memset( CONTROL.read_dataval_pointer,0,MOTOR_NUMBER*sizeof(int));
    memset(CONTROL.timer_motor,0,MOTOR_NUMBER*sizeof(int32_t));
    CONTROL.packagesReadPointer = 0;
    CONTROL.packagesWritePointer = 0;
    CONTROL.loadState = CONTROL_FREE_LOADING;
    CONTROL.buffState = CONTROL_BUFF_EMPTY;
    CONTROL.timer_tout = 0;
    CONTROL.buff_length = 0;
    CONTROL.tout_init= 0;
    for(int i=0; i< MAX_PACKAGE_NUMBER;i++){
        CONTROL.package[i].motor_number = 0;
        CONTROL.package[i].size = 0;
        CONTROL.package[i].cmd = 0;
        memset( CONTROL.package[i].dataValues,0,MAX_DATA_VALUES*sizeof(int));
    } 
}

// Use this function as a weak event to know that we have connection active
void __attribute__ ((weak)) CONTROL_connectionCallback(){
    // we are receiving data from client 
    ;
}

// this function makes a copy of the correspondent of the received pacake
// principal function where to read the data and storage in the proper struct or variable used 
void CONTROL_readNewPackage(){ // RX 
    // client is connected and sending data
    CONTROL_connectionCallback();

    int pointer = CONTROL.packagesWritePointer;
    int len_string = 0;

    int cmd = JSON_readIntValueOffset(command_coord,0,NULL);

    PRINT("Read command: ");
    PRINT_LINE(cmd);

    switch (cmd)
    {
        case SET_CURRENT_REG:
            CONTROL.package[pointer].motor_number = JSON_readIntValueOffset(mnumber_coord,0,CONTROL.package[0].control_motors_id);
            CONTROL.package[pointer].size = JSON_readIntValueOffset(values_coord,0,CONTROL.package[pointer].dataValues);
            PRINT("Number of Motors: ");
            PRINT_LINE(CONTROL.package[pointer].motor_number);
            for(int i = 0; i<CONTROL.package[0].motor_number;i++){
                MOTOR_setCurrent(CONTROL.package[0].control_motors_id[i],CONTROL.package[pointer].dataValues[2*i],CONTROL.package[pointer].dataValues[2*i+1]);
            }
            return;
        case SET_ACTUAL_POS:
            //CONTROL_init();
            CONTROL.package[pointer].motor_number = JSON_readIntValueOffset(mnumber_coord,0,CONTROL.package[pointer].control_motors_id);
            CONTROL.package[pointer].size = JSON_readIntValueOffset(values_coord,0,CONTROL.package[pointer].dataValues);
            PRINT("Number of Motors: ");
            PRINT_LINE(CONTROL.package[pointer].motor_number);
            for(int i = 0; i<CONTROL.package[pointer].motor_number;i++){
                MOTOR_setActualPosReg(CONTROL.package[pointer].control_motors_id[i],CONTROL.package[pointer].dataValues[i]);
            }
            return; 
        case CONTROL_RESET_MOTORS:
            CONTROL_init();
            CONTROL.package[0].motor_number = JSON_readIntValueOffset(mnumber_coord,0,CONTROL.package[0].control_motors_id);
            CONTROL.package[0].cmd = cmd;
            PRINT("Number of Motors: ");
            for(int i = 0; i<CONTROL.package[0].motor_number;i++){
                MOTOR_soft_init(CONTROL.package[0].control_motors_id[i]);
            }
            return; 

        case MOTOR_DISABLE:
            CONTROL_init();
            CONTROL.package[0].motor_number = JSON_readIntValueOffset(mnumber_coord,0,CONTROL.package[0].control_motors_id);
            CONTROL.package[0].cmd = cmd;
            for(int i = 0; i<CONTROL.package[0].motor_number;i++){
                MOTOR_disable(CONTROL.package[0].control_motors_id[i]);
            }
            return;
        case MOTOR_ENABLE:
            CONTROL_init();
            PRINT_LINE("enable motor cmd ");
            CONTROL.package[0].motor_number = JSON_readIntValueOffset(mnumber_coord,0,CONTROL.package[0].control_motors_id);
            for(int i = 0; i<CONTROL.package[0].motor_number;i++){
                MOTOR_enable(CONTROL.package[0].control_motors_id[i]);
            }
            return;
        case CONTROL_CONNECTION:
            PRINT_LINE("client connected");
            CONTROL_connectionCallback();
            return;
            break;
        case CONTROL_POSITION_CMD:// data in buffer: cmd,nmotor,motors_id,nvalues,values
        case CONTROL_VELOCITY_CMD:
            CONTROL.package[pointer].motor_number = JSON_readIntValueOffset(mnumber_coord,0,CONTROL.package[pointer].control_motors_id);
            CONTROL.package[pointer].size = JSON_readIntValueOffset(values_coord,0,CONTROL.package[pointer].dataValues);
            CONTROL.package[pointer].cmd = cmd;
            break;
        case CONTROL_EMER_STOP:// manage stop
            CONTROL.package[pointer].motor_number = JSON_readIntValueOffset(mnumber_coord,0,CONTROL.package[pointer].control_motors_id);
            break;
        case CONTROL_ROBOT_NAME:
            PRINT("NAME: ");
            len_string = JSON_readStringValueOffset(rname_coord,0,CONTROL.robotName);
            PRINT(CONTROL.robotName);
            PRINT(", ");
            PRINT_LINE(len_string);
            CONTROL_connectionCallback();
            return;
            break;
        case CONTROL_SET_HOME:
            //CONTROL_init();
            //stop motors
            CONTROL.package[pointer].motor_number = JSON_readIntValueOffset(mnumber_coord,0,CONTROL.package[pointer].control_motors_id);
            CONTROL.package[pointer].size = JSON_readIntValueOffset(values_coord,0,CONTROL.package[pointer].dataValues);
            CONTROL.package[pointer].cmd = cmd;
            PRINT("pointer: ");
            PRINT_LINE(pointer);
            break;
        default:
            PRINT_LINE("NO CMD FOUND\n");
            return;
            break;
    }

    PRINT("Number of Motors: ");
    PRINT_LINE(CONTROL.package[pointer].motor_number);
    PRINT("Size values: ");
    PRINT_LINE(CONTROL.package[pointer].size);

    for(int j=0;j<CONTROL.package[pointer].size;j++){
        PRINT(CONTROL.package[pointer].dataValues[j]);
        PRINT(",");
    }

    PRINT_LINE();

    for(int j=0;j<CONTROL.package[pointer].motor_number;j++){
        PRINT(CONTROL.package[pointer].control_motors_id[j]);
        PRINT(",");
    }

    PRINT_LINE();

    // loading next package in next call
    CONTROL.packagesWritePointer++;
    if( CONTROL.packagesWritePointer >= MAX_PACKAGE_NUMBER){// reset package counter
        CONTROL.packagesWritePointer=0;
    }
    CONTROL.buff_length++;

    CONTROL_isPossibleToWritePackage();
    
    PRINT("Write pointer pckg: ");
    PRINT_LINE(CONTROL.packagesWritePointer);
    PRINT("length in buffer: ");
    PRINT_LINE(CONTROL.buff_length);
}

char data[200];
void CONTROL_loadPackageProcess(){

    CONTROL.loadState = CONTROL_BUSY_LOADING; // protected zone
    
    // copy all variables 
    int pointer         = CONTROL.packagesReadPointer;
    int motorsNumber    = CONTROL.package[pointer].motor_number;
    int* datavals       = CONTROL.package[pointer].dataValues;
    int* mid            = CONTROL.package[pointer].control_motors_id;
    int valuelen        = CONTROL.package[pointer].size;
    int* datapointer    = CONTROL.read_dataval_pointer;
    int* end_movement   = CONTROL.total_movement;
    int end_count       = 0;
    int pointer_inner   = 0;
    uint32_t* m_timer   = CONTROL.timer_motor;

    // update actual position ofeach motor used
    for (int i=0; i < motorsNumber;i++){
        CONTROL.motor_pos[i] = MOTOR_getActualPosition(mid[i]);
    }
    int* actualpos      = CONTROL.motor_pos;
    int* target         = CONTROL.motor_target_pos;
    int* last_target    = CONTROL.motor_last_target_pos;

    switch (CONTROL.package[pointer].cmd)
    {
        case CONTROL_SET_HOME:
            
            for (int i=0;i<motorsNumber;i++){
                if(end_movement[i] && target[i] == actualpos[i] )
                    end_count++;
                else{
                    if(target[i] == 0){
                        target[i]=1;// motor moving until LS is set
                        MOTOR_controlSpeed(mid[i],datavals[i*2]);
                        if (mid[i]==0){
                            MOTOR_controlSpeed(1,datavals[i*2]);
                        }
                    }
                    if (LS_getSignal(mid[i])){
                        MOTOR_controlSpeed(mid[i],0);
                        if(mid[i]==0) MOTOR_controlSpeed(1,0);
                        PRINT("end of home motor ");
                        PRINT_LINE(mid[i]);
                        PRINT("Actual pos: ");
                        PRINT_LINE(actualpos[i]); // position where we have the end of range
                        int sign_dir = 1;
                        if(actualpos[i]<0)
                            sign_dir = -1;
                        if(datavals[i*2] < 0)datavals[i*2]*=-1;
                        target[i] = actualpos[i] - sign_dir*datavals[i*2+1];
                        PRINT_LINE(target[i]);
                        MOTOR_controlPos(mid[i],datavals[i*2],target[i]);
                        if (mid[i]==0){
                            int actual_m1 = MOTOR_getActualPosition(1);
                            sign_dir = -1;
                            if(actual_m1<0)
                                sign_dir = 1;
                            PRINT("Actual pos 1: ");
                            PRINT_LINE(actual_m1); // position where we have the end of range
                            target[1] = actual_m1 - sign_dir*datavals[i*2+1];
                            PRINT_LINE(actual_m1 - sign_dir*datavals[i*2+1]);
                            MOTOR_controlPos(1,datavals[i*2],target[1]);
                        }
                        end_movement[i]= 1;
                    }
                }
            }
            break;
        case CONTROL_POSITION_CMD:// data in buffer: cmd,nmotor,motors_id,nvalues,values
            for (int i=0;i<motorsNumber;i++){
                pointer_inner = (motorsNumber*datapointer[i] + i)*2;// data pointer and offset

                // check error in position 
                int err=0;
                int set_pos_flag = 0;
                err = abs(actualpos[i] - target[i]); // get the diference   
                // sprintf(data,"(prev %d). actual pos:%d , target: %d ,error: %d, len : %d, pointer : %d\n",i,actualpos[i],target[i],err,valuelen,pointer_inner);
                // PRINT(data); 
                
                if(err <= MIN_DIFFERENCE_POS){
                    if (pointer_inner < valuelen){
                        set_pos_flag    = 1;
                    }
                    else{
                        end_count++;
                    }
                }
                else{
                    if(datapointer[i] == 0){
                        set_pos_flag    = 1;
                    }
                }

                if(set_pos_flag){
                    int vel         = datavals[pointer_inner+1];
                    target[i]       = datavals[pointer_inner];
                    MOTOR_controlPos(mid[i],vel,target[i]);
                    sprintf(data,"(set %d). error: %d, pointer : %d, actualpos: %d, target: %d, vel: %d\n",i,err,datapointer[i],actualpos[i],target[i],vel);
                    PRINT(data); 
                    datapointer[i]++;  
                }
            }
            break;
        case CONTROL_VELOCITY_CMD:
            for (int i=0;i<motorsNumber;i++) {
                if (isTimerExpired(m_timer[i])){
                    pointer_inner = (motorsNumber*datapointer[i] + i)*2;// data pointer and offset
                    if(pointer_inner < valuelen){ 
                        PRINT(" pointer: ");
                        PRINT_LINE(datapointer[i]);
                        #ifdef FEEDBACK_ACTIVE
                        if(CONTROL.motor_target_pos[i] != CONTROL.motor_pos[i] ||datapointer[i]==0 ){
                        #endif
                            CONTROL.motor_target_pos[i]= CONTROL.motor_pos[i];
                            MOTOR_controlSpeed(mid[i],datavals[pointer_inner]);
                            PRINT("Next timer : ");
                            PRINT_LINE(datavals[pointer_inner+1]);
                            m_timer[i] = setTimerLoad(datavals[pointer_inner+1]);// load new timer for next movement
                            datapointer[i]++;// data pointer
                        #ifdef FEEDBACK_ACTIVE
                        } // no movement
                        else{
                            PRINT_LINE("Not moving ...........................................");
                        }
                        #endif
                    }
                    else{
                        end_count++;
                    }
                }
            }
            break;
        case CONTROL_EMER_STOP:// manage stop
            MOTOR_stopMotor_id(mid,motorsNumber);
            break;
        default:
            CONTROL.loadState = CONTROL_BUSY_LOADING;
            return;
            break;
    }

     #if DEBUG_LEVEL > 1
        PRINT("End count : ");
        PRINT_LINE(end_count);
    #endif

    if(end_count >= motorsNumber){// see if its necesary to keep reading
        end_count = 0;
        CONTROL.tout_init = 0;
        // reset control data
        memset(target,0,MOTOR_NUMBER*sizeof(int));
        memset(end_movement,0,MOTOR_NUMBER*sizeof(int));
        memset(datapointer,0,MOTOR_NUMBER*sizeof(int));
        memset(m_timer,0,MOTOR_NUMBER*sizeof(int32_t));
        PRINT_LINE("end");

        // check if is necesary to read
        CONTROL_updateReadLoading();
        CONTROL_connectionCallback();
    }
    CONTROL.loadState = CONTROL_FREE_LOADING;
}

// call this function in a loop to functionality. At least 5 ms

void CONTROL_loop(){
    // enter just if there is data in buffer and there is no loading operation going  
    if (CONTROL.buff_length > 0){

        #if DEBUG_LEVEL > 1
            PRINT_LINE("-----------------------------------------------------------------------");
            PRINT_LINE("-----------------------------------------------------------------------");
            PRINT_LINE("-----------------------------------------------------------------------");
            PRINT("length in buffer: ");
            PRINT_LINE(CONTROL.buff_length);
            PRINT(" init tout flag: ");
            PRINT_LINE(CONTROL.tout_init);
        #endif

        // holding time out of loading package
        if(CONTROL.tout_init == 1){
            if(isTimerExpired(CONTROL.timer_tout)){
                for (int i=0;i<CONTROL.package[CONTROL.packagesReadPointer].motor_number;i++){
                    MOTOR_controlSpeed(CONTROL.package[CONTROL.packagesReadPointer].control_motors_id[i],0);// stop motors for safety
                }
                CONTROL_init(); // reset states and buffer
                PRINT_LINE("Loading procces exceeded LOADIN_PKG_TOUT time .... control buffer reset. Consider robot homming");
                return;
            }
        }
        else{
            CONTROL.tout_init = 1;
            CONTROL.timer_tout = setTimerLoad(LOADING_PKG_TOUT);
            PRINT_LINE("Init timer tou for loading process");
        }

        #if DEBUG_LEVEL > 1
            PRINT_LINE("-----------------------------------------------------------------------");
            PRINT_LINE("-----------------------------------------------------------------------");
            PRINT_LINE("-----------------------------------------------------------------------");
        #endif

        CONTROL_loadPackageProcess();
    }
}