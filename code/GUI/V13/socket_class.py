from Defines_global import *
import socket 

class socket_object:

    def __init__ (self, name):
        self.port = PORT_DEFAULT_ARDUINO
        self.IP   = IP_DEFAULT_ARDUINO
        self.ArduinoReadyNextMSG = 0
        self.name = name
        self.connected = 0
        self.sendCommand = SEND_VEL
        self.connection_type = "TCP"

    ##########################################################
    # Porting functions for conenction Object class
    ##########################################################

    def setReceptionBusy(self):
        self.ArduinoReadyNextMSG = 0

    def setReceptionReady(self):
        self.ArduinoReadyNextMSG=1

    def isReceptionReady(self):
        if (self.ArduinoReadyNextMSG == 1):
            return 1
        return 0

    def getName(self):
        return self.name

    def getConnection(self):
        return self.connected 

    def setParams(self,port, IP):
        self.port = port
        self.IP   = IP
        self.connection_type = "TCP"
        print (f"Set Arduino Socket with port {port} and IP "+IP)
    
    def getParms(self):
        return self.port,self.IP
    
    def changeConnectionType(self,type):
        self.connection_type = type

    #socket connection
    def close(self): #close socket if connected
        if (self.connected):
            self.connected = 0
            self.s.close()
            print ("disconnected")
    
    def getConnectionType(self):
        return self.connection_type
            
    def connect(self): #connecting socket 
        try:
            if self.connection_type == "UDP":
                self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            else:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.connect((self.IP,self.port))
                self.s.setblocking(False)
            self.connected = 1
            print("connected")
            return 1
        except:
            self.connected = 0
            print("connection error")
            return 0

    ############################################################
    def sendMsg(self,msg):
        try:
            if self.connection_type == "UDP":
                self.s.sendto(msg.encode(encoding="utf-8"),(self.IP,self.port))
            else:
                self.s.send(msg.encode(encoding="utf-8"))
        except:
            return 0

    def receiveMsg(self):
        # print("Arduino reception")
        try:
            if self.connection_type == "UDP":
                msg,addr = self.s.recvfrom(2048)
            else:
                msg = self.s.recv(1)
            msg = str(msg.decode(encoding= "utf-8"))
            self.s.setblocking(False)
            return msg
        except :
            # print("REceived Socket Exception")
            return 0