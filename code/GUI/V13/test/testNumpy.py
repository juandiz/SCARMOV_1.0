import numpy as np


qOfPosition = [[0,5],[5,-6],[8,1],[7,2]]
pointerqTosend = 0
while pointerqTosend == 0:
    packageTosend = []
    for i in range(5-1):
        lastPos = np.array(qOfPosition[i])
        newPos = np.array(qOfPosition[i+1])
        vel = (newPos - lastPos )
        packageTosend.append(vel)
        pointerqTosend+=1
        if pointerqTosend >= (3-1):
            print(packageTosend)
            break


    print(packageTosend[0][0])