


PORT_COPPELIA_DEFAULT   =   19999
IP_COPPELIA_DEFAULT     = '127.0.0.1'

#define number of handlers 

REVOLT_JOINT    = 2
LINEAR_JOINT    = 1
GRIPP_JOINTS    = 2
MOTORS          = 2

# Api = Connection(81,'192.168.1.59')
# Joints for robot
#  define here the names of the joint used according to the type 
grip_hdlrs    = ['Barrett_openCloseJoint','Barrett_openCloseJoint0']
linear_joinst = ['joint3']
revolt_joints = ['joint1','joint2']
motor_joints  = ['Pioneer_p3dx_leftMotor','Pioneer_p3dx_rightMotor']

#Robot Constrains
## this should be orthered fist the revolt and then the linear joints. In this case q1,q2,q3
Rjoints_max_limist = [115,135]
Rjoints_min_limist = [-115,-135]
Ljoints_max_limist = [0.3]
Ljoints_min_limist = [0] 


