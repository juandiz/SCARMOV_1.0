


from Movement_calc import RAD_TOGRAD
from CopeliaSim_def import *

import sim 
import time

class Coppelia():

	def __init__ (self,name):
		self.port = PORT_COPPELIA_DEFAULT
		self.IP   = IP_COPPELIA_DEFAULT
		self.name = name
		self.direction_movement = 0
		self.clientID = -1
		self.connectet_sim = 0
		#Starting Gripper

		self.set_GripperHndlr(grip_hdlrs)

		#Starting RObot

		self.set_LJoints(linear_joinst)
		self.set_RJoints(revolt_joints)
		self.set_MJoints(motor_joints)

		print (f"Init CoppeliaSIm with port {self.port} and IP "+ IP_COPPELIA_DEFAULT)

	def setParams(self,port,ip):
		self.port = port
		self.IP   = ip
	
	def changeConnectionType(self,type):
		self.connection_type = type

	def getName(self):
		return self.name

	def getParms(self):
		return self.port,self.IP

	def close(self):
		# sim.simxStopSimulation(self.clientID,sim.simx_opmode_streaming)
		# self.clientID = -1
		# sim.simxFinish(self.clientID)
		return 

	def connect(self):
		print("trying to connect CoppeliaSim")
		if self.connectet_sim == 0:
			self.clientID=sim.simxStart(self.IP,self.port,True,True,2000,5) # Connecting
			print(self.clientID)
			if self.clientID < 0:
				return 0
			self.get_Hndlrs()
			self.connectet_sim = 1
		else:	
			return 1	

	## function to use 
	def setGrippervel(self,vel):
		for i in range(len(self.gpj_hdlrs)):
			retCode = sim.simxSetJointTargetVelocity(self.clientID, self.gpj_hdlrs[i],vel,sim.simx_opmode_streaming)

	def setRobotPos(self,q):
		for i in range(REVOLT_JOINT):
			self.set_jointPos(self.rj_hdlrs[i],q[i]/RAD_TOGRAD)
		for i in range(LINEAR_JOINT):
			self.set_jointPos(self.lj_hdlrs[i],q[i+2]/100) # working with cms

	def setRobotHome(self):
		print("home coppelia")

	#############################################################################

	def set_Vel(self,vel):

		retCode = sim.simxSetJointTargetVelocity(self.clientID, self.mj_hdlrs[0],vel[0],sim.simx_opmode_streaming)
		retCode = sim.simxSetJointTargetVelocity(self.clientID, self.mj_hdlrs[1],vel[1],sim.simx_opmode_streaming)

	def get_Hdlr(self, hdlr_name):
		retCode,hdlr=sim.simxGetObjectHandle(self.clientID, str(hdlr_name) ,sim.simx_opmode_blocking)
		return hdlr

	def set_jointPos(self,hdlr,pos):
		#self.retCode,hdlr=sim.simxGetObjectHandle(self.clientID, hdlr_name,sim.simx_opmode_blocking)
		retCode = sim.simxSetJointTargetPosition(self.clientID, hdlr,pos, sim.simx_opmode_oneshot)

	def receiveMsg(self):
		id=sim.simxGetConnectionId(self.clientID)
		time.sleep(1) # this fucntion is called by reception thread and waits every 1 sec to check connection with coppelia sim
		return id

	def get_Hndlrs(self):
		for i in range(LINEAR_JOINT):
			self.lj_hdlrs[i] = self.get_Hdlr(self.lj_hdlrs[i])
		for i in range(REVOLT_JOINT):
			self.rj_hdlrs[i] = self.get_Hdlr(self.rj_hdlrs[i])
		for i in range(MOTORS):
			self.mj_hdlrs[i] = self.get_Hdlr(self.mj_hdlrs[i])
		for i in range(GRIPP_JOINTS):
			self.gpj_hdlrs[i] = self.get_Hdlr(self.gpj_hdlrs[i])

	def set_LJoints(self,joint_array):
		self.lj_hdlrs=[0]*len(joint_array)
		self.lj_max  =[0]*len(joint_array)
		self.lj_min  =[0]*len(joint_array)
		for i in range(len(joint_array)):
			self.lj_hdlrs[i] = joint_array[i]

	def set_RJoints(self,joint_array):
		self.rj_hdlrs=[0]*len(joint_array)
		self.rj_max  =[0]*len(joint_array)
		self.rj_min  =[0]*len(joint_array)
		for i in range(len(joint_array)):
			self.rj_hdlrs[i] = joint_array[i]

	def set_MJoints(self,joint_array):
		self.mj_hdlrs=[0]*len(joint_array)
		for i in range(len(joint_array)):
			self.mj_hdlrs[i] = joint_array[i]

	def set_GripperHndlr(self,joint_array):
		self.gpj_hdlrs=[0]*len(joint_array)
		for i in range(len(joint_array)):
			self.gpj_hdlrs[i] = joint_array[i]

		#Send via Api functions
	def set_Position(self, hdlr, pos):
		self.set_jointPos(hdlr,pos)

	def gripper_open_close(self, vel):
		err = sim.simxSetJointTargetVelocity(self.clientID, self.gpj_hdlrs[0],vel,sim.simx_opmode_streaming)
		err = sim.simxSetJointTargetVelocity(self.clientID,self.gpj_hdlrs[1],vel/4,sim.simx_opmode_streaming)
		print ("ERR: "+str(err))
	