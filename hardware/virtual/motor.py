import toml

class Motor:
    def __init__(self, config_type):
        print("Initialising Virtual Motors")
        self.config = config_type
        with open("virtualConfig/motor_config.toml") as stream:
            try:
                self.config = toml.load(stream)
                print(self.config[config_type])
            except toml.TomlDecodeError as err:
                print(err)
                sys.exit(-1)
        self.encoder = 0                                    # Encoder value
        self.ang_vel = 0                                    # Angular velocity (degrees / s)
        self.ang_acc = 0                                    # Angular acceleration (degrees / s^2)

    def update(power, torque) -> float:
        """Send a pwm signal into the motor.

        Args:
            power (float): Percentage duty cycle sent to motor [-100, 100].
            torque (float): The current torque on the motor (Nm).
        """
        pass

    def getEncoder() -> int:
        """Get the encoder value for the motor.

        Returns:
            int: The current motor encoder value.
        """
        return self.encoder