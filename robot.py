import toml
import sys
import time
import numpy as np

import hardware.hardwareInterface as hw
import hardware.enumeration as enum
import common as cm

GOAL_COMPLETE_DISTANCE = 0.1

def getHardware(is_virtual) -> hw.HardwareInterface:
    if is_virtual:
        import hardware.virtualInterface as vi
        return vi.VirtualInterface()
    else:
        import hardware.physicalInterface as pi
        return pi.PhysicalInterface()

class Robot:
    def __init__(self, config_path):
        print("Initializing Robot")

        with open(config_path) as stream:
            try:
                self.config = toml.load(stream)
            except toml.TomlDecodeError as err:
                print(err)
                sys.exit(-1)

        self.hw = getHardware(self.config["virtual"])
        self.ready = True   # Ready to execute next instruction

    def start(self):
        """Start the robot executing the commands in the config.
        """
        print("Robot starting")
        commandInd = 0
        currentTime = time.time()
        previousTime = time.time()
        while True:
            if commandInd >= len(self.config['commands']) and self.ready:
                break
            if self.ready:
                self.currentCommand = self.config['commands'][commandInd]
                self.currentCommandState = ()
                commandInd += 1

            dt = currentTime - previousTime

            self.update(dt)
            self.hw.update(dt)
    
    def update(self, dt):
        match self.currentCommand['type']:
            case "FORWARDS":
                self.updateForwards(dt)
            case _:
                print(f"Robot: Unrecognized command : {self.currentCommand['type']}")

    def updateForwards(self, dt):
        if self.ready:
            self.ready = False
            rotations = self.currentCommand['distance'] / (2 * np.pi * self.config['robot']['wheel_radius'])
            self.encoderTargetLeft = self.hw.get_motor_encoder(self.__get_hardware_motor_port__(True)) + rotations * 360
            self.encoderTargetRight = self.hw.get_motor_encoder(self.__get_hardware_motor_port__(False)) + rotations * 360
            self.hw.set_motor_position(self.__get_hardware_motor_port__(True), self.encoderTargetLeft)
            self.hw.set_motor_position(self.__get_hardware_motor_port__(False), self.encoderTargetRight)

        if abs(self.hw.get_motor_encoder(self.__get_hardware_motor_port__(True)) - self.encoderTargetLeft) < GOAL_COMPLETE_DISTANCE:
            self.ready = True
            return

    def __get_hardware_motor_port__(self, isLeft):
        if isLeft:
            return cm.config_port_to_hw(self.config['robot']['left_motor'])
        else:
            return cm.config_port_to_hw(self.config['robot']['right_motor'])