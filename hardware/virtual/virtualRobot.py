import toml
import sys
import numpy as np

import hardware.enumeration as enum
import hardware.virtual.motor as motor
import hardware.hardwareInterface as hw
import common as cm

MOTOR_STATUS = enum.Enumeration("""
    POWER_GOAL,
    POSITION_GOAL,
    HOLD,
    IDLE,
""")

WHEEL = enum.Enumeration("""
    RIGHT,
    LEFT,
    NONE,
""")

# Minimal difference between wheel velocities for the robot to be considered as
# 'moving forward'.
VEL_DIFF_MIN = 0.0001

class VirtualRobot:
    def __init__(self):
        print("Initialising Virtual Robot")
        # Virtual robot will need some values from the physical robot, i.e. 
        # weight, wheelbase, etc
        with open("robot_config.toml") as stream:
            try:
                self.config = toml.load(stream)['robot']
            except toml.TomlDecodeError as err:
                print(err)
                sys.exit(-1)
        self.x = 0
        self.y = 0
        self.orientation = 0
        self.left_motor = motor.Motor("LegoMotor")
        self.right_motor = motor.Motor("LegoMotor")
        self.left_motor_status = (MOTOR_STATUS.HOLD, 0.0)
        self.right_motor_status = (MOTOR_STATUS.HOLD, 0.0)
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


    def update(self, dt):
        vel_left = self.__linear_wheel_velocity(WHEEL.LEFT)
        vel_right = self.__linear_wheel_velocity(WHEEL.RIGHT)

        if abs(vel_left - vel_right) < VEL_DIFF_MIN:
            dx = np.sin(np.deg2rad(self.orientation)) * vel_left
            dy = np.cos(np.deg2rad(self.orientation)) * vel_left
            self.x += dx
            self.y += dy
            return

        radius = self.wheelWidth * (vel_left + vel_right) / (2 * (vel_right - vel_left))
        arc_angle = (vel_right - vel_left) * dt / self.wheelWidth


        # Delta forward
        df = np.sin(arc_angle) * radius
        # Delta sideways
        ds = radius - np.cos(arc_angle) * radius
        
        dx = df * np.sin(self.orientation) + ds * np.sin(270.0 + self.orientation)
        dy = df * np.cos(self.orientation) + ds * np.cos(270.0 + self.orientation)

        self.orientation += 90 - arc_angle
        self.x += dx
        self.y += dy

    def get_x(self) -> float:
        return self.x
    
    def get_y(self) -> float:
        return self.y
    
    def get_orientation(self) -> float:
        return self.orientation

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
        angularVel = 0
        match wheel:
            case WHEEL.RIGHT:
                angularVel = self.right_motor.getVelocity()
            case WHEEL.LEFT:
                angularVel = self.right_motor.getVelocity()
        return self.config['wheel_radius'] * angularVel * np.pi / 180.0