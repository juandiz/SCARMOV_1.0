
#ifndef CONFIG_H_
# define CONFIG_H_

#include "Arduino.h"// used for pin's Macros
#include "stdint.h"

#define DEBUG_LEVEL         1

/////////////////////////////////////////////////////////////////////////////
//////////////////// ROBOT PARAMS ///////////////////////////////////
/////////////////////////////////////////////////////////////////////////////

#define ROBOT_NAME              "SCARMOV 1.0"

#define MOVEMENT_BASE           0

#define ROBOT_CONSTRAINTS_CM    {35,25,80.0F}

/////////////////////////////////////////////////////////////////////////////
//////////////////// MCU_CONFIG ///////////////////////////////////
/////////////////////////////////////////////////////////////////////////////

#define SERIAL_BOUD_RATE            9600
#define SERIAL_INIT_COUNT           5 // number of tries to init serial

/////////////////////////////////////////////////////////////////////////////
//////////////////// MOTORS CONFIGURATION ///////////////////////////////////
/////////////////////////////////////////////////////////////////////////////

#define STEP_PER_REVOLUTION         200
#define USTEPS_REVOLUTION           51200.0F
#define MIN_VELOCITY                500

//The id of each motor corresponds with the place of the array starting from 0 to n-1 , where n is number of motors
#define ENABLE_DRV_PIN              7 // Pin for signal ENABLE of all drivers
#define MOTOR_NUMBER                4
// motors types
#define REV_MOTOR                   0
#define LIN_MOTOR                   1
// pins definitios for motors control
#define GRP_ID                      3
#define MOT_TYPES_ARRAY             {REV_MOTOR,REV_MOTOR,LIN_MOTOR,LIN_MOTOR}
#define MOT_CURRENT_SELECTION       {6,4,1,1}
#define MOTORS_CS_PINS              {2,1,0,A6}
#define MOTORS_SCALE_CONSTANT       {-2.33F,2.45F,1,1}
#define MOTOR_FUNCTION_CUT_I        {-355.8F,-492.53F,-204.22F,-178.63F}
#define MOTOR_FUNCTION_M            {161.11F,127.06F,159.63F,102.82F}
#define REF_ID                      {0,0,2,3}

/////////////////////////////////////////////////////////////////////////////
//////////////////// SENSORS CONFIG ///////////////////////////////////
/////////////////////////////////////////////////////////////////////////////

#define FSR_NUMBER                  3 // number of sensors
#define FSR_RESISTANCE              10000 // resistance
#define FSR_MAX_RESISTANCE          10000000 //   
#define FSR_MESURE_VOLTAGE          3300// in mV
// set resistance config
#define FSR_PULLUP_CONFIG
// #define FSR_PULLDOWN_CONFIG

// FSR's ids
#define FSR_TOP                     0 
#define FSR_MIDDLE                  1
#define FSR_BOTTOM                  2

#define FSR_PINS_SELECTION          {A0,A1,A2} // pins to init

#define LS_NUMBER                   3
#define LS_PINS_SELECTION           {A5,A4,A3}

/////////////////////////////////////////////////////////////////////////////
//////////////////// WIFI SETTINGS ///////////////////////////////////
/////////////////////////////////////////////////////////////////////////////

#define DISCONECT_TOUT      5000 // max waiting time to receive a connection cmd

#define LOCAL_PORT          2390 // local port to listen on

#define WIFI_SSDI_NUMBER    2 

#define MAX_WIFIPACK_SIZE    500

// save de strings if wifi settins. The first value will be the first connection try
#define SECRET_SSID {"mywifi","HUAWEI-MOCHI_2"}
#define SECRET_PASS {"123123jm","KKsks6wjJKws2772"}


/////////////////////////////////////////////////////////////////////////////
//////////////////// TASK CONFIG ///////////////////////////////////
/////////////////////////////////////////////////////////////////////////////

// main loop delays IN MS
#define STATUS_TASK_DELAY           500
#define FSR_TASK_DELAY              100
#define CMD_TASK_DELAY              5
#define COMMUNICATION_LOOP          0

/////////////////////////////////////////////////////////////////////////////
//////////////////// FRAME MANAGER CONFIG ///////////////////////////////////
/////////////////////////////////////////////////////////////////////////////

// Mesages an status management Defines
#define MAX_SEND_BUFF               10
#define MAX_SETRING_SIZE            300

/////////////////////////////////////////////////////////////////////////////
//////////////////// CMD TASK ///////////////////////////////////
/////////////////////////////////////////////////////////////////////////////

#define   MIN_DIFFERENCE_POS      10 // this is 1in grades *100

#define   MAX_PACKAGE_NUMBER      20

#define   LOADING_PKG_TOUT        30000 // max time to process one command

#define   FEEDBACK_ACTIVE

#define   MAX_DATA_VALUES         200 // values 
  
#endif //CONFIG_H_