from src.lib.time_utils import current_time_ms

from enum import Enum

class MessageId(Enum):
    """
    Collection of all message IDs used in the simulation.

    These must all be unique.
    """
    SONAR_READING: int =        0
    NAVIGATION_ESTIMATE: int =  1
    MOVE_REQUEST: int =         2
    TERMINATE_REQUEST: int =    3
    MOVE_ESTIMATE: int =        4


class Message:
    """
    Represents a message with a unique identifier.

    Attributes:
        uid: int
            The unique identifier of this message.
    """

    def __init__(self, uid: MessageId):
        self.uid: MessageId = uid


class TimedMessage(Message):
    """
    Represents a message with an associated timestamp.

    Attributes:
        time: int
            The time in milliseconds at which this message instance was created.
    """

    def __init__(self, uid: MessageId):
        super().__init__(uid)
        self.time: int = current_time_ms()


class SonarReading(TimedMessage):
    """
    Represents a sonar reading message with a timestamp.

    Attributes:
        reading_m: A float representing the sonar reading in meters.
    """
    def __init__(self, reading_m: float):
        super().__init__(MessageId.SONAR_READING)
        self.reading_m = reading_m

class NavigationEstimate(TimedMessage):
    """
    Encapsulates navigation estimates, including positional coordinates.

    Attributes
    x : float
        The positional estimate along the x-axis.
    y : float
        The positional estimate along the y-axis.
    """
    def __init__(self, x: float, y: float):
        super().__init__(MessageId.NAVIGATION_ESTIMATE)
        self.x = x
        self.y = y

class MoveRequest(TimedMessage):
    """
    Represents a move request message with positional coordinates.

    Attributes:
    x (float): The x coordinate for the move request.
    y (float): The y coordinate for the move request.
    """
    def __init__(self, x: float, y: float):
        super().__init__(MessageId.MOVE_REQUEST)
        self.x = x
        self.y = y

class TerminateRequest(TimedMessage):
    """
    Represents a specific type of message for termination requests.
    """
    def __init__(self):
        super().__init__(MessageId.TERMINATE_REQUEST)

class MoveEstimate(TimedMessage):
    """
    Represents an actual movement message with delta coordinates and orientation.


    Attributes:
        x: The delta x-coordinate of the actual position.
        y: The delta y-coordinate of the actual position.
        theta: The orientation angle (in radians) of the actual position.
    """
    def __init__(self, x: float, y: float, theta: float):
        super().__init__(MessageId.MOVE_ESTIMATE)
        self.x = x
        self.y = y
        self.theta = theta