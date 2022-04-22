import sys
sys.path.append('C:/Users/Fusion360/Documents/Recuperacion Disco D/TFG/GitHub/GUI/GUI/V9')

from Defines_global import *
import Movement_calc as Mov
from socket_class import *
import time
pos_init = 0


arduino =socket_object()
arduino.setValues(81,'192.168.1.59')
arduino.connect()

def parsMSG(pos,timems, values):
        print(pos)
        print(str(len(pos)))

        #string for params
        x = timems
        for i in range(5-len(timems)):
            x = "0"+ x
        timems = x

        x = values
        for i in range(5-len(values)):
            x = "0"+ x
        values = x

        #string for velocities
        for i in range(len(pos)):
            pos[i]= int (pos[i])
            x = str(abs(pos[i]))
            for j in range(5-len(x)):
                x = "0"+ x
            if pos[i]<0:
                x = "1"+x
            else:
                x = "0"+x
            pos [i] = x
        
        msj_send = "SCR:"+timems + values + "A:"+pos[0]+"B:"+pos[1]+"C:"+pos[2]
        print(msj_send)
        return msj_send

angs=[0,50,-50,90,50,0]
i=0


while True:
    t = 2
    print("where?")

    try:
        p_end = int(input())
    except:
        break

    
    # dif = angs[i] - pos_init 
    dif = p_end - pos_init 
    if (abs(dif) > 360):
        if (dif>0):
            dif = dif - 360
        else:
            dif = dif + 360

    pos_init = p_end
    # i+=
    vel =((2.5)*dif*VEL_360PERSEC)/(360*t)
    vel = int(vel)
    print("vel ="+str(vel))
    msg = parsMSG([vel,0,0],str(2000),str(1))
    print(msg)
    arduino.sendMsg(msg)
    time.sleep(4)

