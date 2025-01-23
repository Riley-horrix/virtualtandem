import hardware.virtual.motor as motor

class VirtualRobot:
    def __init__(self):
        print("Initialising Virtual Robot")
        self.x = 0
        self.y = 0
        self.orientation = 0
        self.vel = 0
        self.acc = 0
        self.motorL = motor.Motor("LegoMotor")
        self.motorR = motor.Motor("LegoMotor")

    # def update

