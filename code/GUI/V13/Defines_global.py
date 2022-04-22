from Commands import *


#################################################################################
#################################################################################
#################################################################################
############################## GUI

ICON_PATH = 'IMG/LOGO_SM.ico'

################### MANAGERS

TIME_DELAY_LOOP = 1/100
CMD_CONNECTION_TOUT = 1 # the connecte cmd is send each second
MANAGER_CHECK_CONNECTION_TOUT = 10 

###############################################################
# plot

PLOT_BORDER = 20
PLOT_LENGTH = 400
PLOT_TOTAL = PLOT_LENGTH + PLOT_BORDER*2
P0_X  = (PLOT_TOTAL)/2
P0_Y  = (PLOT_TOTAL)/2
P60_X = PLOT_LENGTH + PLOT_BORDER
P60_Y = PLOT_BORDER
Pneg60_Y = P60_X
Pneg60_X = P60_Y

MAX_VALUE_X = 12
MAX_VALUE_Y = 12
distance = (PLOT_LENGTH)/MAX_VALUE_X
init0_0 =[(PLOT_LENGTH)/2,(PLOT_LENGTH)/2]

M_Y = (60)/(P60_Y - P0_Y)
M_X = (60)/(P60_X - P0_X)


###############################################################
#Colors 

RANGE_ROBOT_COLOR = '#218CDB'
BG_CANVAS_MOTORS = '#262626'
TITTEL_CANVAS = '#FFFFFF'
STATUS_BG = '#d4c414'
CONNECT_COLOR_BUTTON ='#6DBD1E'
DISCONNECT_COLOR_BUTTON = '#BA3A43'
LSR_LED_ON = '#78FF00'
LSR_LED_OFF = 'black'
LSR_LED_BRDR = 'grey'
MENUBAR_BG = '#887E36'
MENUBAR_FONT_COLOR = '#FFFFFF'
DFLT_BUTTONS_COLOR = '#7B9697'
WARNING_COLOR = '#CD0000'

######################################################
######################################################
######################################################
######################################################
## File constants

JSON_DEFAULT ={
    "robot_name":"SACRMOV",
    "linear_velocity":5,
    "IP":"192.168.1.138",
    "PORT":2390,
    "point_cm":10,
    "size_package":10,
    "simulation_mode":0,
    "send_mode":0,
    "connection_type":"UDP"
}

###############################################################################
########################## MODES

#Connection Modes

MODE_ARDUINO_MKR = 0
MODE_COPPELIA_SIM = 1
MODE_DEBUG = 2

#################################################################################
#################################################################################
#################################################################################
############# CONNECTION   

PORT_DEFAULT_ARDUINO =  81
IP_DEFAULT_ARDUINO   =  '192.168.43.112'
UDP_CONNECTION = 0
TCP_CONNECTION = 1

CONNECTION_TOUT      = 15 # in secs

#################################################################################
#################################################################################
###############################################################################3
##################### ROBOT DEFINES

# state json structure

STATUS_PROCESS_DELAY = 1/100
MAX_MOVEMENT_TOUT_SEC = 30

JSON_DEFAULT_STATE = {

}

ROBOT_NAME = "ScarMov"

# Movement

CLK = 12000000 # frequency of motor´s drivers TMC5160
uSTEP_PREV = 51200 # microsteps per revolution
VEL_360PERSEC = 71583# velocity for 1RPS or 2*3,14159rad/s
PACKAGE_SEGMENTS = 20  # number of trayectory segments to be send by each package
LINEAR_VEL = 5 # linear velocitie of the gripper in cm/s

# Temporal variables

MIN_TIME_DELAY_MS = 50 # 50 ms of delay to calculate number or segments in trayectory

# send buffer pacake size 

BUFFER_SENT_SIZE_DIVISION = 10

#modes 
VEL_MODE = 1
POS_MODE = 0

# Define constants

TOTAL_JOINTS = 4
LINEAR_JOINT = 1
REVOL_JOINT = 2

LINEAR_MOV_PER_360G = 8 # 8 mm of linear  movemente per spin in motor q2

linearFactorControl = [VEL_360PERSEC/(LINEAR_MOV_PER_360G)]
angularFactorControl = [VEL_360PERSEC/360,(VEL_360PERSEC*2.5)/360]

#Robot Constrains
## this should be orthered fist the revolt and then the linear joints. In this case q1,q2,q3
Constrains         = [35,25,80] # in cms
Rjoints_max_limist = [115,135]
Rjoints_min_limist = [-115,-135]
Ljoints_max_limist = [0.3]
Ljoints_min_limist = [0] 
init_pos = [60, 0 , 10]

INSIDE_RADIUS_LIMIT_CM = 30

# pulley Factors
pull_Fac = [2.5,2.5,1]

DATA_SCALE = 100