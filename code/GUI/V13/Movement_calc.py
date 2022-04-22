
import numpy as np

from Defines_global import *

# global variables

RAD_TOGRAD = 180/np.pi
GRAD_TORAD = 1/RAD_TOGRAD
changePositionFlag = 0 # init with normal results

##### INVERSE KINEMATICS SCARA ## 

## this function is use to have the direct kinematics of the SCARA robot
def get_position_DK(q_array, l_array):
	x = l_array[0]*np.cos(q_array[0]*GRAD_TORAD) + l_array[1]*np.cos((q_array[1]+q_array[0])*GRAD_TORAD)
	y = l_array[0]*np.sin(q_array[0]*GRAD_TORAD) + l_array[1]*np.sin((q_array[1]+q_array[0])*GRAD_TORAD)
	z = l_array[2] - q_array[2]
	return [round(x,2),round(y,2),round(z,2)]

## This function must be changed if we using other robot 
def inverseKinematics(pos,constraints,mode,changePosition):

	aux = (np.power(pos[0],2) + np.power(pos[1],2) - np.power(constraints[0],2) - np.power(constraints[1],2)) / (2 * constraints[0] * constraints[1])
	if abs(aux) < 1:
		theta2 = np.arccos(aux)
	else:
		if aux > 0:
			theta2 = 0
		else:
			theta2 = np.pi

	# look for the other solution on the positioning
	if changePosition == 1:
		print("------------------  Changing position flag !! --------------------- ")
		theta2 = -theta2

	# prevent division by zero
	if pos[1] != 0:
		theta1 = np.arctan(pos[0] / pos[1]) - np.arctan((constraints[1] * np.sin(theta2)) / (constraints[0] + constraints[1] * np.cos(theta2)))
	else:
		if pos[0] > 0:
			theta1 = np.pi/2 - np.arctan((constraints[1] * np.sin(theta2)) / (constraints[0] + constraints[1] * np.cos(theta2)))
		if pos[0] < 0:
			theta1 = -np.pi/2 - np.arctan((constraints[1] * np.sin(theta2)) / (constraints[0] + constraints[1] * np.cos(theta2)))

	theta2 = (-1) * theta2 * RAD_TOGRAD
	theta1 = (90 - theta1*RAD_TOGRAD)

	#Angles adjustment depending in which quadrant the final tool coordinate x,pos[1] is
	
	#fourth quadrant

	if pos[1]<0:
		theta1 = theta1 - 180

	# print(f"theta1 = {theta1:.2f} theta2 = {theta2:.2f}")

	if mode == 0:
		# we are sending to arduino. According with inverse kinematics we have 
		theta2 = theta1 + theta2
		# theta1 = -theta1 # we have interverted the orientation because of construction specification
	#otherwise we are simulating and this angels are acording with the simulation used with joint in every articulation and with no inverted orientation
	
	angels=[]
	angels.append(round(theta1,2))
	angels.append(round(theta2,2))
	angels.append(round(constraints[2] - pos[2],2))

	return angels

def directKinematicXY(q_vector, constraints):
	x = constraints[0]*np.cos(q_vector[0]/RAD_TOGRAD) + constraints[1]*np.cos((q_vector[0]+q_vector[1])/RAD_TOGRAD)
	y = constraints[0]*np.sin(q_vector[0]/RAD_TOGRAD) + constraints[1]*np.sin((q_vector[0]+q_vector[1])/RAD_TOGRAD)
	return [x,y]

#######################################################################################
##################### PERIMETERS POINTS

def getRangePointsForPlot(rev_max, constraints, segments_cm):
	points = []

	#inner range with s2 in max angle and s1 moving from 0 to max
	movement_angle = rev_max[0]+45
	
	angle_0 = -rev_max[0] # init 
	angle_1 = -rev_max[1] # stays in this angle all movement
	p_0 = directKinematicXY([angle_0,angle_1], constraints)
	r =  np.sqrt(np.power(p_0[0],2) + np.power(p_0,2))# radious of movement
	length_movement = movement_angle*(GRAD_TORAD)*r[0]
	number_points = int(round(length_movement/segments_cm,0)+1)
	for i in range(number_points):
		[x,y] = directKinematicXY([angle_0,angle_1], constraints)
		points.append([x,y])
		angle_0+=movement_angle/number_points

	#inner range with s2 in max angle and s1 moving from 0 to max
	movement_angle = rev_max[0]+45
	
	angle_0 = -45 # init 
	angle_1 = rev_max[1] # stays in this angle all movement
	p_0 = directKinematicXY([angle_0,angle_1], constraints)
	r =  np.sqrt(np.power(p_0[0],2) + np.power(p_0,2))# radious of movement
	length_movement = movement_angle*(GRAD_TORAD)*r[0]
	number_points = int(round(length_movement/segments_cm,0)+1)
	for i in range(number_points):
		[x,y] = directKinematicXY([angle_0,angle_1], constraints)
		points.append([x,y])
		angle_0+=movement_angle/number_points

	# first range es1 max, s2 max. Moving s2 from max to 0º
	movement_angle = rev_max[1]
	length_movement = movement_angle*(GRAD_TORAD)*constraints[1]
	number_points = int(round(length_movement/segments_cm,0)+1)
	angle_1 = rev_max[1]
	angle_0 = rev_max[0]
	for i in range(number_points):
		[x,y] = directKinematicXY([angle_0,angle_1], constraints)
		points.append([x,y])
		angle_1-=movement_angle/number_points

	# s2 reach 0º. s1 moving rev_max[0]*2
	movement_angle = rev_max[0]*2
	length_movement = movement_angle*(GRAD_TORAD)*(constraints[1]+constraints[0])
	number_points = int(round(length_movement/segments_cm,0)+1)
	angle_0 = rev_max[0]
	angle_1 = 0
	for i in range(number_points):
		[x,y] = directKinematicXY([angle_0,angle_1], constraints)
		points.append([x,y])
		angle_0-=movement_angle/number_points

	# s2 moving. s1 stays at max
	movement_angle = rev_max[1]
	length_movement = movement_angle*(GRAD_TORAD)*(constraints[1])
	number_points = int(round(length_movement/segments_cm,0)+1)
	angle_0 = -rev_max[0]
	angle_1 = 0
	for i in range(number_points):
		[x,y] = directKinematicXY([angle_0,angle_1], constraints)
		points.append([x,y])
		angle_1-=movement_angle/number_points

	return points

#######################################################################################
##################### MOVEMENT FUNCTIONS AND LIMITATIONS

def moveTrajectory(pos,coord_last,n_points,rev_max,rev_min,constrains,mode):
	[q_send,change] = trajectory(pos,coord_last,n_points,rev_max,rev_min,constrains,mode)
	length = n_points
	if change == -1 :
		q_send = []
		# we must change direction
		[q_send_change, newlastCoord] = changeDirectionTrayectory(coord_last,constrains,mode,n_points)
		[q_send_inner, err] = trajectory(pos,newlastCoord,n_points,rev_max,rev_min,constrains,mode)
		for i in range(n_points):
			q_send.append(q_send_change[i])
		for i in range(n_points):
			q_send.append(q_send_inner[i])
		length += n_points
	return q_send, length

# Trayectory calculation
def trajectory(pos,coord_last,n_points,rev_max,rev_min,constrains,mode):
	#fraccionamiento de trayectoria mas rápida
	global changePositionFlag

	x_iner=[0]*n_points
	y_iner=[0]*n_points
	z_iner=[0]*n_points

	# print("cord last is "+ str(coord_last))
	if (n_points > 0):
		
		# chack if z has changed 
		if (pos[2]!= coord_last[2]):
			add_z = (pos[2]-coord_last[2])/(n_points-1)
			z_change = 1
		else:
			z_change = 0

		# we take 3 posibilities: 	case 1 - y has changed
		#							case 2 - x has changed 
		#							case 3 - no changes on xy positions
		if (pos[1] != coord_last[1]):
			m = (pos[0]-coord_last[0])/(pos[1]-coord_last[1])
			add_y = (pos[1]-coord_last[1])/(n_points-1)
			case = 1
		else :
			if (pos[0] != coord_last[0]):
				# m = 0
				add_x = (pos[0]-coord_last[0])/(n_points-1)
				case = 2
			else:
				case = 0 # not moving

		if case != 0 or z_change == 1:
			q_send = []
			for i in range(len(x_iner)):
				pos_in = [0]*3
				if i > 0:
					if case == 1:
						y_iner[i]=y_iner[i-1]+add_y
						x_iner[i] = m*(y_iner[i]-coord_last[1]) + coord_last[0]
					if case == 2:
						x_iner[i]=x_iner[i-1]+add_x
						y_iner[i] = coord_last[1] 
					if z_change == 1:
						z_iner[i] = z_iner[i-1] + add_z
					else:
						z_iner[i] = coord_last[2]
					
				else:
						y_iner[i]=coord_last[1]
						x_iner[i]=coord_last[0]
						z_iner[i]=coord_last[2]

				if case:
					pos_in = [round(x_iner[i],2),round(y_iner[i],2),round(z_iner[i],2)]
				else:
					if z_change :
						pos_in = [round(pos[0],2),round(pos[1],2),round(z_iner[i],2)]
					else:
						pos_in = [round(pos[0],2),round(pos[1],2),round(pos[2],2)]
				
				pos_in = checkCircularCollision(pos_in)

				q_in = inverseKinematics(pos_in,constrains,mode,changePositionFlag)
				
				[q_in,err]=checkAngularLimits(q_in,rev_max,rev_min)

				i = 0
				for i in range(len(q_in)):
					q_in[i] =	round(q_in[i],2)
				
				if err == 2:
					if changePositionFlag == 1: changePositionFlag = 0
					elif changePositionFlag == 0: changePositionFlag = 1
					return q_send,-1

				q_send.append(q_in)
			return q_send,0
	else:
		return 0,0

# this function evaluates which coordenate has changed and calculates the time to achive the movement
def getDelayTime(pos_new, pos_last, velocity, numberPoints):

	# calculate segment distance 
	d = np.sqrt(np.power((pos_new[0] - pos_last[0]),2) + np.power((pos_new[1] - pos_last[1]),2))

	move_time_xy = (round(d / (velocity*numberPoints) , 2))* 100
	if (move_time_xy == 0):
		move_time_xy = 1
	print("distance "+ str(d) + " in time "+str(move_time_xy))

	move_time_z =  round(abs(pos_new[2] - pos_last[2])/velocity, 2)*100
	if (move_time_z == 0):
		move_time_z = 1

	return move_time_xy,move_time_z # we have the total time in ms needed to make the movement for each segment

	
# check if we cant reach the given position 
def checkPosition(pos, rev_max,rev_min, constraints,mode):

	# here we check if we are inside the physics robot limits 
	if checkLimitsRange(pos) == 0:
		print(" Inside circular limits ")
		return 0
	# here we check angular limits
	q = inverseKinematics(pos,constraints,mode,changePositionFlag)
	[x,err]=checkAngularLimits(q,rev_max,rev_min)
	if err == 1:
		return 0

	return 1

def checkAngularLimits(q,rev_max,rev_min):
		# here we check if the position can be reach according with angular restrictions
	err = 0
	if q[1]>rev_max[1] or q[1] <rev_min[1]: # we must change the direction calculateted. The principal restriction is with the second joint because we can use multiplicity of solution to resolve any problem 
		print("out of angular range"+ str(q))
		if q[1] < 0: 
			q[1] = rev_min[1] 
		if q[1] > 0: 
			q[1] = rev_max[1]
		err = 1
	if q[0]>rev_max[0] or q[0] <rev_min[0]:
		print("change position mode")
		err = 2
		# we must change direction
	return q,err

# this function chec if we are inside the limit circunpherence 
def checkLimitsRange(pos):
	cr = np.power(pos[0],2) + np.power(pos[1],2)
	radius = np.power(INSIDE_RADIUS_LIMIT_CM,2)
	if (cr < radius) or (np.sqrt(np.power(pos[0],2)+np.power(pos[1],2)))>60:
		return 0 # unreachable position
	return 1

# this function is used during trayectory calculation to check if the point collisionate with the circunference. In this case the minimun position in set 
def checkCircularCollision(pos):
	if checkLimitsRange(pos) == 0:
		inside = np.power(INSIDE_RADIUS_LIMIT_CM,2)-np.power(pos[1],2)
		if inside > 0:
			pos[0] = np.sqrt(inside)
		print("new circular: "+ str(pos))
	return pos

# This function loads the second hand movement to change the movement direction

def changeDirectionTrayectory(lastPos,constraints,mode, n_points):
	global changePositionFlag
	if changePositionFlag == 1: chanf = 0
	elif changePositionFlag == 0: chanf = 1

	vector = []
	# looking for actual position 
	q = inverseKinematics (lastPos,constraints,mode,chanf)

	addq = q[1]/(n_points-1)

	# setting circular trayectory
	for i in range (n_points):
		q_cir = q[1] - addq*i
		vector.append([q[0],q_cir,q[2]])

	# Nww last position
	lastPos[0] = np.cos(q[0]/RAD_TOGRAD)*60
	lastPos[1] = np.sin(q[0]/RAD_TOGRAD)*60
	
	return vector, lastPos