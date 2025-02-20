from src.message import Producer, MessageHub

from src.messages import SonarReading

from src.lib.configuration import Configurable
from src.task_handler import TaskHandler, Task


class Sonar(Producer, Configurable):
    def __init__(self, hub: MessageHub, task_handler: TaskHandler):
        super().__init__(hub)
        self.task_handler = task_handler

        self.interval_ms = self.conf.get_conf_num("Sonar", "interval_ms")
        self.emit_handle = self.task_handler.task_interval(Task(self._emit_sonar()), self.interval_ms)

    def _emit_sonar(self):
        reading_m = self._read_sonar_m()
        self.deliver(SonarReading(reading_m))

    def _read_sonar_m(self) -> float:
        return 1.0

