
#include "userMotorControl.h"

#include "TMC5160/TMC5160.h"
#include "TRINAMIC_PORTING.h"

#include "config_file.h"
#include "porting_mcu.h"

enum {
  revol_motor,
  linear_motor
};

#define LINEAR_MOTOR_FACTOR           (float)(USTEPS_REVOLUTION/80.0F) // facto for cm. Inner value x100
#define REVTMC5160_TO_CM100           (float)(80.0F/USTEPS_REVOLUTION)

#define ANGELS_TO_REVTMC5160          (float)(USTEPS_REVOLUTION/36000.0F)
#define REVTMC5160_TO_ANGELS          (float)(36000.0F/USTEPS_REVOLUTION) // degrees values x100

#define IHOLD_IRUN_BASE               0x00060000 //
                                      // (IRUN)12-8(IHOLD)4-0
// #define IHOLD_IRUN_0                  ((IHOLD_IRUN_BASE)|0x00000303) // 
// #define IHOLD_IRUN_1                  ((IHOLD_IRUN_BASE)|0x00000704) // 
// #define IHOLD_IRUN_2                  ((IHOLD_IRUN_BASE)|0X00000808) // 
// #define IHOLD_IRUN_3                  ((IHOLD_IRUN_BASE)|0X00000B0A) // 
// #define IHOLD_IRUN_4                  ((IHOLD_IRUN_BASE)|0X00000C0A) //
// #define IHOLD_IRUN_5                  ((IHOLD_IRUN_BASE)|0X0000100C) //
// #define IHOLD_IRUN_6                  ((IHOLD_IRUN_BASE)|0X00001208) //

// uint32_t reg_ihold_irun[7] = {IHOLD_IRUN_0,IHOLD_IRUN_1,IHOLD_IRUN_2,IHOLD_IRUN_3,IHOLD_IRUN_4,IHOLD_IRUN_5,IHOLD_IRUN_6};

uint32_t reg_iHoldiRun[MOTOR_NUMBER];
float scale_cpy_ptr[MOTOR_NUMBER] = MOTORS_SCALE_CONSTANT;
int   mot_i_level_ptr[MOTOR_NUMBER] = MOT_CURRENT_SELECTION;
int   mot_type_ptr[MOTOR_NUMBER] = MOT_TYPES_ARRAY;
float current_cut_i[MOTOR_NUMBER] = MOTOR_FUNCTION_CUT_I;
float current_m_func[MOTOR_NUMBER] = MOTOR_FUNCTION_M;
uint8_t   hold_reg = 0; 
int ref_motor_id[MOTOR_NUMBER] = REF_ID;


void MOTOR_init(){

  tcm5160_init();

  for(int i = 0; i < MOTOR_NUMBER; i++)
  {

    // MULTISTEP_FILT=1, EN_PWM_MODE=1 enables stealthChop
    tmc5160_writeInt(i, TMC5160_GCONF, 0x0000000C);//4

    // TOFF=3, HSTRT=4, HEND=1, TBL=2, CHM=0 (spreadCycle)
    tmc5160_writeInt(i, TMC5160_CHOPCONF, 0x000100C3);

    // // IHOLD=10, IRUN=15 (max. current), IHOLDDELAY=6
    tmc5160_writeInt(i, TMC5160_IHOLD_IRUN, IHOLD_IRUN_BASE);// starting with IHOLD to 0 in order to set the position of global home if needed

    // TPOWERDOWN=10: Delay before power down in stand still
    tmc5160_writeInt(i, TMC5160_TPOWERDOWN, 0x0000000A);

    // TPWMTHRS=500
    tmc5160_writeInt(i, TMC5160_TPWMTHRS, 0x000001F4);

    // Values for speed and acceleration
    tmc5160_writeInt(i, TMC5160_VSTART, 1);
    tmc5160_writeInt(i, TMC5160_A1, 10000);
    tmc5160_writeInt(i, TMC5160_V1, 20000);
    tmc5160_writeInt(i, TMC5160_AMAX, 20000);
    tmc5160_writeInt(i, TMC5160_VMAX, 50000);
    tmc5160_writeInt(i, TMC5160_DMAX, 20000);
    tmc5160_writeInt(i, TMC5160_D1, 6000);
    tmc5160_writeInt(i, TMC5160_VSTOP, 10);
    tmc5160_writeInt(i, TMC5160_RAMPMODE, TMC5160_MODE_POSITION);

    reg_iHoldiRun[i] = IHOLD_IRUN_BASE;

    MOTOR_controlSpeed(i,0); // set initial speed to 0
  }
}

int MOTOR_getIRun(int target_motor){
  int reg = (((reg_iHoldiRun[target_motor]&(0xFF00))>>8)-1);
  // PRINT("Run_reg: ");
  // PRINT_LINE(reg);
  if (reg<=0) return 0;
  int i = (current_m_func[target_motor]*reg + current_cut_i[target_motor]);
  return i;
}

int MOTOR_getIHold(int target_motor){
  int reg = ((reg_iHoldiRun[target_motor]&(0xFF))-1);
  // PRINT("Hold_reg: ");
  // PRINT_LINE(reg);
  if (reg<=0) return 0;
  int i = (current_m_func[target_motor]*reg + current_cut_i[target_motor]);
  return i;
}

void MOTOR_soft_init(int target_motor){

  hold_reg &= ~((uint8_t)(1<<target_motor)); 

  MOTOR_setActualPosReg(target_motor,0);
  // MULTISTEP_FILT=1, EN_PWM_MODE=1 enables stealthChop
  tmc5160_writeInt(target_motor, TMC5160_GCONF, 0x0000000C);//4

  // TOFF=3, HSTRT=4, HEND=1, TBL=2, CHM=0 (spreadCycle)
  tmc5160_writeInt(target_motor, TMC5160_CHOPCONF, 0x000100C3);

  // // IHOLD=10, IRUN=15 (max. current), IHOLDDELAY=6
  tmc5160_writeInt(target_motor, TMC5160_IHOLD_IRUN,IHOLD_IRUN_BASE);// starting with IHOLD to 0 in order to set the position of global home if needed

  // TPOWERDOWN=10: Delay before power down in stand still
  tmc5160_writeInt(target_motor, TMC5160_TPOWERDOWN, 0x0000000A);

  // TPWMTHRS=500
  tmc5160_writeInt(target_motor, TMC5160_TPWMTHRS, 0x000001F4);

  // Values for speed and acceleration
  tmc5160_writeInt(target_motor, TMC5160_VSTART, 1);
  tmc5160_writeInt(target_motor, TMC5160_A1, 10000);
  tmc5160_writeInt(target_motor, TMC5160_V1, 20000);
  tmc5160_writeInt(target_motor, TMC5160_AMAX, 20000);
  tmc5160_writeInt(target_motor, TMC5160_VMAX, 50000);
  tmc5160_writeInt(target_motor, TMC5160_DMAX, 20000);
  tmc5160_writeInt(target_motor, TMC5160_D1, 6000);
  tmc5160_writeInt(target_motor, TMC5160_VSTOP, 10);
  tmc5160_writeInt(target_motor, TMC5160_RAMPMODE, TMC5160_MODE_POSITION);
}

void MOTOR_setActualPosReg(int mot_id, int actual_pos){
  PRINT("For motor: ");
  PRINT(mot_id);
  PRINT(" set position: ");
  PRINT_LINE(actual_pos);
  float target_pos = ((float)(actual_pos)*ANGELS_TO_REVTMC5160*scale_cpy_ptr[mot_id]);
  tmc5160_writeInt(mot_id, TMC5160_XACTUAL, target_pos); 
  tmc5160_writeInt(mot_id, TMC5160_XTARGET, target_pos);  
}

void MOTOR_setCurrent(int mot_id, int i_hold_mA, int i_run_mA){

  PRINT("---------------------------------------------------------------------------------");

  PRINT("Setting currents: ");
  PRINT(i_hold_mA);
  PRINT(" Run ");
  PRINT_LINE(i_run_mA);

  // // IHOLD=10, IRUN=15 (max. current), IHOLDDELAY=6
  uint8_t reg_hold = 0;
  uint8_t reg_run = 0;
  if (i_hold_mA>0)
    reg_hold = ((uint8_t)(((float)i_hold_mA - current_cut_i[mot_id])/current_m_func[mot_id]))+1;
    if(reg_hold<0) reg_hold = 1;
  if (i_run_mA>0)
    reg_run = ((uint8_t)(((float)i_run_mA - current_cut_i[mot_id])/current_m_func[mot_id]))+1;
    if(reg_run<0) reg_run = 1;
  if(reg_hold >= 31) reg_hold = 31;
  if(reg_run >= 31) reg_run = 31;

  
  PRINT("I_HOLD: ");
  PRINT(reg_hold);
  PRINT(" I_RUN ");
  PRINT_LINE(reg_run);

  // update register
  reg_iHoldiRun[mot_id] = (reg_iHoldiRun[mot_id]&0xFFFF0000)|(reg_run<<8)|reg_hold;
  // reg_iHoldiRun[mot_id] = (reg_iHoldiRun[mot_id]&0xFFFF0000)|(i_run_mA<<8)|i_hold_mA;
  PRINT("New reg ");
  PRINT(mot_id);
  PRINT(": ");
  PRINT_LINE(reg_iHoldiRun[mot_id]);

  PRINT("---------------------------------------------------------------------------------");
  //tmc5160_writeInt(mot_id, TMC5160_IHOLD_IRUN,reg_iHoldiRun[mot_id]);// starting with IHOLD to 0 in order to set the position of global home if needed
}

void MOTOR_controlPos(int targetMotor, int velocity, int pos)
{
  int target_vel = 0,target_pos=0;
  
  switch (mot_type_ptr[targetMotor]){
    case revol_motor:
      target_vel = ((float)(velocity)*ANGELS_TO_REVTMC5160*scale_cpy_ptr[targetMotor]);
      target_pos = ((float)(pos)*ANGELS_TO_REVTMC5160*scale_cpy_ptr[targetMotor]);
      break;
    case linear_motor:
      target_vel = ((float)(velocity)*LINEAR_MOTOR_FACTOR*scale_cpy_ptr[targetMotor]);
      target_pos = ((float)(pos)*LINEAR_MOTOR_FACTOR*scale_cpy_ptr[targetMotor]);
      break;
    default:
      return;
  }
  
  uint8_t buff[100];
  sprintf((char*)buff, "Motor %d -> req position:%d, velocity:%d",targetMotor, target_pos,target_vel);
  PRINT_LINE((char*)buff);

  if (target_vel < 0) target_vel *= -1; // must be a positive velocity
  if (velocity < MIN_VELOCITY) velocity = MIN_VELOCITY;

  tmc5160_writeInt(targetMotor, TMC5160_RAMPMODE, TMC5160_MODE_POSITION);
  tmc5160_writeInt(targetMotor, TMC5160_VMAX, (int)target_vel);
  tmc5160_writeInt(targetMotor, TMC5160_XTARGET, (int)target_pos); //*100

}

uint8_t MOTROR_getHoldState(){
  return hold_reg;
}

void MOTOR_disable(int targeMotor){
  hold_reg &= ~((uint8_t)(1<<targeMotor));
  tmc5160_writeInt(targeMotor, TMC5160_IHOLD_IRUN,(reg_iHoldiRun[targeMotor])&&0xFFFFFF00); // turn IHOLD to 0
}

void MOTOR_enable(int targeMotor){
  hold_reg |= 1<<targeMotor;
  tmc5160_writeInt(targeMotor, TMC5160_IHOLD_IRUN,reg_iHoldiRun[targeMotor]);
}

int MOTOR_checkActive(){
  int reg_aux = 0;
  for(int i = 0; i < MOTOR_NUMBER; i++){
    if(tmc5160_readInt(i, TMC5160_GCONF))
      reg_aux |=1<<i;
    else
      hold_reg &= ~((uint8_t)(1<<i));
  }
  // PRINT_LINE(reg_aux);
  return reg_aux; 
}

void MOTOR_controlSpeed(int targetMotor, int v)
{
  int target_vel = 0;

  switch (mot_type_ptr[targetMotor]){
    case revol_motor:
      target_vel = v*ANGELS_TO_REVTMC5160*scale_cpy_ptr[targetMotor];
      break;
    case linear_motor:
      target_vel = v*LINEAR_MOTOR_FACTOR*scale_cpy_ptr[targetMotor];
      break;
    default:
      return;
  }

  uint8_t buff[100];
  sprintf((char*)buff, "Motor %d -> req speed: %d",targetMotor, target_vel);
  PRINT_LINE((char*)buff);

  if (target_vel>=0)
  {
    tmc5160_writeInt(targetMotor, TMC5160_RAMPMODE, TMC5160_MODE_VELPOS);
  }
  else
  {
    target_vel = -target_vel;
    tmc5160_writeInt(targetMotor, TMC5160_RAMPMODE, TMC5160_MODE_VELNEG);
  }
  if (target_vel<MIN_VELOCITY) target_vel = MIN_VELOCITY;
  tmc5160_writeInt(targetMotor, TMC5160_VMAX, target_vel);//*100
}

void MOTOR_stopMotor_id(int* id,int sizeid){
  for (int i=0; i< sizeid; i++){
    MOTOR_controlSpeed(id[i],0);
  }
}

// this function controls the velocity of each motor. The size determines the last motor to be controlled (if size 1 == control of motor 0)
// size should be the same dimension of velMotores
void MOTOR_setSpeeds(int* velMotores, int size){
  for (int i=0; i< size; i++){
    MOTOR_controlSpeed(i,velMotores[i]);
  }
}

void MOTOR_setPos(int* velMotores, int size){
  for (int i=0; i< size; i++){
    MOTOR_controlPos(i,10000,velMotores[i]);
  }
}

int MOTOR_getActualPosition(int targetMotor){
  int actual_angel = 0;
  switch (mot_type_ptr[targetMotor]){
    case revol_motor:
      actual_angel = REVTMC5160_TO_ANGELS*tmc5160_readInt(targetMotor, TMC5160_XACTUAL)/scale_cpy_ptr[targetMotor];
      break;
    case linear_motor:
       actual_angel = REVTMC5160_TO_CM100*tmc5160_readInt(targetMotor, TMC5160_XACTUAL)/scale_cpy_ptr[targetMotor];
      break;
    default:
      return 0;
  }
  return actual_angel;
}

int MOTOR_getRefPosition(int targetMotor){
  int pos =  MOTOR_getActualPosition(targetMotor);
  if (targetMotor != ref_motor_id[targetMotor]){
    return (pos - MOTOR_getActualPosition(ref_motor_id[targetMotor]));
  }
  return pos;
}
