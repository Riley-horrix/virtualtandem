from src.message import Producer, MessageHub, Consumer

from src.messages import SonarReading, MessageId, Message, TerminateRequest, VirtualSonarRequest, VirtualSonarResponse

from src.lib.configuration import Configurable, Configuration
from src.service import Service
from src.task_handler import TaskHandler, Task, TaskHandle


class Sonar(Producer, Consumer, Configurable, Service):
    def __init__(self, hub: MessageHub, task_handler: TaskHandler):
        Producer.__init__(self, hub)
        Consumer.__init__(self, hub)
        Configurable.__init__(self, "Sonar")
        self.task_handler = task_handler
        self.interval_ms: int = 0
        self.emit_handle: TaskHandle | None = None

        self.std: float = 0.0
        self.constant_std: float = 0.0
        self.normal_std: float = 0.0

    def initialise(self, conf: Configuration = None):
        self.virtual = self.get_conf_str("virtual") == "true"
        self.interval_ms = self.get_conf_num("interval_ms")

        self.std = self.get_conf_num_f("std")
        self.constant_std = self.get_conf_num_f("constant_std")
        self.normal_std = self.get_conf_num_f("normal_std")

    def read_and_emit_sonar(self, _: TaskHandle):
        reading_m = 1.0
        self.deliver(SonarReading(reading_m, self.std, self.constant_std, self.normal_std))

    def send(self, message: Message) -> None:
        if isinstance(message, VirtualSonarResponse):
            self.deliver(SonarReading(message.reading_m, self.std, self.constant_std, self.normal_std))
        if isinstance(message, TerminateRequest):
            self.stop()

    def get_consumed(self) -> list[MessageId]:
        return [
            MessageId.TERMINATE_REQUEST
        ]

    def start(self):
        self.emit_handle = self.task_handler.task_interval(Task(self.read_and_emit_sonar), 100)

    def stop(self):
        if self.emit_handle is not None:
            self.emit_handle.cancel()
            self.emit_handle = None
