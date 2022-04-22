

import numpy as np
import json
import time
import threading

import Movement_calc as Mov

from json_manager import *
from Defines_global import *

from manager import q

# cmd_sg_types = 

pckgdict = {
	"cmd":0,
	"mid":[],
	"data":[]
}

class Robot:

	# inicialización de conexion
	
	def __init__(self,name,constraints,pos_init,rev_max,rev_min,connectionObj):

		self.pos_init       	= pos_init
		self.constraints    	= constraints
		self.name           	= name
		self.coord_last     	= pos_init
		self.actual_pos			= pos_init
		self.connectionObj  	= connectionObj
		self.rev_max_limits 	= rev_max
		self.rev_min_limits 	= rev_min
		self.new_pos 			= 0
		self.last_target 		= 0
		self.new_target 		= 0
		self.movement_active 	= 0
		self.motors_number			= TOTAL_JOINTS
		self.robot_distance = 80

		# Json management
		self.json_status 		= json_manager()

		# constants
		self.packge_size 		= PACKAGE_SEGMENTS
		self.pointsPerCM	 	= 0
		self.rangePoints 		= Mov.getRangePointsForPlot(rev_max,constraints,2)

		# Inner vectors
		self.q_target 			= [0]*TOTAL_JOINTS # motors position to be set in the movement
		self.p_actual 			= [0,0,0] # actual position 	
		self.qOfPosition 		= []
		self.wOfPosition		= []
		self.delayMs 			= []
		self.timeDelay			= 0
		self.sizeqTosend		= 0
		self.send_pointer 		= 0
		self.numberOfPoints 	= 50
		self.flag_z_move		= 0
		self.flag_xy_move		= 0
		self.active_motors 		= [] #save the id of the motors that will be moved 
		self.velocityInCMpS 	= LINEAR_VEL # default velocity
		self.sendMode 			= POS_MODE
		self.packge_size 		= PACKAGE_SEGMENTS
		self.enable_robot 		= 0
		self.enable_motor_idle 	= []
		self.is_robot_connected = False
		self.connecting_timer 	= 0
		self.robot_moving_flag = 0
		self.homming_active = 0

		#thread for recepion msg

		#  status flags and data from reception json
		self.simMode            = 0
		self.connection         = 0
		self.toggle_connection  = 0
		self.send_buff_flag     = 0
		self.json_ready_flag    = 0
		self.json_ready_flag	= 0
		self.robot_power        = 0
		self.robot_hold         = 0
		self.robot_ls_reg       = 0
		self.hold_current		= [0]*TOTAL_JOINTS
		self.run_current		= [0]*TOTAL_JOINTS
		self.robot_fsr_array    = [0,0,0]
		self.motor_positions    = [0,0,0]
		self.movement_counter 	= 0
		self.cmd_connection_timer = 0
		self.moving_base_active = 0
		self.gripper_motor_id = 3
		self.grp_cm_rat = 0

		# homming management
		self.home_setting 		= False
		self.home_order_id 		= [2,0,1] # this is the motors order to make homming
		self.home_velocities 	= [-500,2000,-2000]
		self.home_return_pos 	= [100,500,500] # after reachinfthe LS the motor will return this value
		self.homing_counter 	= 0

		self.recept_thread = threading.Thread(target=self.reception_status_loop)
		self.recept_thread.setDaemon(True)
		self.recept_thread.start()

	#################################################################
	#################################################################


	# this is the reception thread used to load new data to json_status

	def reception_status_loop(self):
		while True:
			if self.connectionObj.getConnection():

				if self.connectionObj.getMode() == MODE_DEBUG or self.connectionObj.getMode() == MODE_COPPELIA_SIM:
					time.sleep(1)
					if self.is_robot_connected != True:
						self.moving_base_active = 1
						self.is_robot_connected = True
						self.p_actual = [60,0,30]
						self.constraints = [35,25,30]
				else:
					# send connection msg 
					dif = time.perf_counter() - self.cmd_connection_timer
					if dif >= CMD_CONNECTION_TOUT:
						self.cmd_connection_timer =  time.perf_counter()
						self.connectionObj.send_new_mesage("{cmd:5010}") # sending connection status

					msg = self.connectionObj.receiveMsg()
					if msg != 0:
						print("RECEIVED: "+msg)
						
						# self.check_initMSG()

						if self.json_status.json_loadString(msg):
							if self.is_robot_connected == False:
								dif = time.perf_counter() - self.connecting_timer
								try:
									self.name = self.json_status.json_getValue("ROBOT_NAME")
									if self.name!='error_reading_json':
										# self.gripper_motor_id = self.json_status.json_getValue("GRP_ID")
										self.motors_number = self.json_status.json_getValue("MOT_NUMBER")
										self.movement_active = self.json_status.json_getValue("MOV_BASE")
										self.constraints = self.json_status.json_getValue("CONSTRAINTS")
										self.is_robot_connected = True
								except:
									if dif >= CONNECTION_TOUT:
										self.toggleConnection()
							else:
								self.timer_connection_tout  = 0 # reset timer
								self.send_buff_flag         = self.json_status.json_getValue("BUFF")
								if self.send_buff_flag!='error_reading_json':
									self.json_ready_flag        = self.json_status.json_getValue("JSON")
									self.robot_moving_flag      = self.json_status.json_getValue("BUFF_LOAD")
									self.robot_power            = self.json_status.json_getValue("MOT_ACTIVE")
									self.robot_hold             = self.json_status.json_getValue("MOT_HOLD")
									self.robot_ls_reg           = self.json_status.json_getValue("LS")
									self.robot_fsr_array        = self.json_status.json_getValue("FSR")
									self.motor_positions        = self.json_status.json_getValue("MOT_POS")
									self.hold_current 			= self.json_status.json_getValue("MOT_IHOLD")
									self.run_current 			= self.json_status.json_getValue("MOT_IRUN")
									# update positions
									self.p_actual = Mov.get_position_DK([self.motor_positions[0]/100,self.motor_positions[1]/100,self.motor_positions[2]/100],self.constraints)

							self.connectionObj.rest_connection_tout()						
							
						## if there is a moving active check if we have reached the position
						if self.movement_active:
							time_dif = time.perf_counter()-self.movement_counter
							if (time_dif) >= MAX_MOVEMENT_TOUT_SEC:
								print("Movement TOUT, reset counter . . . ")
								self.movement_counter = 0
								self.movement_active = 0
							rest_0 = abs(self.q_target[0]*100 - self.motor_positions[0])
							rest_1 = abs(self.q_target[1]*100 - self.motor_positions[1])
							rest_2 = abs(self.q_target[2]*100 - self.motor_positions[2])
							if rest_0 < 100 and rest_1 < 100 and rest_2 < 10:
								self.movement_active = 0

						if self.robot_moving_flag == 0 and self.homming_active:
							self.homming_active = 0
							time.sleep(1)
							self.connectionObj.send_new_mesage('{cmd:'+str(CMD_SET_ACTUAL_POS)+',motors:[0,1,2,3],values:[10500,-2000,0,0]}')

			else:
				self.name = ""
				time.sleep(1)
				self.is_robot_connected = False
			time.sleep(STATUS_PROCESS_DELAY)
	
	#################################################################
	#################################################################

	def is_connected(self):
		return self.is_robot_connected

	def toggleConnection(self):
		self.connectionObj.toggleConnection()
		if self.is_robot_connected:
			self.is_robot_connected = False
		else:
			self.connectionObj.send_new_mesage("{cmd:5010}")
			self.connecting_timer = time.perf_counter()


	# status set and get functions
	def is_motorEnable(self, mot_id):
		for i in range(len(self.enable_motor_idle)):
			if self.enable_motor_idle[i] == mot_id:
				return 1
		return 0 # motor not enabled

	def is_powered(self):
		if self.connectionObj.getMode() == MODE_DEBUG or self.connectionObj.getMode() == MODE_COPPELIA_SIM:
			return 1
		return self.robot_power

	def isNewPositionActive(self):
		return self.movement_active

	def setPointsPer_cm(self,points):
		self.pointsPerCM = points

	def setSendMode(self,mode):
		self.sendMode = mode
		self.connectionObj.setCommandMode(mode)

	def setNumberPonitForMovement(self, points):
		self.numberOfPoints = points

	def setVelocityForMovement(self, vel):
		self.velocityInCMpS = vel

	def save_Move(self):
		move = 0

	def sendNextPackage(self):
		if self.flag_xy_move == 1:
			data = []
			if self.sendMode == VEL_MODE:
				pckgdict["cmd"] = CMD_SETVELOCITIES
				for i in range(self.packge_size-1):
					data.append(self.wOfPosition[self.send_pointer][0])
					data.append(self.timeDelay)
					data.append(self.wOfPosition[self.send_pointer][1])
					data.append(self.timeDelay)
					self.send_pointer += 1
					if self.send_pointer >= self.sizeqTosend-1:
						self.flag_xy_move = 0
						self.send_pointer = 0
						self.timeDelay = []
						self.wOfPosition = []
						break
			
			elif self.sendMode == POS_MODE:
				pckgdict["cmd"] = CMD_SETPOSITIONS
				for i in range(self.packge_size-1):
					data.append(int(100*self.qOfPosition[self.send_pointer+1][0]))
					data.append(int(100*self.wOfPosition[self.send_pointer][0]))
					data.append(int(100*self.qOfPosition[self.send_pointer+1][1]))
					data.append(int(100*self.wOfPosition[self.send_pointer][1]))
					self.send_pointer += 1
					if self.send_pointer >= self.sizeqTosend-1:
						self.flag_xy_move = 0
						self.send_pointer = 0
						self.wOfPosition = []
						self.qOfPosition = []
						break
			else:
				return 0	
			pckgdict["data"] = data
			pckgdict["mid"]  = [0,1]
			self.connectionObj.send_new_mesage(json.dumps(pckgdict,separators=(',', ':')))
			q.put((SEND_PCKG))
		else:
			if self.flag_z_move == 1: 
				self.flag_z_move = 0
				# self.robot_moving_flag  		= 0
				pckgdict["cmd"] = CMD_SETPOSITIONS
				pckgdict["data"] = [self.zPos,self.zVel]
				pckgdict["mid"]  = [2]
				self.connectionObj.send_new_mesage(json.dumps(pckgdict,separators=(',', ':')))
			self.send_pointer 				= 0
			# self.robot_moving_flag  		= 0
			self.new_pos 					= 0
			self.wOfPosition = []
			self.qOfPosition = []
			self.timeDelay = []

	def setNewCurrent(self,mot_id,h_current,r_current):
		values=[]
		self.enable_motor_idle = []
		rst_id = []

		if len(mot_id):
			# check if current has chaged
			change = False
			for i in range(len(h_current)):
				if self.hold_current[mot_id[i]] != h_current[i]:
					change = True
					self.hold_current[mot_id[i]] = h_current[i]
			for i in range(len(r_current)):
				if self.run_current[mot_id[i]] != r_current[i]:
					change = True
					self.run_current[mot_id[i]] = r_current[i]

			# save new data
			for i in range(len(mot_id)):
				self.enable_motor_idle.append(mot_id[i]) # save new enabled motors
				values.append(h_current[i])
				values.append(r_current[i])
			
			if change == False:
				return

			for i in range(self.motors_number):
				reset = True
				for k in range(len(mot_id)):
					if i == mot_id[k]:
						reset = False
						break
				if reset:
					rst_id.append(i)

			self.reset(rst_id)	
			str_vals = str(values).replace(" ", "")
			str_ids = str(mot_id).replace(" ", "")
			command = '{cmd:'+str(CMD_SET_CURRENT_REG)+',motors:'+str_ids+',values:'+str_vals+'}'
			self.connectionObj.send_new_mesage(command)
			# print(command)
		else:
			self.reset()
		return 

	#Movement
	def send_qPos(self,mot_id, pos_q, vel):
		self.connectionObj.send_new_mesage('{cmd:5012,motors:['+str(mot_id)+'],values:['+str(pos_q)+','+str(vel)+']}')

	def move_Robot(self,pos):
		if(self.movement_active == 0):
			if self.p_actual != pos:
				# check posibility of movement
				if Mov.checkPosition(pos,self.rev_max_limits,self.rev_min_limits,self.constraints,self.connectionObj.simMode) == 1:

					#get the values for motor 0 and 1 that describe the x-y
					[self.qOfPosition,self.sizeqTosend] = Mov.moveTrajectory(pos,self.p_actual,self.numberOfPoints,self.rev_max_limits,self.rev_min_limits,self.constraints, self.connectionObj.simMode)
					i_q_aux = len(self.qOfPosition)-1
					for i in range(len(self.qOfPosition[i_q_aux])):
						if i == 1:
							self.q_target[i] = self.qOfPosition[i_q_aux][1] - self.qOfPosition[i_q_aux][0]
						else:
							self.q_target[i] = self.qOfPosition[i_q_aux][i]
					#if we are usin copelia
					if self.connectionObj.simMode == 1:
						self.movement_active  = 1
						self.new_pos 			= 1
						for i in range(self.sizeqTosend):
							self.qOfPosition[i][2] = -1*self.qOfPosition[i][2]
							self.connectionObj.setRobotPos(self.qOfPosition[i])
							time.sleep(1/100)
						self.movement_active  = 0
						self.p_actual 		  = pos
						return 

					#the motor z will always be controlled by velocity and time 
					[self.timeDelay,self.zDelay ] = Mov.getDelayTime(pos,self.p_actual,self.velocityInCMpS,self.sizeqTosend)

					#check what we need to move
					if pos[0] !=self.p_actual[0] or pos[1] !=self.p_actual[1]:
						self.flag_xy_move		= 1
					if pos[2] !=self.p_actual[2]:
						self.flag_z_move		= 1
						self.zDelay 			= (int((abs(self.q_target[2] - self.p_actual[2])*1000/self.velocityInCMpS)))
						self.zPos 				= int(self.q_target[2]*100)
						self.zVel 				= self.velocityInCMpS*100
					elif self.flag_xy_move:
						self.zPos 				= 0
						self.zVel 				= self.velocityInCMpS*100
						self.connectionObj.send_new_mesage('{cmd:'+str(CMD_SETPOSITIONS)+',motors:[2],values:['+str(self.zPos )+','+str(self.zVel )+']}')
						self.q_target[2] = 0

					#check what we need to move
					if self.flag_z_move == 0 and self.flag_xy_move ==0:
						self.movement_active  = 0
						return 0

					#copy last position
					self.last_target = self.new_target
					self.new_target = pos

					# ##
					self.setVelocitiesToRobot()
					self.movement_active  = 1
					self.movement_counter = time.perf_counter()
					q.put((SEND_PCKG))
					return 1
				else:
					return 0
			else:
				print("Robot placed in position already")
				return 1
		else:
			print("robot moving")
			return 0
	
	# def get_positionWWithDirectK():

	def setVelocitiesToRobot(self): #calculate the velocity between the 2 consecutives positions 
		acel_count = 0
		deacel_count = 0
		first_thld = int((len(self.qOfPosition)-1)*0.10)  # for acceleration process
		second_thld = int((len(self.qOfPosition)-1)*0.90) # for deacceleration process

		for i in range(len(self.qOfPosition)-1):
			lastPos = np.array(self.qOfPosition[i])
			newPos 	= np.array(self.qOfPosition[i+1])
			vel 	= (newPos - lastPos )*100/self.timeDelay
			vel[0] 	= round(vel[0],2)
			vel[1] 	= round(vel[1],2)
			if vel[0] < 0 :
				vel[0]*=-1
			if vel[1] < 0 :
				vel[1]*=-1
			
			# acceleration and deacceleration control

			if i < first_thld:
				acel_count += 1
				vel = vel*(acel_count / first_thld)
			elif i > second_thld:
				deacel_count += 1
				vel = vel - vel*(deacel_count / ((len(self.qOfPosition)-1)-second_thld))

			self.wOfPosition.append(vel)
			self.delayMs.append(self.timeDelay)
		
	def move_Home(self):
		self.connectionObj.send_new_mesage('{cmd:5006,motors:[2],values:[-500,100]}')
		self.connectionObj.send_new_mesage('{cmd:5006,motors:[1],values:[-2000,500]}')
		self.connectionObj.send_new_mesage('{cmd:5006,motors:[0],values:[2000,500]}')
		self.homming_active = 1
		return

	def toggle_robot_en(self):
		if len(self.enable_motor_idle):
			if self.enable_robot:
				self.enable_robot = 0
				self.connectionObj.send_new_mesage('{cmd:'+str(CMD_MOTOR_EN)+',motor_id:'+str(self.enable_motor_idle).replace(" ", "")+'}')
			else:
				self.enable_robot = 1
				self.connectionObj.send_new_mesage('{cmd:'+str(CMD_MOTOR_DIS)+',motor_id:'+str(self.enable_motor_idle).replace(" ", "")+'}')
			return 100
		else:
			print("there is no motors enabled, check Edit->Motors")
		return 0
	

	def set_Initpos(self,pos):
		self.pos_init = pos
		self.move_Robot(self.pos_init)
		return 

	def reset(self, mid = None):
		if mid == None:
			mid = []
			for i in range(self.motors_number):
				mid.append(i)
		self.connectionObj.send_new_mesage('{cmd:'+str(CMD_RESET_MOTORS)+',motors:'+str(mid).replace(" ", "")+'}')

	def setGripperRatio(self,ratio):
		self.grp_cm_rat = ratio
	
	def Close_Gripper(self):
		self.connectionObj.send_new_mesage('{cmd:5002,motor_id:['+str(self.gripper_motor_id)+'],val:[350,500]}')
		self.connectionObj.gripper_control(0.1)
	
	def Open_Gripper(self):
		end_pos = self.grp_cm_rat
		self.connectionObj.send_new_mesage('{cmd:5002,motor_id:['+str(self.gripper_motor_id)+'],val:['+str(end_pos)+',500]}')
		self.connectionObj.gripper_control(-0.1)
