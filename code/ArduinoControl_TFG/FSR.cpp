
#include "FSR.h"

#include "porting_mcu.h"

#include "config_file.h"

#define G_FORCE 9.98F // m/s

uint8_t FSR_pinNumber[FSR_NUMBER] = FSR_PINS_SELECTION;    // define da pins for FSR

uint16_t fsrReading = 0;
unsigned long fsrResistance;  // The voltage converted to resistance
unsigned long fsrConductance; 

typedef struct{
  uint8_t pin; //
  uint32_t resistance_ohm;// the last value of voltage read
  float force_N;
}FSR_typedef;

FSR_typedef FSR_object[FSR_NUMBER];

void FSR_init(){
  for (int i=0; i<FSR_NUMBER;i++){
    FSR_object[i].pin = FSR_pinNumber[i];
    FSR_object[i].resistance_ohm = 0;
    FSR_object[i].force_N = 0;
  }
}

float FSR_getForce_N(int FSR_id){ 
  if(FSR_id < FSR_NUMBER)
    return FSR_object[FSR_id].force_N;
  else
    return 0;
}

float FSR_read(int pin){
  fsrReading = analogRead(pin); 
  // analog voltage reading ranges from about 0 to 1023 which maps to FSR_MESURE_VOLTAGE
  float V_FSR = (float)fsrReading*FSR_MESURE_VOLTAGE/1023;
  //V_FSR = map(fsrReading, 0, 1023, 0, FSR_MESURE_VOLTAGE);
  float R_FSR = 0;

  #if DEBUG_LEVEL > 2
    PRINT("mV:  ");
    PRINT_LINE(V_FSR);
  #endif

  #ifdef FSR_PULLUP_CONFIG
    if (V_FSR < FSR_MESURE_VOLTAGE)
      R_FSR = (float)FSR_RESISTANCE/(((float)FSR_MESURE_VOLTAGE/(float)V_FSR)-1);
    else{
 //     PRINT("out ");
      R_FSR = FSR_MAX_RESISTANCE;
      return 0; // no force
    }
  #elif defined(FSR_PULLDOWN_CONFIG)
      ////////////////////////////////

  #endif

  // PRINT("Resist ");
  // PRINT_LINE(R_FSR);

  float F_Newton = 0.0;

  // We have mN units 
  if(R_FSR<300){  //   0≤R_FSR<300
  //PRINT("Tramo 1");
    F_Newton = (0.8611*(float)R_FSR*(float)R_FSR-523.87*(float)R_FSR+82769.0)*G_FORCE;
  }
  else if (R_FSR < 750){ // 300Ω≤R_FSR<750Ω
   // PRINT("Tramo 2");
    F_Newton = (0.0214*(float)R_FSR*(float)R_FSR-26.544*(float)R_FSR+8569.7)*G_FORCE;
  } 
  else if (R_FSR < 1500){ //    750Ω≤R_FSR<∞
 // PRINT("Tramo 3");
    F_Newton = (0.0005*(float)R_FSR*(float)R_FSR-1.4764*(float)R_FSR+1218.4)*G_FORCE;
  }
  else{
    F_Newton = (-0.1408*(float)R_FSR+379.61)*G_FORCE;
  }

  if (F_Newton < 0) F_Newton = 0;
  else{
    F_Newton = F_Newton/1000; // change to Newtons
  }

  #if DEBUG_LEVEL > 2
    PRINT("Force ");
    PRINT_LINE(F_Newton);
  #endif

  return F_Newton;
}

void FSR_task(){ // this function should be called every 100 ms at least to upodate all values
  for (int i=0; i<FSR_NUMBER;i++){
    FSR_object[i].force_N = FSR_read(FSR_object[i].pin);
  }
}

