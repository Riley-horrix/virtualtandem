import toml
import sys
import numpy as np


import hardware.virtual.motor as motor
import hardware.hardwareInterface as hw

import common as cm
from common import Enumeration

import graphics.robotGraphics as robGraphics
import graphics.graphics as gp

MOTOR_STATUS = Enumeration("""
    POWER_GOAL,
    POSITION_GOAL,
    HOLD,
    IDLE,
""")

WHEEL = Enumeration("""
    RIGHT,
    LEFT,
    NONE,
""")

# Minimal difference between wheel velocities for the robot to be considered as
# 'moving forward'.
VEL_DIFF_MIN = 0.0001

# Difference in encoder position and target to consider a move done
POSITION_CONTROL_REACHED = 1

class VirtualRobot:
    def __init__(self):
        print("Initialising Virtual Robot")
        # Virtual robot will need some values from the physical robot, i.e. 
        # weight, wheelbase, etc
        with open("robot_config.toml") as stream:
            try:
                self.config = toml.load(stream)['robot']
                print(self.config)
            except toml.TomlDecodeError as err:
                print(err)
                sys.exit(-1)

        self.x = 0
        self.y = 0
        self.orientation = 0

        window = gp.GraphWin("VirtualTandem", 800, 800)
        window.setCoords(-2, -2, 2, 2)

        self.graphics = robGraphics.RobotGraphics(window, self.config['inner_wheel_base'], self.config['wheel_radius'], (self.config['outer_wheel_base'] - self.config['inner_wheel_base']) / 2)
        self.graphics.updateRobot(self.x, self.y, self.orientation)

        self.left_motor = motor.Motor("LegoMotor")
        self.right_motor = motor.Motor("LegoMotor")
        self.left_motor_status = (MOTOR_STATUS.HOLD, 0)
        self.right_motor_status = (MOTOR_STATUS.HOLD, 0)
        self.wheelWidth = np.mean([self.config['outer_wheel_base'], self.config['inner_wheel_base']])


    def set_motor_power(self, port, power):
        motor = self.__motorFromPort__(port)
        match motor:
            case WHEEL.LEFT:
                self.left_motor_status = (MOTOR_STATUS.POWER_GOAL, power)
            case WHEEL.RIGHT:
                self.right_motor_status = (MOTOR_STATUS.POWER_GOAL, power)
            case WHEEL.NONE:
                print("Virtual Robot: Trying to set power of unattached port.")

    def set_motor_position(self, port, position):
        wheel = self.__motorFromPort__(port)
        if wheel == WHEEL.LEFT:
            self.left_motor_status = (MOTOR_STATUS.POSITION_GOAL, position)
        else:
            self.right_motor_status = (MOTOR_STATUS.POSITION_GOAL,  position)

    def updateMotor(self, motor: motor.Motor, status, dt: float) -> bool:
        """Update a motor depending on its status. 

        Args:
            motor (motor.Motor): The motor.
            status (_type_): The motor status.

        Returns:
            bool: Whether or not this status can be moved into locked.
        """
        match status[0]:
            # PID Goes here in the future
            case MOTOR_STATUS.POSITION_GOAL:
                # Simple proportional controller
                difference = status[1] - motor.getEncoder()
                print("diff:", difference)
                if abs(difference) < POSITION_CONTROL_REACHED:
                    print("End reached")
                    return True
                
                motor.update(cm.bound(difference * 2, -100, 100), 0, dt)

            case MOTOR_STATUS.HOLD:
                motor.update(0, 0, dt)

            case _:
                print("----- UNKNOWN INSTR -----")
        return False

    def update(self, dt):
        print("----- UPDATING -----")
        if self.updateMotor(self.left_motor, self.left_motor_status, dt):
            self.left_motor_status = (MOTOR_STATUS.HOLD, 0)
        if self.updateMotor(self.right_motor, self.right_motor_status, dt):
            self.right_motor_status = (MOTOR_STATUS.HOLD, 0)

        vel_left = self.__linear_wheel_velocity(WHEEL.LEFT)
        vel_right = self.__linear_wheel_velocity(WHEEL.RIGHT)

        dx = 0
        dy = 0
        do = 0

        if abs(vel_left - vel_right) < VEL_DIFF_MIN:
            dx = np.sin(np.deg2rad(self.orientation)) * dt * (vel_left + vel_right) / 2.0
            dy = np.cos(np.deg2rad(self.orientation)) * dt * (vel_left + vel_right) / 2.0
        else:
            radius = self.wheelWidth * (vel_left + vel_right) / (2 * (vel_right - vel_left))
            arc_angle = (vel_right - vel_left) * dt / self.wheelWidth

            # Delta forward
            df = np.sin(arc_angle) * radius
            # Delta sideways
            ds = radius - np.cos(arc_angle) * radius
            
            dx = df * np.sin(self.orientation) + ds * np.sin(270.0 + self.orientation)
            dy = df * np.cos(self.orientation) + ds * np.cos(270.0 + self.orientation)
            do = 90 - arc_angle

        self.orientation += do 
        self.x += dx
        self.y += dy

        print("virtual robot y", self.y)

        self.graphics.updateRobot(dx, dy, do)

    def get_x(self) -> float:
        return self.x
    
    def get_y(self) -> float:
        return self.y
    
    def get_orientation(self) -> float:
        return self.orientation
    
    def get_encoder_left(self) -> int:
        return self.left_motor.encoder
    
    def get_encoder_right(self) -> int:
        return self.right_motor.encoder
    
    def get_encoder(self, port) -> int:
        if self.__motorFromPort__(port) == WHEEL.LEFT:
            return self.get_encoder_left()
        else:
            return self.get_encoder_right()

    def __motorFromPort__(self, port):
        if cm.config_port_to_hw(self.config['left_motor']) == port:
            return WHEEL.LEFT
        elif cm.config_port_to_hw(self.config['right_motor']) == port:
            return WHEEL.RIGHT
        else:
            return WHEEL.NONE
    
    def __linear_wheel_velocity(self, wheel) -> float:
        """Calculate the linear velocity of a wheel (m/s).

        Args:
            wheel (enum): The wheel to calculate for.

        Returns:
            float: The linear velocity of the wheel (m/s).
        """
        angularVel = self.right_motor.getVelocity() if wheel == WHEEL.RIGHT else self.left_motor.getVelocity()
                
        print("linear wheel vel", 2 * np.pi * self.config['wheel_radius'] * angularVel / 360.0)

        return 2 * np.pi * self.config['wheel_radius'] * angularVel / 360.0
