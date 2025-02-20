from src.message import TimedMessage

from enum import Enum

class MessageIds(Enum):
    SONAR_READING: int = 0
    NAVIGATION_ESTIMATE: int = 1
    MOVE_REQUEST: int = 2
    TERMINATE_REQUEST: int = 3

class SonarReading(TimedMessage):
    def __init__(self, reading_m: float):
        super().__init__(MessageIds.SONAR_READING.value)
        self.reading_m = reading_m

class NavigationEstimate(TimedMessage):
    def __init__(self, x: float, y: float):
        super().__init__(MessageIds.NAVIGATION_ESTIMATE.value)
        self.x = x
        self.y = y

class MoveRequest(TimedMessage):
    def __init__(self, x: float, y: float):
        super().__init__(MessageIds.MOVE_REQUEST.value)
        self.x = x
        self.y = y

class TerminateRequest(TimedMessage):
    def __init__(self):
        super().__init__(MessageIds.TERMINATE_REQUEST.value)
