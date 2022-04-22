from Defines_global import *
from GUI import GUI
from file_manager import FileManager
from manager import man_control
from ConnectionObject import connectionObject
from Robot import Robot

if __name__ == '__main__' :

    #principal objects init
    connection_man = connectionObject()
    file_data = FileManager() #init file manager for data
    robot_scara = Robot(ROBOT_NAME,Constrains,init_pos,Rjoints_max_limist,Rjoints_min_limist,connection_man)

    #read and set saved values if possible
    connection_man.changeMode(file_data.getAttrValue("simulation_mode"))
    connection_man.setParams(file_data.getAttrValue("PORT"),file_data.getAttrValue("IP"))
    connection_man.setSizeOfPackage(file_data.getAttrValue("size_package"))
    connection_man.changeMode(file_data.getAttrValue("simulation_mode"))
    connection_man.changeConnectionType(file_data.getAttrValue("connection_type"))

    robot_scara.name = file_data.getAttrValue("robot_name")
    robot_scara.velocityInCMpS= file_data.getAttrValue("linear_velocity")
    robot_scara.setPointsPer_cm(file_data.getAttrValue("point_cm"))
    robot_scara.setSendMode(file_data.getAttrValue("send_mode"))

    # init threads and GUI
    man = man_control(robot_scara,connection_man,file_data)
    app = GUI(ICON_PATH,robot_scara,connection_man)  
    connection_man.start()
    man.start()
    app.loop()
