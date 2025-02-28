from src.lib.time_utils import current_time_ms

from enum import Enum

class MessageId(Enum):
    """
    Collection of all message IDs used in the simulation.

    These must all be unique.
    """
    SONAR_READING: int =            0
    VIRTUAL_SONAR_REQUEST: int =    1
    VIRTUAL_SONAR_RESPONSE: int =   2

    NAVIGATION_ESTIMATE: int =      10
    MOVE_ESTIMATE: int =            11
    TURN_ESTIMATE: int =            12
    CIRCULAR_MOVE_ESTIMATE: int =   13

    MOVE_REQUEST: int =             20
    TERMINATE_REQUEST: int =        21


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
        std: A float representing the uncertainty of the sonar reading.
    """
    def __init__(self, reading_m: float, std: float, constant_std: float, normal_std: float):
        super().__init__(MessageId.SONAR_READING)
        self.reading_m = reading_m
        self.std = std
        self.constant_std = constant_std
        self.normal_std = normal_std

class NavigationEstimate(TimedMessage):
    """
    Encapsulates navigation estimates, including positional coordinates.

    Attributes
    x : float
        The positional estimate along the x-axis.
    y : float
        The positional estimate along the y-axis.
    """
    def __init__(self, x: float, y: float, theta: float):
        super().__init__(MessageId.NAVIGATION_ESTIMATE)
        self.x = x
        self.y = y
        self.theta = theta

class MoveRequest(TimedMessage):
    """
    Represents a request to perform a movement action.

    :ivar theta: The angle of rotation for the move request.
    :ivar distance: The distance to move for the move request.
    """
    def __init__(self, theta: float, distance: float):
        super().__init__(MessageId.MOVE_REQUEST)
        self.theta = theta
        self.distance = distance

class TerminateRequest(TimedMessage):
    """
    Represents a specific type of message for termination requests.
    """
    def __init__(self):
        super().__init__(MessageId.TERMINATE_REQUEST)

class MoveEstimate(TimedMessage):
    """
    Represents an estimate of movement including distance, angle, and their respective uncertainties.

    This class inherits from the TimedMessage class and is used for encapsulating
    movement estimate data such as distance moved, angle turned, and their
    associated standard deviations.

    :ivar distance: Estimated distance moved.
    :ivar distance_std: Standard deviation of the estimated distance.
    :ivar theta_std: Standard deviation of the estimated angle in radians.
    """
    def __init__(self, distance: float, distance_std: float, theta_std: float):
        super().__init__(MessageId.MOVE_ESTIMATE)
        self.distance = distance
        self.distance_std = distance_std
        self.theta_std = theta_std

class TurnEstimate(TimedMessage):
    """
    Represents an estimate of a turn of the robot.

    :ivar theta: Estimated angle turned in radians.
    :ivar theta_std: Standard deviation of the estimated angle in radians.
    """
    def __init__(self, theta: float, theta_std: float):
        super().__init__(MessageId.TURN_ESTIMATE)
        self.theta = theta
        self.theta_std = theta_std

class CircularMoveEstimate(TimedMessage):
    def __init__(self, radius: float, angle: float, std: tuple[float, float]):
        super().__init__(MessageId.CIRCULAR_MOVE_ESTIMATE)
        self.radius = radius
        self.angle = angle
        self.std = std

class VirtualSonarRequest(TimedMessage):
    """
    Represents a request for a virtual sonar reading from the geofence.
    """
    def __init__(self):
        super().__init__(MessageId.VIRTUAL_SONAR_REQUEST)

class VirtualSonarResponse(TimedMessage):
    """
    Represents a response from the geofence with a virtual sonar reading.
    """
    def __init__(self, reading_m: float):
        super().__init__(MessageId.VIRTUAL_SONAR_RESPONSE)
        self.reading_m = reading_m