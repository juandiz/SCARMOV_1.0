

#ifndef CONTROL_CMD_H_
#define CONTROL_CMD_H_

int CONTROL_isPossibleToWritePackage();
int CONTROL_getBufferLoad();
void CONTROL_readNewPackage();
void CONTROL_loop();
void CONTROL_init();

#endif