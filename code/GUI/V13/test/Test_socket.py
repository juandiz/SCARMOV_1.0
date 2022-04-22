import socket
# import Movement_calc as Mov
import time
import numpy as np

ip_addr = '192.168.1.140'
port = 2390

last_pos = [0,0.6,0]
q_init = [0,0,0]
vel_lin = 0.5 # m/s
POINTS = 50
T_MOV = 1 # seconds 

def openSocket():

    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip_addr,port))
        print("connected")
    except:
        print("connection error")
    return s

def openSocket_UDP():
    global s
   
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # s.connect((ip_addr,port))
        print("connected")
    except:
        print("connection error")
    return s

def getPos():
    print("Position: ")
    pos=input()
    coord=3*[0]
    i=0
    p=0
    data = ''
    for x in pos:
        i += 1
        if x != ',':
            data = data + x
        if x == ',' or i == len(pos):
            coord[p] = data
            p += 1
            data = ''
    return coord

def parsMSG(pos):
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
    
    msj_send = "OWRx:"+pos[0]+"y:"+pos[1]+"z:"+pos[2]
    print(msj_send)
    return msj_send


if __name__ == "__main__":
    s = openSocket_UDP()
    
    while True:
        m = input()
        if m[0] == 'g':
            if m[1] == 'c':
                msg = '{cmd:5006,motors:[2],values:[450,500]}'
            elif m[1] == 'o':
                msg = '{cmd:5006,motors:[2],values:[100,500]}'
        if m[0] == 'h':
            try:
                if m[1] == '0':
                    msg = '{cmd:5006,motors:[0],values:[2000,1000]}'
                elif m[1] == '1':
                    msg = '{cmd:5006,motors:[1],values:[-2000,1000]}'
                elif m[1] == '2':
                    msg = '{cmd:5006,motors:[2],values:[-500,100]}'
                try:
                    print(msg)
                    s.sendto(msg.encode(encoding="utf-8"),(ip_addr,port))
                    time.sleep(1/POINTS)
                except:
                    print("connection lost")
                    break
            except:
                msg = '{cmd:5006,motors:[2],values:[-500,100]}'
                s.sendto(msg.encode(encoding="utf-8"),(ip_addr,port))
                time.sleep(1/10)
                msg = '{cmd:5006,motors:[1],values:[-2000,500]}'
                s.sendto(msg.encode(encoding="utf-8"),(ip_addr,port))
                time.sleep(1/10)
                msg = '{cmd:5006,motors:[0],values:[2000,500]}'
                s.sendto(msg.encode(encoding="utf-8"),(ip_addr,port))
                time.sleep(1/10)
        else:
            msg = '{cmd:5002,motors:[1],values:['+str(m)+',3000]}'
            n=m
            try:
                print(msg)
                s.sendto(msg.encode(encoding="utf-8"),(ip_addr,port))
                time.sleep(1/POINTS)
            except:
                print("connection lost")
                break
