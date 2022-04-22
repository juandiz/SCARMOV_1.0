import queue
import threading

from socket_class import *
from CoppeliaSim_IF import *
from Defines_global import *

from manager import q
from pubsub import pub

q_send = queue.Queue()

# this class generalize the connection object use between the arduino of the simulation with coppelia sim

class connectionObject(threading.Thread):
    def __init__(self):

        # self object thread
        threading.Thread.__init__(self)
        self.daemon = True

        # self connection params

        #  status flags and data from reception json
        self.simMode            = -1
        self.connection         = 0 # disconnected
        self.toggle_connection  = 0
        self.send_buff_flag     = 0
        self.json_ready_flag    = 0
        self.moving_flag        = 0
        self.motor_active       = 0
        self.robot_power        = 0
        self.robot_hold         = 0
        self.robot_ls_reg       = 0
        self.robot_fsr_array    = []
        self.motor_positions    = []

        # data position management
        self.data1              = []
        self.data2              = []
        self.totalSizeDataToSend = 0

        self.movingActive       = 0 
        self.pointerqTosend     = 0
        self.connection_tout    = 0

        #package data
        self.sendcommand   = VEL_MODE
        self.dataPackage1 = []
        self.dataPackage2 = []
        self.sizePackage = PACKAGE_SEGMENTS

        # reception timer timer
        self.timer_connection_tout = 0

        # object by default Arduino_Sckt
        # self.ObjectConnect = Arduino_Sckt("Arduino Socket")  #default with arduino connection

    # loop for mannage connection features
    def run(self):
        while True:
            # try to toggle conenction
            if self.toggle_connection == 1:
                self.toggle_connection = 0
                if self.connection == 0:
                    pub.sendMessage("update", State= "Trying to connect . . .  " )
                    if self.connect() == 1:
                        pub.sendMessage("update", State= "Connected " )
                    else:
                        pub.sendMessage("update", State= "Connection error. Check connection params . . ." )
                else:
                    self.close()
                    pub.sendMessage("update", State= "Disconnected " )

            if self.getConnection():
                #check if we need to send data from queue
                dif = time.perf_counter()-self.timer_connection_tout
                if dif >= CONNECTION_TOUT and self.simMode == MODE_ARDUINO_MKR:
                    self.toggleConnection()
                else:
                    self.checkSendDataActive()
            else:
                time.sleep(1)# delay for avoiding blocking 
            time.sleep(1/100)

    ########################################################################

    def send_new_mesage(self, mesage):
        q_send.put((mesage))

    def rest_connection_tout(self):
        self.timer_connection_tout = time.perf_counter()

    def receiveMsg(self):
        return self.ObjectConnect.receiveMsg()

    def checkSendDataActive(self): # this function checks if there is new data in query to be send
        try:
            item = q_send.get(block=False)
            if self.simMode == 0:
                print(item)
                self.ObjectConnect.sendMsg(item) 
        except queue.Empty:
            item = 0

    def toggleConnection(self):
        self.timer_connection_tout = time.perf_counter()
        self.toggle_connection = 1

    def getParams(self):
        return self.ObjectConnect.getParms()

    def setCommandMode(self, mode):
        self.ObjectConnect.sendCommand = mode

    def getConnection(self):
        return self.connection

    def getConnectionType(self):
        if self.simMode == MODE_ARDUINO_MKR:
            return self.ObjectConnect.getConnectionType()
        else:
            return "UDP"

    def changeConnectionType(self, type):
        self.ObjectConnect.changeConnectionType(type)

    def setParams(self,port,IP):
        if self.connection == 1:
            self.ObjectConnect.close()
        self.ObjectConnect.setParams(port,IP)

    def changeMode(self, mode):
        if mode != self.simMode:
            if self.connection == 1:
                self.close() #close connection
            if mode == MODE_COPPELIA_SIM:
                self.ObjectConnect = Coppelia("CoppeliaSim Edu")
            elif mode == MODE_ARDUINO_MKR:
                self.ObjectConnect = socket_object("Arduino Socket")
            elif mode == MODE_DEBUG:
                print("Debugging mode selected")
            self.simMode = mode
        return

    def getMode(self):
        return self.simMode

    def getName(self):
        return self.ObjectConnect.getName()

    def connect(self):
        if self.simMode != MODE_DEBUG:
            if self.ObjectConnect.connect() == 1:
                self.connection = 1
            else:
                self.connection = 0    
            return self.connection
        else:
            self.connection = 1
        return self.connection

    def close(self):
        self.connection = 0
        if self.simMode != MODE_DEBUG:
            self.ObjectConnect.close()

    def setReceptionBusy(self):
        self.ObjectConnect.setReceptionBusy()

    def setReceptionReady(self):
        self.ObjectConnect.setReceptionReady()

    def isReceptionReady(self):
        return self.ObjectConnect.isReceptionReady()

    def sendMsg(self, msg):
        q_send.put((msg))
    
    ########################################
    #################### Robot movement 
    ########################################

    def isRobotOn(self):
        if self.simMode == MODE_ARDUINO_MKR:
            return self.motor_active
        return 1
                
    def isRobotMoving(self):
        return self.movingActive

    def setSizeOfPackage(self,size):
        self.sizePackage = size

    def loadDataToSend(self,mode,data1,data2):
        self.totalSizeDataToSend = len(data1)
        self.setCommandMode(mode)
        if self.totalSizeDataToSend >0:
            for i in range(self.totalSizeDataToSend):
                self. data1.append(data1[i])
                self.data2.append(data2[i])
            self.movingActive = 1
            self.loadNewPackageToSend()
            

    def loadNewPackageToSend(self):
        for i in range(self.sizePackage):
            if (self.pointerqTosend+i) > (self.totalSizeDataToSend):
                self.pointerqTosend = 0
                self.movingActive = 0
                i = self.sizePackage
                break 
            else:
                self.dataPackage1.append(self.data1[self.pointerqTosend+i])
                self.dataPackage2.append(self.data2[self.pointerqTosend+i])
                
        if (self.movingActive==1):
            self.pointerqTosend+=self.sizePackage
            q.put((SEND_VEL))

    def sendRobotNextPackage(self):
        if self.simMode != MODE_DEBUG:
            self.ObjectConnect.set_data(self.dataPackage1,self.dataPackage2)
            self.dataPackage1 = []
            self.dataPackage2 = []

    def setGrippervel(self,vel):
        self.ObjectConnect.setGrippervel(vel)
    
    def setRobotPos(self,q):
        self.ObjectConnect.setRobotPos(q)

    def set_velocity(self,vel):
        self.ObjectConnect.set_Vel(vel)
    
    def setRobotHome(self,vels,timesarray):
        self.ObjectConnect.setRobotHome(vels,timesarray)

    def gripper_control(self,vel):
        self.ObjectConnect.gripper_open_close(vel)