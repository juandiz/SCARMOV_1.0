


class Gripper:

	def __init__(self, name):
		self.name = name
		print ("Im the Gripper " + name)

	def Open(self, vel):
		self.api.set_Vel(self.gripper_hdlr[0],vel)
		self.api.set_Vel(self.gripper_hdlr[1],vel)

	def Close(self,vel):
		self.api.set_Vel(self.gripper_hdlr[0],-vel)
		self.api.set_Vel(self.gripper_hdlr[1],-vel)