import sys

from numpy import ndarray
sys.path.append('C:/Users/Fusion360/Documents/Recuperacion Disco D/TFG/GitHub/GUI/GUI/V9')

from Defines_global import *
import Movement_calc as Mov
from socket_class import *
import time

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

# Definimos una función para construir las matrices de transformación
# en forma simbóĺica a partir de los parámetros D-H

def symTfromDH(theta, d, a, alpha):
    # theta y alpha en radianes
    # d y a en metros
    Rz = sp.Matrix([[sp.cos(theta), -sp.sin(theta), 0, 0],
                   [sp.sin(theta), sp.cos(theta), 0, 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]])
    tz = sp.Matrix([[1, 0, 0, 0],
                   [0, 1, 0, 0],
                   [0, 0, 1, d],
                   [0, 0, 0, 1]])
    ta = sp.Matrix([[1, 0, 0, a],
                   [0, 1, 0, 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]])
    Rx = sp.Matrix([[1, 0, 0, 0],
                   [0, sp.cos(alpha), -sp.sin(alpha), 0],
                   [0, sp.sin(alpha), sp.cos(alpha), 0],
                   [0, 0, 0, 1]])
    T = Rz*tz*ta*Rx
    return T

def matrixFromEuler(alpha, beta, gamma):
    # theta y alpha en radianes
    # d y a en metros
    Ra = sp.Matrix([[1, 0, 0, 0],
                   [0, sp.cos(alpha), -sp.sin(alpha), 0],
                   [0, sp.sin(alpha), sp.cos(alpha), 0],
                   [0, 0, 0, 1]])
    Rb = sp.Matrix([[sp.cos(beta), 0, sp.sin(beta), 0],
                   [0, 1, 0, 0],
                   [-sp.sin(beta), 0, sp.cos(beta), 0],
                   [0, 0, 0, 1]])
    Rc = sp.Matrix([[sp.cos(gamma), -sp.sin(gamma), 0, 0],
                   [sp.sin(gamma), sp.cos(gamma), 0, 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]])
    T = Ra*Rb*Rc
    return T

# matrix 
q1=sp.symbols('q1')
T01 = symTfromDH(q1, 0, 0.35, sp.pi)

q2=sp.symbols('q2')
T12 = symTfromDH(q2+q1, 0, 0.25, sp.pi)

q3=sp.symbols('q3')
T23 = symTfromDH(0, q3, 0, 0)

T03= T01*T12*T23
T=sp.simplify(T03)

def setPos(pos,rot):
    
    t = sp.Matrix([[1, 0, 0, pos[0]],
                [0, 1, 0, pos[1]], 
                [0, 0, 1, pos[2]], 
                [0, 0, 0, 1]])

    D = t*matrixFromEuler(rot[0], rot[1], rot[2])
    print(D)
    print(T)               

    q = sp.nsolve((T-D),(q1,q2,q3),(1,1,1), prec = 6, verify=False) #agregamos valor inicial para probar
    for i in range(len(q)):
        q[i]=q[i]*180/np.pi
    print(q)
    return q


#pos y orientacion
t=2
pos_init=[0,0,0]
kend=0
positions = [[0,0,0],[-0.3,-0.3,0],[0.5,0.5,0],[0.3,-0.3,0],[0.4,0.4,0],[0.5,0.5,0]]
while kend < 6:
    # print("x: ")
    # x = round(float(input()),2)
    # print("y: ")
    # y = round(float(input()),2)
    # z = 0
    alpha = 0
    beta = 0
    gamma = 0
    #calculo del angulo necesario a partir de la jacobiana.
    if kend>0:
        print(positions[kend])
        q = setPos(positions[kend],[alpha,beta,gamma])
    
        kend+=1
   
        vel=[]
        for i in range(3):
            dif = q[i] - pos_init[i] 
            if (abs(dif) > 360):
                if (dif>0):
                    dif = dif - 360
                else:
                    dif = dif + 360

            pos_init[i]  = q[i]
            speed =(2.5*dif*VEL_360PERSEC)/(360*t)
            vel.append(speed)
            print("vel" + str(i)+"="+str(vel[i]))
        msg = parsMSG(vel,str(t*1000),str(1))
        print(msg)
        arduino.sendMsg(msg)
    else:
        vel = [0,0,0]
        msg = parsMSG(vel,str(t*1000),str(1))
        print(msg)
        arduino.sendMsg(msg)
        kend+=1
    time.sleep(5)


