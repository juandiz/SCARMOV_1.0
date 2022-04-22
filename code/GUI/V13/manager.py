
# python modules 
import threading
from pubsub import pub
import time
import queue

# propietary modules include
from Commands import *
from Defines_global import *

#principal objects used
q = queue.Queue()

# Daemon class with main proccess 
class man_control(threading.Thread):

    def __init__(self, robot, connection, file ):
        threading.Thread.__init__(self)
        self.daemon                     = True
        self.numberVelSend              = 0
        self.robot                      = robot
        self.connection                 = connection
        self.data_file                  = file
        self.counter_connection         = 0
        self.counter_connection_send    = 0
        self.check_connection_timer     = 0

    def run(self):

        print("main Proccess thread")
        time.sleep(2)
        #This is the proccess that calculates everithing with a while loop which multiplex 
        #the following command each iteration  
        while True:
            try:
                # update display and get next process
                cmd = 0
                pub.sendMessage("State Display")
                # if we dont have any new command check connection
                if self.connection.getMode() != MODE_DEBUG:
                    dif = time.perf_counter() - self.check_connection_timer 
                    if dif >= MANAGER_CHECK_CONNECTION_TOUT:
                        self.check_connection_timer  = time.perf_counter()
                        if self.connection.getConnection():
                            pub.sendMessage("update", State= " Connected . . . " )
                        else:
                            pub.sendMessage("update", State= " Disconnected . . . " )

                # pub.sendMessage("State Display")
                item = q.get(block=True, timeout=TIME_DELAY_LOOP)

                ## here read the next procces to run comming from the quiery q
                if type(item) == tuple :
                    cmd = item[0]
                    if self.connection.getConnection():
                        if self.robot.is_powered():
                            if item[0] == NEW_POS:
                                # in this function we send the new position to the class robot 
                                print("New Position " + str(item[1]))
                                pub.sendMessage("update", State= " Setting New Position " )
                                if self.robot.move_Robot(item[1]) == 0:
                                    pub.sendMessage("update", State= " Unreachable Position " )
                                else:
                                    pub.sendMessage("update", State= " Robot Moving " )
                            if item[0] == CMD_SET_CURRENT_REG:
                                m_id = item[1]
                                h_reg = item[2]
                                r_reg = item[3]
                                self.robot.setNewCurrent(m_id,h_reg,r_reg)
                        else:
                            pub.sendMessage("update", State= "Robot not powered  . . . " )
                    #update last ip saved
                    if item[0] == SAVE_NEW_IP:   
                        pub.sendMessage("update", State= "New Connection Data" )
                        self.data_file.updateAttrValue("IP",item[1])
                        self.data_file.updateAttrValue("PORT",int(item[2]))
                        self.connection.setParams(int(item[2]),item[1])
                        self.connection.changeConnectionType(item[3])

                    if item[0] == SET_ROBOT_PARAMS:
                        change = 0
                        if item[1] != self.robot.name:
                            change+=1
                            self.robot.name = item[1]
                            self.data_file.updateAttrValue("robot_name",item[1])
                        if item[2] != str(self.robot.velocityInCMpS):
                            change+=2
                            self.robot.velocityInCMpS= int(item[2])
                            self.data_file.updateAttrValue("linear_velocity",int(item[2]))
                        if change == 1:
                            pub.sendMessage("update", State= "New robot Name" )
                        elif change == 2:
                            pub.sendMessage("update", State= "New robot Velocity" )
                        elif change == 3:
                            pub.sendMessage("update", State= "New robot Params" )
                    if item[0] == SET_CONNECTION_MODE:
                        self.connection.changeMode(int(item[1]))
                        self.data_file.updateAttrValue("simulation_mode",item[1])
                    if item[0] == SET_COMMUNICATION_SETTINGS:
                        self.robot.setSendMode(int(item[3]))
                        self.robot.setPointsPer_cm(int(item[2]))
                        self.connection.setSizeOfPackage(int(item[1]))
                        self.data_file.updateAttrValue("size_package",int(item[1]))
                        self.data_file.updateAttrValue("point_cm",int(item[2]))
                        self.data_file.updateAttrValue("send_mode",int(item[3]))
                    if item[0] == GRIPPER_CONFIG:
                        ratio = item[1]
                        self.robot.setGripperRatio(ratio)
                else:
                    cmd = item
                    if item == KILL_THRD:
                        self.data_file.writeFile()
                    if self.connection.getConnection():
                        if self.robot.is_powered():
                            if item == CMD_RESET_MOTORS:
                                pub.sendMessage("update", State= "Reset drivers " )
                                self.robot.reset()
                            if item == SEND_PCKG:
                            #here we have the q free to send and check if we can send new values
                                if self.robot.isNewPositionActive() == 1 and self.robot.send_buff_flag == 1 and self.robot.json_ready_flag == 0:
                                    self.robot.sendNextPackage()
                            if item == GO_HOME:
                                pub.sendMessage("update", State= "Setting Home" )
                                self.robot.move_Home()
                                pub.sendMessage("update", State= " Home set " )
                            
                            if item == OPEN_GRIPPER:
                                print("Open Gripper command")
                                self.robot.Open_Gripper()

                            if item == CLOSE_GRIPPER:
                                self.robot.Close_Gripper()
                                print("Close Gripper command")
                            if item == TOGGLE_ROBOT_EN:
                                self.robot.toggle_robot_en()
                                pub.sendMessage("update", State= " Robot toggle " )
                        else:
                            pub.sendMessage("update", State= "Robot not powered  . . . " )
                    else:
                        pub.sendMessage("update", State= "Disconnected . . . " )
                       
                    if item == CONNECT:
                        if self.connection.getConnection():
                            pub.sendMessage("update", State= "Disconnecting . . . " )
                        else:
                            pub.sendMessage("update", State= "Connecting . . . " )
                        self.robot.toggleConnection()
                        
            except queue.Empty:
                # if the manager is free save data in file
                self.data_file.writeFile()
                
            except:
                time.sleep(1)
                pub.sendMessage("update", State= "Exception in Main Proccess "+str(cmd))