//************************************************************************************************************************
//**********Archivo que contiene todas las funciones creadas para facilitar la comunicacion con los motores***************
//************************************************************************************************************************
#ifndef USER_MOTOR_CONTROL_H_
#define USER_MOTOR_CONTROL_H_

#include <stdint.h>

void MOTOR_init();                          //Funcion que inicializa los drivers de los motores y los pone a velocidad 0.
void MOTOR_disable(int targeMotor);
void MOTOR_enable(int targeMotor);
void MOTOR_soft_init(int target_motor);
void MOTOR_controlSpeed(int targetMotor, int v);  //Funcion que permite controlar la velocidad de un motor. Ej: controlSpeed(0,5000);
void MOTOR_controlPos(int targetMotor, int velocity, int pos);
void MOTOR_setSpeeds(int * velMotores, int);           //Funcion que permite escribir las velocidades de los tres motores. Ej: setSpeeds(velocidades);
void MOTOR_setPos(int* velMotores, int size);
void MOTOR_setHomePos(int targetMotor);
void MOTOR_stopMotor_id(int* id,int sizeid);
int MOTOR_getActualPosition(int motorid);
int MOTOR_checkActive();
uint8_t MOTROR_getHoldState();
void MOTOR_setActualPosReg(int mot_id, int actual_pos);
void MOTOR_setCurrent(int mot_id, int i_hold_mA, int i_run_mA);
int MOTOR_getIRun(int target_motor);
int MOTOR_getIHold(int target_motor);
int MOTOR_getRefPosition(int targetMotor);

#endif // USER_MOTOR_CONTROL_H_