import hardware.enumeration as enum

SENSOR_PORTS = enum.Enumeration("""
    PORT_1,
    PORT_2,
    PORT_3,
    PORT_4,
""")

MOTOR_PORTS = enum.Enumeration("""
    PORT_A,
    PORT_B,
    PORT_C,
    PORT_D,
""")

class HardwareInterface:
    def set_motor_power(self, port, power):
        """
        Set the motor power in percent

        Keyword arguments:
        port -- The Motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        power -- The power from -100 to 100, or -128 for float
        """
        raise "Method not defined"

    def set_motor_position(self, port, position):
        """
        Set the motor target position in degrees

        Keyword arguments:
        port -- The motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        position -- The target position
        """
        raise "Method not defined"

    def set_motor_position_relative(self, port, degrees): 
        """
        Set the relative motor target position in degrees. Current position plus the specified degrees.

        Keyword arguments:
        port -- The motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        degrees -- The relative target position in degrees
        """
        raise "Method not defined"

    def set_motor_position_kp(self, port, kp = 25):
        """
        Set the motor target position KP constant

        If you set kp higher, the motor will be more responsive to errors in position, at the cost of perhaps overshooting and oscillating.
        kd slows down the motor as it approaches the target, and helps to prevent overshoot.
        In general, if you increase kp, you should also increase kd to keep the motor from overshooting and oscillating.

        Keyword arguments:
        port -- The motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        kp -- The KP constant (default 25)
        """
        raise "Method not defined"

    def set_motor_position_kd(self, port, kd = 70):
        """
        Set the motor target position KD constant

        If you set kp higher, the motor will be more responsive to errors in position, at the cost of perhaps overshooting and oscillating.
        kd slows down the motor as it approaches the target, and helps to prevent overshoot.
        In general, if you increase kp, you should also increase kd to keep the motor from overshooting and oscillating.

        Keyword arguments:
        port -- The motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        kd -- The KD constant (default 70)
        """
        raise "Method not defined"

    def set_motor_dps(self, port, dps):
        """
        Set the motor target speed in degrees per second

        Keyword arguments:
        port -- The motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        dps -- The target speed in degrees per second
        """
        raise "Method not defined"


    def set_motor_limits(self, port, power = 0, dps = 0):
        """
        Set the motor speed limit

        Keyword arguments:
        port -- The motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        power -- The power limit in percent (0 to 100), with 0 being no limit (100)
        dps -- The speed limit in degrees per second, with 0 being no limit
        """
        raise "Method not defined"

    def get_motor_status(self, port):
        """
        Read a motor status

        Keyword arguments:
        port -- The motor port (one at a time). PORT_A, PORT_B, PORT_C, or PORT_D.

        Returns a list:
            flags -- 8-bits of bit-flags that indicate motor status:
                bit 0 -- LOW_VOLTAGE_FLOAT - The motors are automatically disabled because the battery voltage is too low
                bit 1 -- OVERLOADED - The motors aren't close to the target (applies to position control and dps speed control).
            power -- the raw PWM power in percent (-100 to 100)
            encoder -- The encoder position
            dps -- The current speed in Degrees Per Second
        """
        raise "Method not defined"

    def get_motor_encoder(self, port):
        """
        Read a motor encoder in degrees

        Keyword arguments:
        port -- The motor port (one at a time). PORT_A, PORT_B, PORT_C, or PORT_D.

        Returns the encoder position in degrees
        """
        raise "Method not defined"


    def offset_motor_encoder(self, port, position):
        """
        Offset a motor encoder

        Keyword arguments:
        port -- The motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        offset -- The encoder offset

        You can zero the encoder by offsetting it by the current position
        """
        raise "Method not defined"


    def reset_motor_encoder(self, port):
        """
        Reset motor encoder(s) to 0

        Keyword arguments:
        port -- The motor port(s). PORT_A, PORT_B, PORT_C, and/or PORT_D.
        """
        raise "Method not defined"
