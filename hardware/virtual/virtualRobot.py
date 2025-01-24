import hardware.virtual.motor as motor

class VirtualRobot:
    def __init__(self):
        print("Initialising Virtual Robot")
        # Virtual robot will need some values from the physical robot, i.e. 
        # weight, wheelbase, etc
        with open("robot_config.toml") as stream:
            try:
                self.config = toml.load(stream)
            except toml.TomlDecodeError as err:
                print(err)
                sys.exit(-1)
        self.x = 0
        self.y = 0
        self.orientation = 0
        self.vel = 0
        self.acc = 0
        self.motorL = motor.Motor("LegoMotor")
        self.motorR = motor.Motor("LegoMotor")

