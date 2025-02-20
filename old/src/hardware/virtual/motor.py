import toml
import sys

class Motor:
    def __init__(self, config_type):
        print("Initialising Virtual Motors")
        self.config = config_type
        with open("config/motor_config.toml") as stream:
            try:
                self.config = toml.load(stream)[config_type]
                print(self.config)
            except toml.TomlDecodeError as err:
                print(err)
                sys.exit(-1)
        self.encoder = 0    # Encoder value
        self.ang_vel = 0    # Angular velocity (degrees / s)
        self.ang_acc = 0    # Angular acceleration (degrees / s^2)

    def update(self, power, torque, dt) -> float:
        """Send a pwm signal into the motor.

        Args:
            power (float): Percentage duty cycle sent to motor [-100, 100].
            torque (float): The current torque on the motor (Nm).
            dt (float): Time passed since last update (s).
        """
        # Calculate normal rpm from power and bound it by the torque
        self.encoder += self.ang_vel * dt * self.config['encoder_degrees']
        print("----- MOTOR ENCODER -----",self.encoder)
        rpm = min(self.config['rpm_power_a'] * power, self.config['rpm_torque_a'] + self.config['rpm_torque_b'] * torque)

        self.ang_vel = rpm * 6.0

        return dt

    def getEncoder(self) -> int:
        """Get the encoder value for the motor.

        Returns:
            int: The current motor encoder value.
        """
        return round(self.encoder)
    
    def getVelocity(self) -> float:
        """Get the current angular velocity of the motor.

        Returns:
            float: The current velocity of the motor (degrees / s).
        """
        return self.ang_vel