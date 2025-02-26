from src.message import Producer, MessageHub, Consumer

from src.messages import SonarReading, MessageId, Message, TerminateRequest, VirtualSonarRequest, VirtualSonarResponse

from src.lib.configuration import Configurable, Configuration
from src.task_handler import TaskHandler, Task, TaskHandle


class Sonar(Producer, Consumer, Configurable):
    def __init__(self, hub: MessageHub, task_handler: TaskHandler):
        Producer.__init__(self, hub)
        Consumer.__init__(self, hub)
        Configurable.__init__(self, "Sonar")
        self.task_handler = task_handler
        self.virtual: bool = True
        self.interval_ms: int = 0
        self.emit_handle: TaskHandle | None = None

        self.std: float = 0.0
        self.constant_std: float = 0.0
        self.normal_std: float = 0.0

    def initialise(self, conf: Configuration = None):
        self.virtual = self.get_conf_str("virtual") == "true"
        self.interval_ms = self.get_conf_num("interval_ms")
        self.emit_handle = self.task_handler.task_interval(Task(self._emit_sonar()), self.interval_ms)

        self.std = self.get_conf_num_f("std")
        self.constant_std = self.get_conf_num_f("constant_std")
        self.normal_std = self.get_conf_num_f("normal_std")

        if self.virtual:
            self.task_handler.task_interval(Task(self._request_virtual_sonar), 100)
        else:
            self.task_handler.task_interval(Task(self._read_and_emit_sonar), 100)

    def _request_virtual_sonar(self):
        self.deliver(VirtualSonarRequest())

    def _read_and_emit_sonar(self):
        reading_m = 1.0
        self.deliver(SonarReading(reading_m, self.std, self.constant_std, self.normal_std))

    def send(self, message: Message) -> None:
        if isinstance(message, VirtualSonarResponse):
            self.deliver(SonarReading(message.reading_m, self.std, self.constant_std, self.normal_std))
        if isinstance(message, TerminateRequest):
            if self.emit_handle:
                self.emit_handle.cancel()
                self.emit_handle = None
            return

    def get_consumed(self) -> list[MessageId]:
        return [
            MessageId.TERMINATE_REQUEST
        ]
