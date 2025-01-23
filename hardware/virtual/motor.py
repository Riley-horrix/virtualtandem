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

        self.encoder = 0
        self.velocity = 0
        self.acceleration = 0

    def set_pwm_input(pwm):
        """Send a pwm signal into the motor.

        Args:
            pwm (int): Integer in the range [-1024, 1024]
        """
        pass