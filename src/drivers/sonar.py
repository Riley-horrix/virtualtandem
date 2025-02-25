from src.message import Producer, MessageHub, Consumer

from src.messages import SonarReading, MessageId, Message, TerminateRequest

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

    def _emit_sonar(self):
        reading_m = self._read_sonar_m()
        self.deliver(SonarReading(reading_m, self.std, self.constant_std, self.normal_std))

    def _read_sonar_m(self) -> float:
        if self.virtual:
            # Reference the virtual geofence and ray cast
            return 1.0
        else:
            # Use brickpi3 to read the sensor
            return 0.0

    def send(self, message: Message) -> None:
        if isinstance(message, TerminateRequest):
            if self.emit_handle:
                self.emit_handle.cancel()
                self.emit_handle = None
            return

    def get_consumed(self) -> list[MessageId]:
        return [
            MessageId.TERMINATE_REQUEST
        ]
