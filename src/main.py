# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       Ethan Waines                                                 #
# 	Created:      2/24/2026, 9:59:01 AM                                        #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #
#region VEX Robot Configuration
from vex import *
import urandom
import math
import threading

# Brain should be defined by default
brain=Brain()

# Robot configuration code
controller_1 = Controller(PRIMARY)

#Configuration of the Odometry
wheel_diameter = 4
wheel_circumference = math.pi * wheel_diameter
DistanceBetweenLeftRightTrackingWheels = 4
DistanceBetweenBackTrackingWheelAndCenter = 2

#Odometry Resets
x_position_of_robot = 0
y_position_of_robot = 0
current_heading = 0
prev_Left = 0
prev_Right = 0
prev_Back = 0

#Drivetrain
#Left Drivetrain
Left_1 = Motor(Ports.PORT3, GearSetting.RATIO_6_1, False)
Left_2 = Motor(Ports.PORT2, GearSetting.RATIO_6_1, True)
Left_3 = Motor(Ports.PORT1, GearSetting.RATIO_6_1, False)

#Right Drivetrain
Right_1 = Motor(Ports.PORT8, GearSetting.RATIO_6_1, False)
Right_2 = Motor(Ports.PORT7, GearSetting.RATIO_6_1, True)
Right_3 = Motor(Ports.PORT6, GearSetting.RATIO_6_1, False)

#Encoders/Trackers
Left_Tracker = Rotation(Ports.PORT10, False)
Right_Tracker = Rotation(Ports.PORT11, False)
Back_Tracker = Rotation(Ports.PORT12, False)
# wait for rotation sensor to fully initialize

wait(30, MSEC)

def Drivetrain_Control():
    #Setting speeds based on controller joystick input
    #Left side of drivetrain
    Left_1.set_velocity((controller.axis3.position + 0.5 * controller.axis1.position), PERCENT)
    Left_2.set_velocity((controller.axis3.position + 0.5 * controller.axis1.position), PERCENT)
    Left_3.set_velocity((controller_1.axis3.position + 0.5 * controller.axis1.position), PERCENT)
    #Right side of drivetrain
    Right_1.set_velocity((controller.axis3.position - 0.5 * controller.axis1.position), PERCENT)
    Right_2.set_velocity((controller.axis3.position - 0.5 * controller.axis1.position), PERCENT)
    Right_3.set_velocity((controller.axis3.position - 0.5 * controller.axis1.position), PERCENT)

    #Make Motors always moving
    #Left Drivetrain
    Left_1.spin(FORWARD)
    Left_2.spin(FORWARD)
    Left_3.spin(FORWARD)
    #Right Drivetrain
    Right_1.spin(FORWARD)
    Right_2.spin(FORWARD)
    Right_3.spin(FORWARD)

# Make random actually random
def initializeRandomSeed():
    wait(100, MSEC)
    random = brain.battery.voltage(MV) + brain.battery.current(CurrentUnits.AMP) * 100 + brain.timer.system_high_res()
    urandom.seed(int(random))
      
# Set random seed 
initializeRandomSeed()

# add a small delay to make sure we don't print in the middle of the REPL header
wait(200, MSEC)
# clear the console to make sure we don't have the REPL in the console
print("\033[2J")

#endregion VEX Robot Configuration

#region Odometry code
def Odometry_Calculation():
    global x_position_of_robot, y_position_of_robot, current_heading
    global prev_Left, prev_Right, prev_Back
    #Create variables for calulation for position right now
    Left = Left_Tracker.position(DEGREES)
    Right = Right_Tracker.position(DEGREES)
    Back = Back_Tracker.position(DEGREES)

    #Create variables for the change in postition recently but in inches
    Change_Left = (Left - prev_Left) * wheel_circumference/180
    Change_Right = (Right - prev_Right) * wheel_circumference/180
    Change_Back = (Left - prev_Back) * wheel_circumference/180

    #Resetting the positions so that the prev position is equal to what it is now
    prev_Left = Left
    prev_Right = Right
    prev_Back = Back

    #Caculate the change of heading
    Change_Heading = (Change_Right - Change_Left) / DistanceBetweenLeftRightTrackingWheels

    #Create variables that show where the robot is locally (relative to robot)
    Change_x_Local = Change_Back - Change_Heading * DistanceBetweenBackTrackingWheelAndCenter
    Change_y_Local = (Change_Left + Change_Right)/2

    #Create variables that show where the robot is relative to the field
    Change_x_Field = Change_x_Local * math.cos(current_heading) - Change_y_Local * math.sin(current_heading)
    Change_y_Field = Change_y_local * math.cos(current_heading) + Change_x_Local * math.sin(current_heading)

    #Set it all as the position of the robot right now
    x_position_of_robot = x_position_of_robot + Change_x_Field
    y_position_of_robot = y_position_of_robot + Change_y_Field
    current_heading = current_heading + Change_Heading

def Odometry_Movement(x_postion, y_postion):
    global x_position_of_robot, y_position_of_robot, current_heading
    turns = 0
    change_in_x = x_postion - x_position_of_robot
    change_in_y = y_postion - y_position_of_robot
    Front_and_Back = ""
    Left_and_Right = ""
    #Check which direction the target it
    '''
    if change_in_y < 0:
        Front_and_Back = "Back"
    elif change_in_y > 0:
        Front_and_Back = "Front"
    elif change_in_y = 0:
        Front_and_Back = "NO CHANGE"
        '''
    if change_in_x < 0:
        Left_and_Right = "Left"
    elif change_in_x > 0:
        Left_and_Right = "Right"
    '''
    elif change_in_x = 0:
        Left_and_Right = "NO CHANGE"
    '''
    #Now, to deal with angle calculation
    angle_change = math.atan2(change_in_y, change_in_x)
    turn_amount = angle_change - current_heading
    while turn_amount > math.pi:
        turn_amount = turn_amount - 2 * math.pi

    while turn_amount < -math.pi:
        turn_amount = turn_amount + 2 * math.pi
    #angle_change = math.degrees(angle_change)
    Radius = DistanceBetweenLeftRightTrackingWheels/2
    Tracker_travel_length = Radius * abs(turn_amount)
    degrees_need_to_turn = (Tracker_travel_length*360)/wheel_circumference
    '''
    while degrees_need_to_turn > 360:
        turns = turns + 1
        degrees_need_to_turn = degrees_need_to_turn - 360
    '''
    Change_in_tracking_Left = Left_Tracker.position(DEGREES)
    Change_in_tracking_Right = Right_Tracker.position(DEGREES)
    if turn_amount > 0:
        Right_1.spin(REVERSE)
        Right_2.spin(REVERSE)
        Right_3.spin(REVERSE)
        Left_1.spin(FORWARD)
        Left_2.spin(FORWARD)
        Left_3.spin(FORWARD)
    else:
        Left_1.spin(REVERSE)
        Left_2.spin(REVERSE)
        Left_3.spin(REVERSE)
        Right_1.spin(FORWARD)
        Right_2.spin(FORWARD)
        Right_3.spin(FORWARD)
    
    #Now, to tell the robot when to stop turning
    while (Left_Tracker.position(DEGREES) - Change_in_tracking_Left) < degrees_need_to_turn  and (Right_Tracker.position(DEGREES) - Change_in_tracking_Right) < degrees_need_to_turn:
        wait(5, MSEC)
    Left_1.stop()
    Left_2.stop()
    Left_3.stop()
    Right_1.stop()
    Right_2.stop()
    Right_3.stop()
    current_heading = current_heading + turn_amount
    while current_heading > math.pi:
        current_heading = current_heading - 2*math.pi
    while current_heading < -math.pi:
        current_heading = current_heading + 2 * math.pi
    x_position_of_robot = x_postion
    y_position_of_robot = y_postion
    change_in_x = abs(change_in_x)
    change_in_y = abs(change_in_y)
    hypotonuse = (change_in_x**2 + change_in_y**2)**0.5
    Odometry_Forward_Movement(hypotonuse)

def Odometry_Forward_Movement(travel_distance):
    global wheel_circumference
    turns = 0
    degrees_need_to_turn = (travel_distance*360)/wheel_circumference
    '''
    while degrees_need_to_turn > 360:
        turns = turns + 1
        degrees_need_to_turn = degrees_need_to_turn - 360
    '''
    #Reset the tracker position momentarily
    Change_in_tracking = (Left_Tracker.position(DEGREES) + Right_Tracker.position(DEGREES))/2
    #Left Drivetrain
    Left_1.spin(FORWARD)
    Left_2.spin(FORWARD)
    Left_3.spin(FORWARD)
    #Right Drivetrain
    Right_1.spin(FORWARD)
    Right_2.spin(FORWARD)
    Right_3.spin(FORWARD)
    while ((Left_Tracker.position(DEGREES) + Right_Tracker.position(DEGREES))/2 - Change_in_tracking) < degrees_need_to_turn:
        wait(5, MSEC)
    #Stop the whole driving from moving
    #Left drivetrain
    Left_1.stop()
    Left_2.stop()
    Left_3.stop()
    #Right drivetrain
    Right_1.stop()
    Right_2.stop()
    Right_3.stop()

def calibrate_trackers():
    Left_Tracker.set_position(0, DEGREES)
    Right_Tracker.set_position(0, DEGREES)
    Back_Tracker.set_position(0, DEGREES)

#Create the loop for Odometry calculation
def Odometry_Loop():
    while True:
        Odometry_Calculation()
        wait(5, MSEC)

#endregion Odometry code

def pre_auton():
    #Runs code before autonomous
    brain.screen.clear_screen()
    brain.screen.print("pre-auton")
    #Set stopping of drivetrain to brake
    #Left drivetrain
    Left_1.set_stopping(BRAKE)
    Left_2.set_stopping(BRAKE)
    Left_3.set_stopping(BRAKE)
    #Right drivetrain
    Right_1.set_stopping(BRAKE)
    Right_2.set_stopping(BRAKE)
    Right_3.set_stopping(BRAKE)
    #Start the odometry
    calibrate_trackers()
    odometry_thread = threading.Thread(target = Odometry_Loop, daemon = True)
    odometry_thread.start()
    # place pre-auton code here

def autonomous():
    brain.screen.clear_screen()
    brain.screen.print("autonomous code")
    #Set speed of drivetrain
    #Left drivetrain
    Left_1.set_velocity(100, PERCENT)
    Left_2.set_velocity(100, PERCENT)
    Left_3.set_velocity(100, PERCENT)
    #Right drivetrain
    Right_1.set_velocity(100, PERCENT)
    Right_2.set_velocity(100, PERCENT)
    Right_3.set_velocity(100, PERCENT)

    # place automonous code here

def user_control():
    brain.screen.clear_screen()
    brain.screen.print("driver control")
    # place driver control in this while loop
    while True:
        wait(20, MSEC)
        Drivetrain_Control()

# create competition instance
comp = Competition(user_control, autonomous)

# actions to do when the program starts
brain.screen.clear_screen()
pre_auton()