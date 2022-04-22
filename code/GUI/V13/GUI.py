###############################################################
# modules from third parties
import time
from pubsub import pub

from tkinter import *
import tkinter

import tkinter.font as TkFont

from Defines_global import *
from manager import q

###############################################################

##############################################################
# Drawing functions
##############################################################

def createCircle(self,x,y,r,**args):
	return self.create_oval(x-r, y-r, x+r, y+r, **args)

tkinter.Canvas.create_circle = createCircle # crete circle with canvas 

def getPixelPosition(pos):
	p_x = (pos[0]/M_X) + P0_X
	p_y = (pos[1]/M_Y) + P0_Y
	return [p_x,p_y]

###############################################################

class GUI():

	TOTAL_JOINTS= 0

	def __init__(self,img,robot,connection):
		self.daemon = True
		self.img   = img
		self.root = Tk() ## create the app window

		# one pixel size reference
		self.pixelVirtual = tkinter.PhotoImage(width=1, height=1)
		
		# Fonts
		self.MonserratFont_8b = TkFont.Font(family="Monserrat",size=8,weight="bold")
		self.MonserratFont_10b = TkFont.Font(family="Monserrat",size=10,weight="bold")
		self.MonserratFont_12b = TkFont.Font(family="Monserrat",size=12,weight="bold")
		self.MonserratFont_14b= TkFont.Font(family="Monserrat",size=14,weight="bold")
		self.MonserratFont_8 = TkFont.Font(family="Monserrat",size=8)
		self.MonserratFont_16b = TkFont.Font(family="Monserrat",size=16,weight="bold")
		self.MonserratFont_10 = TkFont.Font(family="Monserrat",size=10)
		self.MonserratFont_12 = TkFont.Font(family="Monserrat",size=12)
		self.MonserratFont_14= TkFont.Font(family="Monserrat",size=14)
		self.MonserratFont_16 = TkFont.Font(family="Monserrat",size=16)

		# Connection Mode
		self.simMode = 0 # set simulation with coppelia false by default

		self.buttons_disable 	= 0
		self.last_power	 		= -1
		self.last_hold 			= -1
		self.last_fsr_top 		= -1
		self.last_fsr_mid 		= -1 
		self.last_fsr_bot 		= -1 #
		self.last_mot_pos 		= [-1]*TOTAL_JOINTS
		self.last_pos 			= [-1,-1,-1]
		self.last_ls 			= 0

		self.robot = robot
		self.connection = connection

		# GUI declaration
		self.root.title(self.robot.name)
		self.root.iconbitmap(self.img)
		self.root.resizable(width=False, height=False)
		
		self.openFiles()
		self.setMenu()
		self.set_movementRobotButtons()
		self.set_States("Disconnected")
		self.set_logicButtons()
		self.createSensorControlCanvas()
		self.init_directKinematicCanvas()
		self.createCoordenatesCanvas()
		self.createPlotCanvas()
		self.createGripperControlCanvas()

		# subcription to update state
		pub.subscribe(self.set_States, "update" )
		# pub.subscribe(self.setNewSensorsValues, "Sensors update" )
		pub.subscribe(self.stateDisplay,"State Display")

	############################################################################################################################################
	# Subcriptions functions 
	############################################################################################################################################

	def set_States(self,State):
		print(State)
		self.e = Label(self.root, text= State, font= self.MonserratFont_10b,background=STATUS_BG, relief=SUNKEN, bd=1, anchor=E)
		self.e.grid(row=11,column=0, columnspan=7,sticky=W+E)
		
		#this function get the pixels of the img and transforms if to coordenates
	
	def stateDisplay(self):
		# update positions
		if self.last_pos[0] != self.robot.p_actual[0]:
			self.last_pos[0] = self.robot.p_actual[0]
			self.x_input.delete(0,END)
			self.x_input.insert(0, self.last_pos[0])
		if self.last_pos[1] != self.robot.p_actual[1]:
			self.last_pos[1] = self.robot.p_actual[1]
			self.y_input.delete(0,END)
			self.y_input.insert(0, self.last_pos[1])
		if self.last_pos[2] != self.robot.p_actual[2]:
			self.last_pos[2] = self.robot.p_actual[2]
			self.z_input.delete(0,END)
			self.z_input.insert(0, self.last_pos[2])

		if self.robot.is_connected() == 1: # if connected update new data

			if self.buttons_disable == 0:
				self.toggle_widgetsFromConnection()

			# motors enabled check
			if self.last_hold != self.robot.robot_hold:
				self.last_hold = self.robot.robot_hold
				if(self.last_hold):
					self.Buton_on_off['image'] = self.on_off_g
				else:
					self.Buton_on_off['image'] = self.on_off_r
			
			#FSR update
			if self.last_fsr_mid != self.robot.robot_fsr_array[1]:
				self.last_fsr_mid = self.robot.robot_fsr_array[1]
				self.FSR_midVal.delete(0,END)
				self.FSR_midVal.insert(0,self.last_fsr_mid)
			if self.last_fsr_top != self.robot.robot_fsr_array[2]:
				self.last_fsr_top = self.robot.robot_fsr_array[2]
				self.FSR_topVal.delete(0,END)
				self.FSR_topVal.insert(0,self.last_fsr_top)		
			if self.last_fsr_bot != self.robot.robot_fsr_array[0]:
				self.last_fsr_bot = self.robot.robot_fsr_array[0]
				self.FSR_botVal.delete(0,END)
				self.FSR_botVal.insert(0,self.last_fsr_bot)

			#update position of robots
			for i in range(self.robot.motors_number):
				if self.last_mot_pos[i] != self.robot.motor_positions[i]:
					self.last_mot_pos[i] = self.robot.motor_positions[i]
					self.q_out[i].delete(0,END)
					self.q_out[i].insert(0,str(self.last_mot_pos[i]/DATA_SCALE))

			#LS update 
			if  self.last_ls != self.robot.robot_ls_reg:
				self.last_ls =  self.robot.robot_ls_reg
				self.updateLSRLed(self.last_ls)

			#update power status
			if self.last_power != self.robot.robot_power:
				self.last_power = self.robot.robot_power
				self.display_power_status(self.robot.robot_power)

		elif self.buttons_disable:
			# Disable if not connected
			self.toggle_widgetsFromConnection()
		
	def updatePlot(self,point):
		self.my_canvas_plot.create_oval()
		return

	################################################################################################################################################################
	# tkinter function implementation
	################################################################################################################################################################

	def openFiles(self):
		#Buttons images
		self.gripperHoldImg 	= PhotoImage(file='IMG/holdButton.png')
		self.gripperReleaseImg 	= PhotoImage(file='IMG/releaseButton.png')
		self.connetRImg 		= PhotoImage(file='IMG/connectRButton.png')
		self.connetGImg 		= PhotoImage(file='IMG/connectGButton.png')
		self.loadImg 			= PhotoImage(file='IMG/loadButton.png')
		self.homeImg 			= PhotoImage(file='IMG/homeButton.png')
		self.savePodImg 		= PhotoImage(file='IMG/saveposButton.png')
		self.forwardImg 		= PhotoImage(file='IMG/forwardButton.png')
		self.backwardImg 		= PhotoImage(file='IMG/backwardButton.png')
		self.rigthImg 			= PhotoImage(file='IMG/rigthButton.png')
		self.leftImg 			= PhotoImage(file='IMG/leftButton.png')
		self.stopImg 			= PhotoImage(file='IMG/stopButton.png')
		self.on_off_r 			= PhotoImage(file='IMG/on_off_r.png')
		self.on_off_g 			= PhotoImage(file='IMG/on_off_1.png')
		self.reset_img 			= PhotoImage(file='IMG/reset.png')

	##############################################################
	# separation of main window with canvas 
	##############################################################

	def createGripperControlCanvas(self):
		self.my_canvas_gripper= Canvas(self.root, width=150, height=110, background= BG_CANVAS_MOTORS)
		self.my_canvas_gripper.create_text(73,15,text="Gripper Command",font= self.MonserratFont_10b, fill= TITTEL_CANVAS)
		self.Button_Release = Button(self.my_canvas_gripper,activebackground=BG_CANVAS_MOTORS, background=BG_CANVAS_MOTORS, image=self.gripperHoldImg,compound="c",borderwidth=0, command= lambda :self.Grip(1),state= 'disable')
		self.Button_Hold = Button(self.my_canvas_gripper,background=BG_CANVAS_MOTORS,activebackground=BG_CANVAS_MOTORS,image=self.gripperReleaseImg,compound="c",borderwidth=0,command= lambda: self.Grip(0),state= 'disable')
		self.Button_Release.place(x = 35, y = 30 )
		self.Button_Hold.place(x = 35, y = 70 )

		self.my_canvas_gripper.grid(row = 3, column= 0)

	##################################################################################
	# functions for Plot Canvas
	##################################################################################

	def createPlotCanvas(self):
		self.my_canvas_plot = Canvas(self.root, width=PLOT_TOTAL, height=PLOT_TOTAL, background= 'white')
		self.my_canvas_plot.grid(row=0,column=3, rowspan = 4 )
		self.my_canvas_plot.bind("<Button 1>",self.getPos)
		self.my_canvas_plot.create_text(PLOT_TOTAL/2,PLOT_TOTAL/2,text = "Robot not connected",fill='grey',font = self.MonserratFont_12)
		self.errase_text = 1
	
	def update_plot_canvas(self):
		#Draw range 
		positions = []

		if self.errase_text:
			self.errase_text = 0
			self.my_canvas_plot.create_rectangle(PLOT_TOTAL/2 - 100,PLOT_TOTAL/2-10,PLOT_TOTAL/2 + 100,PLOT_TOTAL/2+10,fill='white',outline='white')

		for i in range(int(len(self.robot.rangePoints))):
			[x,y]=getPixelPosition(self.robot.rangePoints[i])
			positions.append(x)
			positions.append(y) 
		self.my_canvas_plot.create_polygon(positions,fill= RANGE_ROBOT_COLOR, outline="black")

		self.my_canvas_plot.create_line(P0_X,P60_Y ,P0_X,Pneg60_Y,width=2)
		self.my_canvas_plot.create_line(P60_X,P0_Y,Pneg60_X,P0_Y,width=2)

		#draw coordenates
		for i in range(13):
			value = (i - 6)*10
			if value == 0:
				offset = 5
			else:
				offset = 0
			self.my_canvas_plot.create_text((i*distance)+offset+PLOT_BORDER,init0_0[1] + 7+PLOT_BORDER,text = str(value),font = self.MonserratFont_8)
			self.my_canvas_plot.create_text((init0_0[0]-10)+PLOT_BORDER,(i*distance) - offset+PLOT_BORDER,text = str(-value),font = self.MonserratFont_8)
			self.my_canvas_plot.create_line((i*distance)+PLOT_BORDER,init0_0[1]+PLOT_BORDER,(i*distance)+PLOT_BORDER,init0_0[1]-5+PLOT_BORDER,width=2)
			self.my_canvas_plot.create_line((init0_0[0])+PLOT_BORDER,(i*distance)+PLOT_BORDER,(init0_0[0]+5)+PLOT_BORDER,(i*distance)+PLOT_BORDER,width=2)
	
	def getPos(self,eventorigin):

		if self.robot.is_connected():
			#Draw circle Point
			x = eventorigin.x
			y = eventorigin.y
			
			self.update_plot_canvas()
			self.my_canvas_plot.create_circle(x, y, 1, fill="red")
			
			self.last_point_in_plot = [x,y]

			m_x = (60)/(P60_X - P0_X)
			f_x = m_x*(x - P0_X)

			m_y = (60)/(P60_Y - P0_Y)
			f_y = m_y*(y-P0_Y)

			#passing pixels to coordenates in cms
			try:
				x = round(f_x,1)
				y = round(f_y,1)
				z = round(float(self.z_input.get()),2)
				
				q.put((NEW_POS,[x,y,z]))
				print(x,y,z)
			except:
				pub.sendMessage("update", State= "ERROR. Check loaded values . . ." )

	##################################################################################
	##################################################################################
	##################################################################################
	
	def createCoordenatesCanvas(self):

		self.my_canvas_Coord = Canvas(self.root, width=150, height=225, background= BG_CANVAS_MOTORS)
		self.my_canvas_Coord.create_text(80,25,text="Coordenates",font= self.MonserratFont_10b, fill= TITTEL_CANVAS)

		self.my_canvas_Coord.create_text(20,60,text="x",font= self.MonserratFont_10, fill= TITTEL_CANVAS)
		self.my_canvas_Coord.create_text(120,60,text="cm",font= self.MonserratFont_10, fill= TITTEL_CANVAS)
		self.x_input = Entry(self.my_canvas_Coord, width=10, borderwidth=5)
		self.x_input.place(x = 35,y=50)
		# self.x_input.insert(0,f"{float(self.robot.actual_pos[0]):.2f}")

		self.my_canvas_Coord.create_text(20,110,text="y",font= self.MonserratFont_10, fill= TITTEL_CANVAS)
		self.my_canvas_Coord.create_text(120,110,text="cm",font= self.MonserratFont_10, fill= TITTEL_CANVAS)
		self.y_input = Entry(self.my_canvas_Coord, width=10, borderwidth=5)
		self.y_input.place(x = 35,y=100)
		# self.y_input.insert(0,f"{float(self.robot.actual_pos[1]):.2f}")

		self.my_canvas_Coord.create_text(20,160,text="z",font= self.MonserratFont_10, fill= TITTEL_CANVAS)
		self.my_canvas_Coord.create_text(120,160,text="cm",font= self.MonserratFont_10, fill= TITTEL_CANVAS)
		self.z_input = Entry(self.my_canvas_Coord, width=10, borderwidth=5)
		self.z_input.place(x = 35,y=150)
		# self.z_input.insert(0,f"{float(self.robot.actual_pos[2]):.2f}")

		self.my_canvas_Coord.grid(row=1,column=2, rowspan = 4)

	def createSensorControlCanvas(self):
		self.my_canvasSensor = Canvas(self.root, width=150, height=110, background= BG_CANVAS_MOTORS)
		self.my_canvasSensor.create_text(70,10,text="Gripper Sensing",font= self.MonserratFont_10b, fill= TITTEL_CANVAS)

		self.my_canvasSensor.create_text(40,35,text="FSR_TOP",font= self.MonserratFont_10, fill= TITTEL_CANVAS)
		self.FSR_topVal = Entry(self.my_canvasSensor, width=10, borderwidth=5)

		self.my_canvasSensor.create_text(40,65,text="FSR_MID",font= self.MonserratFont_10, fill= TITTEL_CANVAS)
		self.FSR_midVal = Entry(self.my_canvasSensor, width=10, borderwidth=5)

		self.my_canvasSensor.create_text(40,95,text="FSR_BOT",font= self.MonserratFont_10, fill= TITTEL_CANVAS)
		self.FSR_botVal = Entry(self.my_canvasSensor, width=10, borderwidth=5)

		self.FSR_topVal.place(x = 75, y = 20 )
		self.FSR_midVal.place(x = 75, y = 50 )
		self.FSR_botVal.place(x = 75, y = 80 )

		self.my_canvasSensor.grid(row=1, column = 0)

	def updateFSRValue(self,value):
		self.FSR_botVal.delete(0,END)
		self.FSR_botVal.insert(0,value[0])
		self.FSR_midVal.delete(0,END)
		self.FSR_midVal.insert(0,value[1])
		self.FSR_topVal.delete(0,END)
		self.FSR_topVal.insert(0,value[2])

	##################################################################################
	# functions for Direct kinematics Canvas
	##################################################################################
	def init_directKinematicCanvas(self):
		self.my_canvas_dirKin = Canvas(self.root, width=150, height=225, background= BG_CANVAS_MOTORS)
		self.my_canvas_dirKin.create_text(80,25,text="Direct Kinematics",font= self.MonserratFont_10b, fill= TITTEL_CANVAS)	
		self.my_canvas_dirKin.grid(row=1,column=1, rowspan = 4)

	def active_DirectKinematicCanvas(self):
		self.ls_q = []
		self.q_out=[0]*(TOTAL_JOINTS)
		self.y_def = 40
		for i in range(TOTAL_JOINTS):
			self.my_canvas_dirKin.create_text(110,65+self.y_def*i,text="LS",font= self.MonserratFont_10, fill= TITTEL_CANVAS)
			self.my_canvas_dirKin.create_oval(125,55+self.y_def*i,145,75+self.y_def*i,fill= LSR_LED_OFF, outline= LSR_LED_BRDR)

			self.my_canvas_dirKin.create_text(15,65+self.y_def*i,text="q"+str(i),font= self.MonserratFont_10, fill= TITTEL_CANVAS)
			self.q_out[i] = Entry(self.my_canvas_dirKin, width=10, borderwidth=5)
			self.q_out[i].place( x = 25 , y=(self.y_def*i + 50))
	
	def updateLSRLed(self, bin_value):
		for i in range(TOTAL_JOINTS):
			if (bin_value & 1<<i):
				self.my_canvas_dirKin.create_oval(125,55+self.y_def*i,145,75+self.y_def*i,fill= LSR_LED_ON, outline= LSR_LED_BRDR)
			else:
				self.my_canvas_dirKin.create_oval(125,55+self.y_def*i,145,75+self.y_def*i,fill= LSR_LED_OFF, outline= LSR_LED_BRDR)
	##################################################################################
	##################################################################################
	##################################################################################

	def set_logicButtons(self):
	
		self.button_LogicCanvas = Canvas(self.root, width=150,height=220,background=BG_CANVAS_MOTORS,state= 'disable')
		self.button_LogicCanvas.create_text(70,15,text="General",font= self.MonserratFont_10b, fill= TITTEL_CANVAS)
		self.Button_Load = Button(self.button_LogicCanvas,activebackground=BG_CANVAS_MOTORS, background=BG_CANVAS_MOTORS,image=self.loadImg,borderwidth=0, command=lambda: self.Load(1),state= 'disable')
		self.Button_Connect = Button(self.button_LogicCanvas,activebackground=BG_CANVAS_MOTORS, background=BG_CANVAS_MOTORS,image=self.connetRImg,borderwidth=0,compound="c",command=self.Connect)
		self.Button_SetInitPos = Button(self.button_LogicCanvas,activebackground=BG_CANVAS_MOTORS, background=BG_CANVAS_MOTORS,image=self.homeImg,borderwidth=0,compound="c",command=lambda: self.Load(0),state= 'disable')
		# self.Button_SavePosition = Button(self.button_LogicCanvas,activebackground=BG_CANVAS_MOTORS, background=BG_CANVAS_MOTORS,image=self.savePodImg,borderwidth=0,compound="c",command=lambda: self.Load(0))
		# self.Button_SavePosition = Button(self.button_LogicCanvas,activebackground=BG_CANVAS_MOTORS, background=BG_CANVAS_MOTORS,image=self.savePodImg,borderwidth=0,compound="c",command = self.toggleRobot)
		self.button_LogicCanvas.create_text(55,195,text="POWER ON",font= self.MonserratFont_10, fill= TITTEL_CANVAS)
		self.button_LogicCanvas.create_oval(100,180,125,205,fill= 'black', outline= 'grey')
		
		#Buttons placement
		
		self.Button_Connect.place(x = 35,y=30)
		self.Button_Load.place(x = 35,y=70)
		# self.Button_SavePosition.place(x = 35,y=110)
		self.Button_SetInitPos.place(x = 35,y=110)
		
		self.button_LogicCanvas.grid(row=0,column=0)

	def set_movementRobotButtons(self):
	
		#Buttons functionality
		self.button_MovementCanvas = Canvas(self.root, width=305,height=220,background=BG_CANVAS_MOTORS)
		self.button_MovementCanvas.create_text(150,15,text="Movement Command",font= self.MonserratFont_10b, fill= TITTEL_CANVAS)
		self.Buton_on_off = Button(self.button_MovementCanvas,activebackground=BG_CANVAS_MOTORS, background=BG_CANVAS_MOTORS,image=self.on_off_r,borderwidth=0,compound="c",command = self.toggleRobot,state= 'disable')
		self.reset = Button(self.button_MovementCanvas,activebackground=BG_CANVAS_MOTORS, background=BG_CANVAS_MOTORS,image=self.reset_img,borderwidth=0,compound="c",command = self.resetRobot,state= 'disable')
		self.Button_Forward = Button(self.button_MovementCanvas,borderwidth=0,activebackground=BG_CANVAS_MOTORS, background=BG_CANVAS_MOTORS,image=self.forwardImg,compound="c",command= lambda: self.Robot_Move([1,1],"Forward"),state= 'disable')
		self.Button_Backward = Button(self.button_MovementCanvas,borderwidth=0,activebackground=BG_CANVAS_MOTORS, background=BG_CANVAS_MOTORS,image=self.backwardImg, compound="c",  command= lambda: self.Robot_Move([-1,-1],"Backward"),state= 'disable')
		self.Button_Righ = Button(self.button_MovementCanvas,borderwidth=0,activebackground=BG_CANVAS_MOTORS, background=BG_CANVAS_MOTORS,image=self.rigthImg,compound="c",command=lambda: self.Robot_Move([2,0],"Rigth"),state= 'disable')
		self.Button_Left = Button(self.button_MovementCanvas,borderwidth=0,activebackground=BG_CANVAS_MOTORS, background=BG_CANVAS_MOTORS,image=self.leftImg,compound="c",  command=lambda: self.Robot_Move([0,2],"Left"),state= 'disable')
		self.Button_Stop = Button(self.button_MovementCanvas,borderwidth=0,activebackground=BG_CANVAS_MOTORS, background=BG_CANVAS_MOTORS,image=self.stopImg,compound="c",command=lambda: self.Robot_Move([0,0],"Stop"),state= 'disable')
		
		#Buttons placement
		self.reset.place(x = 200,y = 170)
		self.Buton_on_off.place(x = 10,y = 170)
		self.Button_Forward.place(x = 105,y=50)
		self.Button_Righ.place(x = 10,y=95)
		self.Button_Stop.place(x = 105,y=95)
		self.Button_Left.place(x = 200,y=95)
		self.Button_Backward.place(x = 105,y=140)
		
		self.button_MovementCanvas.grid(row=0,column=1, columnspan=2)

	##################################################################################
	##################################################################################
	##################################################################################
	##################################################################################
	# Menu creation with functions
	##################################################################################
	
	# dummy function
	def donothing(self):
		filewin = Toplevel(self.root)
		button = Button(filewin, text="Do nothing button")
		button.pack()

	def setMenu(self):
		self.menubar = Menu(self.root)
	
		filemenu = Menu(self.menubar, tearoff=0)
		filemenu.add_command(label="New", command=self.donothing)
		filemenu.add_command(label="Open", command=self.donothing)
		filemenu.add_command(label="Save", command=self.donothing)
		filemenu.add_separator()
		filemenu.add_command(label="Exit", command=self.root.quit)

		self.menubar.add_cascade(label="File", menu=filemenu)

		editmenu = Menu(self.menubar, tearoff=0)
		editmenu.add_command(label="Simulation", command=self.Simulation)
		editmenu.add_command(label="Connection", command=self.connectionSet)
		editmenu.add_separator()
		editmenu.add_command(label="Robot", command=self.setRName)
		editmenu.add_command(label="Gripper", command=self.gripperConfig)
		editmenu.add_command(label="Motors", command=self.motorsConfig)
		editmenu.add_command(label="Communication", command=self.comunnicationSet)

		self.menubar.add_cascade(label="Edit", menu=editmenu)

		helpmenu = Menu(self.menubar, tearoff=0)
		helpmenu.add_command(label="Help Index", command=self.donothing)
		helpmenu.add_command(label="About...", command=self.donothing)

		self.menubar.add_cascade(label="Help", menu=helpmenu)

		terminalview = Menu(self.menubar, tearoff=0)
		terminalview.add_command(label="Open Terminal", command=self.activeTerminal)
		terminalview.add_command(label="Save Data", command=self.donothing)

		self.menubar.add_cascade(label="Terminal Viewer", menu=terminalview)

		self.root.config(menu=self.menubar)

	def gripperConfig(self):
		if self.robot.is_connected():
			frame = Toplevel(self.menubar)
			frame.iconbitmap(self.img)
			frame.title('Gripper')
			frame.geometry("250x150")
			frame.resizable(width=False, height=False)

			def close():
				q.put((GRIPPER_CONFIG,int(rat_cm.get())))
				frame.destroy()
			
			cavasFrame = Canvas(frame, height= '150', width='250', background = MENUBAR_BG)	
			cavasFrame.create_text(45,30,text = "ID ",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
			cavasFrame.create_text(45,50,text = "Ratio ",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
			cavasFrame.create_text(160,50,text = "cm ",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
			cavasFrame.create_text(45,70,text = "Hold current ",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
			cavasFrame.create_text(160,70,text = "mA",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
			cavasFrame.create_text(45,90,text = "Run current ",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
			cavasFrame.create_text(160,90,text = "mA",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)

			grp_id = Entry(cavasFrame, font= self.MonserratFont_8b, width = 10)
			rat_cm = Entry(cavasFrame, font= self.MonserratFont_8b, width = 10)
			hold_curr = Entry(cavasFrame,  font= self.MonserratFont_8b, width = 10)
			run_curr = Entry(cavasFrame,  font= self.MonserratFont_8b, width = 10)

			grp_id.insert(0,self.robot.gripper_motor_id)
			rat_cm.insert(0,self.robot.grp_cm_rat)
			hold_curr.insert(0,str(self.robot.hold_current[self.robot.gripper_motor_id]))
			run_curr.insert(0,str(self.robot.run_current[self.robot.gripper_motor_id]))
			hold_curr['state'] = 'readonly'
			run_curr['state'] = 'readonly'
			grp_id['state'] = 'readonly'

			grp_id.place(x=80,y=20)
			rat_cm.place(x=80,y=40)
			run_curr.place(x=80,y=60)
			hold_curr.place(x=80,y=80)

			button = Button(cavasFrame, text="OK", command = close)
			button.place(x=90,y=110)
			
			cavasFrame.pack()
		else:
			self.alert_frame("Thereis no robot connected")

	def motorsConfig(self):
		if self.robot.is_connected():
			frame = Toplevel(self.menubar)
			frame.iconbitmap(self.img)
			frame.title('Motors')
			frame.resizable(width=False, height=False)

			def close():
				m_id 	= []
				m_ihold = []
				m_irun 	= []
				for i in range(TOTAL_JOINTS):
					if m_chechVals[i].get():
						print("check motor "+str(i))
						m_id.append(i)
						m_ihold.append(int(hold_curr[i].get()))
						m_irun.append(int(run_curr[i].get()))
				q.put((CMD_SET_CURRENT_REG,m_id,m_ihold,m_irun))
				# frame.destroy()

			def_width = 220
			def_heigth = TOTAL_JOINTS*40+20
			increase 	= 25
			base 		= 20
			entry_base_x = 80
			entry_base_y = 35
			hold_curr 	= []
			run_curr 	= []
			m_enCheck 	= []
			m_chechVals = []
			
			frame.geometry(str(def_width)+'x'+str(def_heigth))
			cavasFrame = Canvas(frame, height=str(def_heigth), width=str(def_width), background = MENUBAR_BG)	

			cavasFrame.create_text(100,base,text = "IHOLD(mA)",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
			cavasFrame.create_text(160,base,text = "IRUN(mA)",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
			for i in range(TOTAL_JOINTS):
				cavasFrame.create_text(30,2*base+i*increase,text = "MOTOR "+str(i),font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
				hold_curr.append(Entry(cavasFrame,  font= self.MonserratFont_8b, width = 6)) 
				run_curr.append(Entry(cavasFrame,  font= self.MonserratFont_8b, width = 6))
				hold_curr[i].delete(0,END)
				hold_curr[i].insert(0,self.robot.hold_current[i])
				run_curr[i].delete(0,END)
				run_curr[i].insert(0,self.robot.run_current[i])
				hold_curr[i].place(x=entry_base_x,y=entry_base_y+i*increase)
				run_curr[i].place(x=entry_base_x+60,y=entry_base_y+i*increase)
				m_chechVals.append(IntVar())
				m_enCheck.append(Checkbutton(cavasFrame, background=MENUBAR_BG, variable=m_chechVals[i],onvalue=1,offvalue=0))
				m_enCheck[i].place(x=220-30,y=entry_base_y+i*increase)
				if self.robot.is_motorEnable(i):
					m_enCheck[i].select()

			button = Button(cavasFrame, text="SET CURRENT", command = close)
			button.place(x=def_width/2-10,y=def_heigth - 30)
			cavasFrame.pack()
		else:
			self.alert_frame("Thereis no robot connected")

	def activeTerminal(self): 
		print("Terminal active\n")
		self.terminal = Toplevel(self.menubar)
		self.terminal.iconbitmap(self.img)
		self.terminal.title('Mode')
		self.terminal.geometry("")
		return 

	def Simulation(self):
		frame = Toplevel(self.menubar)
		frame.iconbitmap(self.img)
		frame.title('Mode')
		frame.geometry("200x120")
		frame.resizable(width=False, height=False)

		def close():
			if (var.get() != self.connection.getMode()): # if the mode has change write in memory and set change
				q.put((SET_CONNECTION_MODE,var.get()))

			frame.destroy()

		cavasFrame = Canvas(frame, height= '120', width='200', background = MENUBAR_BG)	
		cavasFrame.create_text(45,20,text = "Arduino MKR ",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
		cavasFrame.create_text(45,40,text = "CopeliaSim EDU",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
		cavasFrame.create_text(45,60,text = "Debug",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)

		var=IntVar()

		R1 = Radiobutton(cavasFrame, background=MENUBAR_BG,variable=var, value=MODE_ARDUINO_MKR)
		R2 = Radiobutton(cavasFrame, background=MENUBAR_BG,variable=var, value=MODE_COPPELIA_SIM)
		R3 = Radiobutton(cavasFrame, background=MENUBAR_BG,variable=var, value=MODE_DEBUG)
		button = Button(cavasFrame, text="OK", command = close)

		R1.place(x=120,y=10)
		R2.place(x=120,y=30)
		R3.place(x=120,y=50)
		button.place(x=90,y=90)

		connectionmsg = " CONNECTION "
		if self.connection.getMode()==0:
			connectionmsg = connectionmsg + " TO ARDUINO "
			R1.select()
		elif self.connection.getMode()==1:
			connectionmsg = connectionmsg + " TO COPPELIASIM "
			R2.select()
		else:
			connectionmsg = connectionmsg + " TO DEBUG "
			R3.select()

		cavasFrame.create_text(100,80,text = connectionmsg,font = self.MonserratFont_10b, fill= WARNING_COLOR)
		cavasFrame.pack()

	def connectionSet(self):
		frame = Toplevel(self.menubar)
		frame.iconbitmap(self.img)
		frame.title('Connection')
		frame.geometry("250x120")
		frame.resizable(width=False, height=False)
		connectParamas = self.connection.getParams()
		ip_addr = connectParamas[1]
		actual_port = connectParamas[0]

		def close():
			data_ip = (ip.get())
			data_port = (port.get())
			if self.robot.is_connected()==False and (data_ip != str(ip_addr) or data_port!= str(actual_port)) or self.connection.getConnectionType() != con_type.get():
				q.put((SAVE_NEW_IP,data_ip,data_port,con_type.get()))
			frame.destroy()
		
		cavasFrame = Canvas(frame, height= '120', width='250', background = MENUBAR_BG)	
		cavasFrame.create_text(50,25,text = "IP",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
		cavasFrame.create_text(50,45,text = "PORT",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)

		ip = Entry(cavasFrame, font= self.MonserratFont_8b, width = 20)
		port = Entry(cavasFrame,  font= self.MonserratFont_8b, width = 20)
		ip.place(x=80,y=20)
		port.place(x=80,y=40)

		cavasFrame.create_text(50,75,text = "UDP",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
		cavasFrame.create_text(120,75,text = "TCP",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
		con_type = StringVar()
		tcp_circle = Radiobutton(cavasFrame, background=MENUBAR_BG,variable=con_type, value="TCP")
		udp_circle = Radiobutton(cavasFrame, background=MENUBAR_BG,variable=con_type, value="UDP")
		udp_circle.place(x = 75, y= 65)
		tcp_circle.place(x = 150, y= 65)

		if self.connection.getConnectionType()== 'UDP':
			udp_circle.select()
		elif self.connection.getConnectionType()== 'TCP':
			tcp_circle.select()

		#insert conenction params saved 
		ip.insert(0,ip_addr) 
		port.insert(0,actual_port)
		
		button = Button(cavasFrame, text="OK", command = close)
		button.place(x=200,y=65)

		if self.robot.is_connected() :
			button['state'] = 'disable'
			cavasFrame.create_text(125,100,text = "YOU ARE ALREADY CONNECTED",font = self.MonserratFont_10b, fill= WARNING_COLOR)
		
		cavasFrame.pack()

	def comunnicationSet(self):

		if self.robot.is_connected():
			frame = Toplevel(self.menubar)
			frame.iconbitmap(self.img)
			frame.title('Comunication Settings')
			frame.geometry("250x120")
			frame.resizable(width=False, height=False)

			def close():
				q.put((SET_COMMUNICATION_SETTINGS,packageNumberPerCMD.get(),pointPerCM.get(),var.get()))
				frame.destroy()

			cavasFrame = Canvas(frame, height= '120', width='250', background = MENUBAR_BG)	
			cavasFrame.create_text(90,20,text = "Command per Package send",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
			cavasFrame.create_text(80,40,text = "Number of points per cm",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
			cavasFrame.create_text(80,60,text = "Send Position",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
			cavasFrame.create_text(80,80,text = "Send Velocities",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)

			var = IntVar()
			R1 = Radiobutton(cavasFrame,background=MENUBAR_BG, variable=var, value=POS_MODE)
			R2 = Radiobutton(cavasFrame, background=MENUBAR_BG, variable=var, value=VEL_MODE)
			
			packageNumberPerCMD = Entry(cavasFrame, font= self.MonserratFont_8b, width = 5)
			pointPerCM = Entry(cavasFrame,  font= self.MonserratFont_8b, width = 5)
			button = Button(cavasFrame, text="OK", command = close)

			packageNumberPerCMD.place(x=200,y=10)
			pointPerCM.place(x=200,y=30)
			packageNumberPerCMD.insert(0,str(self.connection.sizePackage))
			pointPerCM.insert(0,str(self.robot.pointsPerCM))

			R1.place(x=200,y=45)
			R2.place(x=200,y=65)
			
			if self.robot.sendMode == POS_MODE:
				R1.select()
			elif self.robot.sendMode == VEL_MODE:
				R2.select()

			button.place(x=125,y=90)
			cavasFrame.pack()
		else:
			self.alert_frame("Thereis no robot connected")
	
	def setRName(self):
		if self.robot.is_connected():
			frame = Toplevel(self.menubar)
			frame.iconbitmap(self.img)
			frame.title('Robot Config')
			frame.geometry("250x100")
			frame.resizable(width=False, height=False)

			def close():
				q.put((SET_ROBOT_PARAMS,robotName.get(),robotVel.get()))
				frame.destroy()

			cavasFrame = Canvas(frame, height= '100', width='250', background = MENUBAR_BG)	
			cavasFrame.create_text(60,20,text = "Name ",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
			cavasFrame.create_text(80,40,text = "Linear velocity (max 5)",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
			cavasFrame.create_text(200,40,text = "cm/s",font = self.MonserratFont_8b, fill= MENUBAR_FONT_COLOR)
			
			robotName = Entry(cavasFrame, font= self.MonserratFont_8b, width = 15)
			robotName.insert(0,self.robot.name)
			robotVel = Entry(cavasFrame, font= self.MonserratFont_8b, width = 5)
			robotVel.insert(0,self.robot.velocityInCMpS)
			button = Button(cavasFrame, text="OK", command = close)

			robotName.place(x=150,y=10)
			robotVel.place(x=150,y=30)
			button.place(x=125,y=60)
			cavasFrame.pack()
		else:
			self.alert_frame("Thereis no robot connected")
		

	################################################################################
	# tkinter function implementation
	################################################################################
	
	def alert_frame(self,msg):
		frame = Toplevel(self.root)
		frame.iconbitmap(self.img)
		frame.title('Alert')
		frame.geometry("250x100")
		cavasFrame = Canvas(frame, height= '100', width='250', background = MENUBAR_BG)	
		cavasFrame.create_text(125,50,text = msg,font = self.MonserratFont_12b, fill= WARNING_COLOR)
		cavasFrame.pack()

	def display_power_status(self,logic_state):
		if logic_state:
			self.button_LogicCanvas.create_oval(100,180,125,205,fill= LSR_LED_ON, outline= 'grey')
		else:
			self.button_LogicCanvas.create_oval(100,180,125,205,fill= 'black', outline= 'grey')

	def loop(self):
		self.root.mainloop()
		print("Shut down GUI")

	def toggle_widgetsFromConnection(self):
		if self.buttons_disable:

			self.buttons_disable = 0
			# Disable if not connected
			self.Buton_on_off['state'] = 'disable'
			self.Button_Backward['state'] = 'disable'
			self.Button_Release['state'] = 'disable'
			self.Button_Righ['state'] = 'disable'
			self.Button_Left['state'] = 'disable'
			self.Button_Stop['state'] = 'disable'
			self.Button_Load['state'] = 'disable'
			self.Button_Hold['state'] = 'disable'
			self.Button_SetInitPos['state'] = 'disable'
			self.Button_Forward['state'] = 'disable'
			# self.Button_SavePosition['state'] = 'disable'
			self.reset['state']= 'disable'

			#colors
			self.Button_Connect['image'] = self.connetRImg

			#delete widgets
			self.init_directKinematicCanvas()
			self.createPlotCanvas()

			return 1
		else:
			self.buttons_disable = 1
			self.reset['state']= 'normal'

			if self.robot.gripper_motor_id > 0:
				self.Buton_on_off['state'] = 'normal'
				self.Button_Release['state'] = 'normal'
			
			if self.robot.moving_base_active:
				self.Button_Righ['state'] = 'normal'
				self.Button_Left['state'] = 'normal'
				self.Button_Stop['state'] = 'normal'
				self.Button_Forward['state'] = 'normal'
				self.Button_Backward['state'] = 'normal'

			self.Button_Load['state'] = 'normal'
			self.Button_Hold['state'] = 'normal'
			self.Button_SetInitPos['state'] = 'normal'

			# self.Button_SavePosition['state'] = 'normal'

			#colors 
			self.Button_Connect['image'] = self.connetGImg

			self.update_plot_canvas()
			self.active_DirectKinematicCanvas()

			
	#Robot functions
	def toggleRobot(self):
		q.put((TOGGLE_ROBOT_EN))

	def resetRobot(self):
		q.put((CMD_RESET_MOTORS))

	def Load(self,type):
		pos = [0,0,0]
		
		try: 
			#type 1 set new coordenates. type 0 set init position
			if type == 1:
				pos[0] = float(self.x_input.get())
				pos[1] = float(self.y_input.get())
				pos[2] = float(self.z_input.get())
				#Pasing data to robot
				print(pos)
				q.put((NEW_POS, pos))
				
			else:
				q.put(GO_HOME)
		except:
			pub.sendMessage("update", State= "ERROR. Check loaded data . . . ")

	def Robot_Move(self,vel,func): #function for car moving
		self.connection.set_velocity(vel)
		self.set_States(func)
		return

	def Grip(self,op): #function to control gripper. 0 open, 1 close
		if op == 1:
			q.put((OPEN_GRIPPER))
		else:
			q.put((CLOSE_GRIPPER))
		return 

	#Api connection 
	def Connect(self): #function for connecting to port
		#change connection status
		q.put((CONNECT))
		return
