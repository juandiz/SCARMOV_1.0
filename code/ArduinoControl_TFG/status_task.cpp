
#include "stdio.h"

#include "status_task.h"
#include "FSR.h"
#include "LimSwitch.h"
#include "frameManager.h"
#include "userMotorControl.h"
#include "control_cmd.h"
#include "config_file.h"
#include "porting_mcu.h"
#include "Timer.h"
#include "wifi_if.h"
#include "display_if.h"

#define SENSOR_DATA_SIZE  40
#define OLED_DELAY_STATE  5000

typedef enum{
    OLED_IP_CONFIG_1 = 0,
    OLED_IP_CONFIG_2 = 1,
    OLED_SENSORS_STATE = 2,
}OLED_State;

OLED_State actual_oled_state = OLED_IP_CONFIG_1;
uint32_t oled_state_timer = setTimerLoad(OLED_DELAY_STATE);
bool oled_change_state = false;

float sensor_new_fsr_top = 0;
float sensor_new_fsr_mid = 0;
float sensor_new_fsr_bot = 0;
uint16_t sensor_new_ls = 0;
uint32_t motor_position = 0;
int buff_state = 0;
int json_state = 0;
int motor_active = 0;
int buff_load = 0;
int msg_number = 0;
int hold_reg_mot = 0;
int port = 0;
char ip[20];

char sensor_data_string[MAX_SETRING_SIZE];
char sensor_data_m[SENSOR_DATA_SIZE];

void state_oled(){
    switch(actual_oled_state) {
        case OLED_IP_CONFIG_1:
            PRINT_LINE("config 1 ____________________");
            display_clear();
            get_ip_config(ip);
            display_println(0,10,"IP Address: ",1);
            display_println(0,20,ip,1);
            actual_oled_state = OLED_IP_CONFIG_2;
            break;
        case OLED_IP_CONFIG_2:
            PRINT_LINE("config 2 ____________________");
            display_clear();
            char port_str[10];
            sprintf(port_str,"%d",LOCAL_PORT);
            display_println(0,10,"Port: ",1);
            display_println(0,20,port_str,1);
            actual_oled_state = OLED_SENSORS_STATE;
            break;
        case OLED_SENSORS_STATE:
            actual_oled_state = OLED_IP_CONFIG_1;
            break;
    }
}

void init_connection_message(){
    float constr[MOTOR_NUMBER]=ROBOT_CONSTRAINTS_CM;
    sprintf(sensor_data_string,"{\"ROBOT_NAME\":\"%s\",\"GRP_ID\":%d,\"MOT_NUMBER\":%d,\"MOV_BASE\":%d,\"CONSTRAINTS\":[",ROBOT_NAME,GRP_ID,MOTOR_NUMBER,MOVEMENT_BASE);
    for(int i=0; i <MOTOR_NUMBER;i++){
        sprintf(sensor_data_m,"%.2f",constr[i]);
        strcat(sensor_data_string,sensor_data_m);
        if(i<(MOTOR_NUMBER-1))
            strcat(sensor_data_string,",");
    }
    strcat(sensor_data_string,"]}\n");
    SEND_newString(sensor_data_string,strlen(sensor_data_string));

    sprintf(sensor_data_string,"");
    sprintf(sensor_data_m,""); 
}

void state_function(){

    if (isTimerExpired(oled_state_timer)){
        state_oled();
        oled_state_timer = setTimerLoad(OLED_DELAY_STATE);
    }

    sensor_new_fsr_top = FSR_getForce_N(FSR_TOP);
    sensor_new_fsr_mid = FSR_getForce_N(FSR_MIDDLE);
    sensor_new_fsr_bot = FSR_getForce_N(FSR_BOTTOM);
    sensor_new_ls  = LS_read();
    buff_state = CONTROL_isPossibleToWritePackage();
    buff_load  = CONTROL_getBufferLoad();
    json_state = JSON_getReadState();
    motor_active = MOTOR_checkActive();
    hold_reg_mot = MOTROR_getHoldState();

    sprintf(sensor_data_string,"{\"ID\":%d,\"LS\":%d,\"FSR\":[%.2f,%.2f,%.2f],\"BUFF\":%d,\"BUFF_LOAD\":%d,\"JSON\":%d,\"MOT_ACTIVE\":%d,\"MOT_HOLD\":%d,\"MOT_POS\":[",
                                        msg_number++,
                                        sensor_new_ls,
                                        sensor_new_fsr_top,
                                        sensor_new_fsr_mid,
                                        sensor_new_fsr_bot,
                                        buff_state,
                                        buff_load,
                                        json_state,
                                        motor_active,
                                        hold_reg_mot);

    for(int i=0; i <MOTOR_NUMBER;i++){
        sprintf(sensor_data_m,"%d",MOTOR_getRefPosition(i));
        strcat(sensor_data_string,sensor_data_m);
        if(i<(MOTOR_NUMBER-1))
            strcat(sensor_data_string,",");
    }
    strcat(sensor_data_string,"],\"MOT_IHOLD\":[");
    sprintf(sensor_data_m,""); 
    for(int i=0; i <MOTOR_NUMBER;i++){
        sprintf(sensor_data_m,"%d",MOTOR_getIHold(i));
        strcat(sensor_data_string,sensor_data_m);
        if(i<(MOTOR_NUMBER-1))
            strcat(sensor_data_string,",");
    }
    strcat(sensor_data_string,"],\"MOT_IRUN\":[");
    sprintf(sensor_data_m,""); 
    for(int i=0; i <MOTOR_NUMBER;i++){
        sprintf(sensor_data_m,"%d",MOTOR_getIRun(i));
        strcat(sensor_data_string,sensor_data_m);
        if(i<(MOTOR_NUMBER-1))
            strcat(sensor_data_string,",");
    }
    strcat(sensor_data_string,"]}\n");
    SEND_newString(sensor_data_string,strlen(sensor_data_string));
    #if DEBUG_LEVEL > 0
        // PRINT_LINE(sensor_data_string);
    #endif
    sprintf(sensor_data_string,"");
    sprintf(sensor_data_m,"");    
}
