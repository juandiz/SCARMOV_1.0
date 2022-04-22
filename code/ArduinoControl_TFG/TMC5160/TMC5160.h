/*
 * TMC5160.h
 *
 *  Created on: 17.03.2017
 *      Author: ED based on BS
 */

#ifndef TMC_IC_TMC5160_H_
#define TMC_IC_TMC5160_H_

#include "../helpers/API_Header.h"
#include "TMC5160_Register.h"
#include "TMC5160_Mask_Shift.h"
#include "TMC5160_Constants.h"

#define TMC5160_FIELD_READ(motor, address, mask, shift)           FIELD_READ(tmc5160_readInt, motor, address, mask, shift)
#define TMC5160_FIELD_WRITE(motor, address, mask, shift, value)   FIELD_WRITE(tmc5160_writeInt, motor, address, mask, shift, value)
#define TMC5160_FIELD_UPDATE(motor, address, mask, shift, value)  FIELD_UPDATE(tmc5160_readInt, tmc5160_writeInt, motor, address, mask, shift, value)

// Factor between 10ms units and internal units for 16MHz
//#define TPOWERDOWN_FACTOR (4.17792*100.0/255.0)
// TPOWERDOWN_FACTOR = k * 100 / 255 where k = 2^18 * 255 / fClk for fClk = 16000000)

typedef struct
{
	int velocity, oldX;
	uint32 oldTick;
	int32 registerResetState[TMC5160_REGISTER_COUNT];
	uint8 registerAccess[TMC5160_REGISTER_COUNT];
	u8 channels[TMC5160_MOTORS];
} TMC5160TypeDef;

void tmc5160_initConfig(TMC5160TypeDef *tmc5160);
void tmc5160_periodicJob(u8 motor, uint32 tick, TMC5160TypeDef *tmc5160, ConfigurationTypeDef *TMC5160_config);
u8 tmc5160_reset(ConfigurationTypeDef *TMC5160_config);
u8 tmc5160_restore(ConfigurationTypeDef *TMC5160_config);

#endif /* TMC_IC_TMC5160_H_ */
