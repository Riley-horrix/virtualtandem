from src.drivers.motor_controller import MotorController
from src.drivers.sonar import Sonar
from src.lib.csv_logger import CSVLogger
from src.mc_estimator import MonteCarloPositionEstimator
from src.message import MessageHub
from src.messages import StartRequest, InitialiseRequest, TerminateRequest
from src.navigator import Navigator
from src.task_handler import TaskHandler


class Robot:
    def __init__(self):
        self.task_handler = TaskHandler()
        self.message_hub = MessageHub(self.task_handler)

        # Physical components
        self.sonar = Sonar(self.message_hub, self.task_handler)
        self.motor = MotorController(self.message_hub, self.task_handler)

        # Virtual components
        self.estimator = MonteCarloPositionEstimator(self.message_hub)
        self.logger = CSVLogger(self.message_hub)
        self.navigator = Navigator(self.message_hub, self.task_handler)

    def start(self):
        print("[Robot]: Starting robot")
        self.message_hub.deliver_message(InitialiseRequest())
        self.message_hub.deliver_message(StartRequest())

        try:
            self.task_handler.start()
        except KeyboardInterrupt:
            self.message_hub.deliver_message(TerminateRequest())