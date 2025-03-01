from src.message import Producer, MessageHub, Consumer

from src.messages import SonarReading, MessageId, Message, TerminateRequest, VirtualSonarRequest, VirtualSonarResponse, \
    StartRequest

from src.lib.configuration import Configurable, Configuration, ConfigurationException
from src.service import Service
from src.task_handler import TaskHandler, Task, TaskHandle

from src.drivers.brickpi3 import bp_global_context, BrickPi3

class Sonar(Producer, Consumer, Configurable, Service):
    def __init__(self, hub: MessageHub, task_handler: TaskHandler, conf_object: str = "Sonar"):
        Producer.__init__(self, hub)
        Consumer.__init__(self, hub)
        Configurable.__init__(self, conf_object)
        self.task_handler = task_handler
        self.interval_ms: int = 0
        self.emit_handle: TaskHandle | None = None

        self.std: float = 0.0
        self.constant_std: float = 0.0
        self.normal_std: float = 0.0

        self.bp: BrickPi3 = bp_global_context
        self.sonar_port: int = 0
        self.position: tuple[float, float] = (0.0, 0.0)

    def initialise(self, conf: Configuration = None):
        self.interval_ms = self.get_conf_num("interval_ms")

        self.std = self.get_conf_num_f("std")
        self.constant_std = self.get_conf_num_f("constant_std")
        self.normal_std = self.get_conf_num_f("normal_std")

        self.sonar_port = self.sonar_port_to_port(self.get_conf_str("sonar_port"))
        self.bp.set_sensor_type(self.sonar_port, self.bp.SENSOR_TYPE.ULTRASONIC)

        x_off = self.get_conf_num_f("position_x")
        y_off = self.get_conf_num_f("position_y")
        self.position: tuple[float, float] = (x_off, y_off)

    def sonar_port_to_port(self, sonar_port: str) -> int:
        if sonar_port == "port_1":
            return self.bp.PORT_1
        elif sonar_port == "port_2":
            return self.bp.PORT_2
        elif sonar_port == "port_3":
            return self.bp.PORT_3
        elif sonar_port == "port_4":
            return self.bp.PORT_4
        else:
            raise ConfigurationException(f"[Sonar]: Invalid sonar port string: {sonar_port}")

    def read_and_emit_sonar(self, _: TaskHandle):
        reading_m = 1.0
        self.deliver(SonarReading(reading_m, self.std, self.constant_std, self.normal_std))

    def send(self, message: Message) -> None:
        if isinstance(message, TerminateRequest):
            self.stop()
        if isinstance(message, StartRequest):
            self.start()

    def get_consumed(self) -> list[MessageId]:
        return [
            MessageId.TERMINATE_REQUEST,
            MessageId.START_REQUEST,
        ]

    def start(self):
        self.emit_handle = self.task_handler.task_interval(Task(self.read_and_emit_sonar), 100)

    def stop(self):
        if self.emit_handle is not None:
            self.emit_handle.cancel()
            self.emit_handle = None
