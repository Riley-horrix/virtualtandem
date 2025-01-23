import hardware.hardwareInterface as hw
import brickpi3

bp = brickpi3.BrickPi3()

class PhysicalInterface(hw.HardwareInterface):
    def __init__(self):
        print("Physical Interface Initialising")

    def set_motor_power(self, port, power):
        return bp.set_motor_power(port, power)

    def set_motor_position(self, port, position):
        return bp.set_motor_position(port, position)

    def set_motor_position_relative(self, port, degrees): 
        return bp.set_motor_position_relative(port, degrees)

    def set_motor_position_kp(self, port, kp = 25):
        return bp.set_motor_position_kp(port, kp)

    def set_motor_position_kd(self, port, kd = 70):
        return bp.set_motor_position_kd(port, kd)

    def set_motor_dps(self, port, dps):
        return bp.set_motor_dps(port, dps)

    def set_motor_limits(self, port, power = 0, dps = 0):
        return bp.set_motor_limits(port, power, dps)

    def get_motor_status(self, port):
        return bp.get_motor_status(port)

    def get_motor_encoder(self, port):
        return bp.get_motor_encoder(port)

    def offset_motor_encoder(self, port, position):
        return bp.offset_motor_encoder(port, position)

    def reset_motor_encoder(self, port):
        return bp.reset_motor_encoder(port)
