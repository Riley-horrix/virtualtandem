from abc import ABC, abstractmethod

from src.lib.time_utils import current_time_ms

from enum import Enum

class MessageId(Enum):
    """
    Collection of all message IDs used in the simulation.

    These must all be unique.
    """
    SONAR_READING: int =            0

    NAVIGATION_ESTIMATE: int =      10
    MOVE_ESTIMATE: int =            11
    TURN_ESTIMATE: int =            12
    CIRCULAR_MOVE_ESTIMATE: int =   13

    MOVE_REQUEST: int =             20

    START_REQUEST: int =            30
    TERMINATE_REQUEST: int =        31

all_message_ids: list[MessageId] = [
    MessageId.SONAR_READING,
    MessageId.NAVIGATION_ESTIMATE,
    MessageId.MOVE_ESTIMATE,
    MessageId.TURN_ESTIMATE,
    MessageId.CIRCULAR_MOVE_ESTIMATE,
    MessageId.MOVE_REQUEST,
    MessageId.START_REQUEST,
    MessageId.TERMINATE_REQUEST,
]


class Message(ABC):
    """
    Represents a message with a unique identifier.

    Attributes:
        uid: int
            The unique identifier of this message.
    """

    def __init__(self, uid: MessageId):
        self.uid: MessageId = uid

    def __eq__(self, other):
        if isinstance(other, Message):
            return self.uid == other.uid
        return False

    def __hash__(self):
        return hash(self.uid)

    def get_fields(self) -> dict[str, str]:
        """
        Return a string representation of the message fields.
        """
        return {}

    @staticmethod
    def get_string() -> str:
        """
        Returns a concise string representation of the message type.
        """
        return ""

    @staticmethod
    def get_string_fields() -> list[str]:
        """
        String representation of the message fields.
        """
        return []

class TimedMessage(Message, ABC):
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

    @staticmethod
    def get_string() -> str:
        return "snr"

    def get_fields(self) -> dict[str, str]:
        return {
            "reading_m": str(self.reading_m),
            "std": str(self.std),
            "constant_std": str(self.constant_std),
            "normal_std": str(self.normal_std),
        }

    @staticmethod
    def get_string_fields() -> list[str]:
        return ["reading_m", "std", "constant_std", "normal_std"]


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

    @staticmethod
    def get_string() -> str:
        return "nav_est"

    def get_fields(self) -> dict[str, str]:
        return {
            "x": str(self.x),
            "y": str(self.y),
            "theta": str(self.theta),
        }

    @staticmethod
    def get_string_fields() -> list[str]:
        return ["x", "y", "theta"]


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

    @staticmethod
    def get_string() -> str:
        return "move_req"

    def get_fields(self) -> dict[str, str]:
        return {
            "theta": str(self.theta),
            "distance": str(self.distance),
        }

    @staticmethod
    def get_string_fields() -> list[str]:
        return ["theta", "distance"]


class StartRequest(TimedMessage):
    """
    Represents a request to start the robot / simulation.
    """
    def __init__(self):
        super().__init__(MessageId.START_REQUEST)

    @staticmethod
    def get_string() -> str:
        return "start_req"

    def get_fields(self) -> dict[str, str]:
        return {}

    @staticmethod
    def get_string_fields() -> list[str]:
        return []


class TerminateRequest(TimedMessage):
    """
    Represents a specific type of message for termination requests.
    """
    def __init__(self):
        super().__init__(MessageId.TERMINATE_REQUEST)

    @staticmethod
    def get_string() -> str:
        return "term_req"

    def get_fields(self) -> dict[str, str]:
        return {}

    @staticmethod
    def get_string_fields() -> list[str]:
        return []


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

    @staticmethod
    def get_string() -> str:
        return "move_est"

    def get_fields(self) -> dict[str, str]:
        return {
            "distance": str(self.distance),
            "distance_std": str(self.distance_std),
            "theta_std": str(self.theta_std),
        }

    @staticmethod
    def get_string_fields() -> list[str]:
        return ["distance", "distance_std", "theta_std"]


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

    @staticmethod
    def get_string() -> str:
        return "t_move_est"

    def get_fields(self) -> dict[str, str]:
        return {
            "theta": str(self.theta),
            "theta_std": str(self.theta_std),
        }

    @staticmethod
    def get_string_fields() -> list[str]:
        return ["theta", "theta_std"]


class CircularMoveEstimate(TimedMessage):
    def __init__(self, radius: float, angle: float, std: tuple[float, float]):
        super().__init__(MessageId.CIRCULAR_MOVE_ESTIMATE)
        self.radius = radius
        self.angle = angle
        self.std = std

    @staticmethod
    def get_string() -> str:
        return "c_move_est"

    def get_fields(self) -> dict[str, str]:
        return {
            "radius": str(self.radius),
            "angle": str(self.angle),
            "std_rad": str(self.std[0]),
            "std_ang": str(self.std[1]),
        }

    @staticmethod
    def get_string_fields() -> list[str]:
        return ["radius", "angle", "std_rad", "std_ang"]


def message_fields_from_id(message_id) -> list[str]:
    match message_id:
        case MessageId.SONAR_READING:
            return SonarReading.get_string_fields()
        case MessageId.NAVIGATION_ESTIMATE:
            return NavigationEstimate.get_string_fields()
        case MessageId.MOVE_ESTIMATE:
            return MoveEstimate.get_string_fields()
        case MessageId.TURN_ESTIMATE:
            return TurnEstimate.get_string_fields()
        case MessageId.CIRCULAR_MOVE_ESTIMATE:
            return CircularMoveEstimate.get_string_fields()
        case MessageId.MOVE_REQUEST:
            return MoveRequest.get_string_fields()
        case MessageId.START_REQUEST:
            return StartRequest.get_string_fields()
        case MessageId.TERMINATE_REQUEST:
            return TerminateRequest.get_string_fields()
        case _:
            raise ValueError(f"[Messages]: Unable to get message fields for message with id {message_id}")

def message_name_from_id(message_id) -> str:
    match message_id:
        case MessageId.SONAR_READING:
            return SonarReading.get_string()
        case MessageId.NAVIGATION_ESTIMATE:
            return NavigationEstimate.get_string()
        case MessageId.MOVE_ESTIMATE:
            return MoveEstimate.get_string()
        case MessageId.TURN_ESTIMATE:
            return TurnEstimate.get_string()
        case MessageId.CIRCULAR_MOVE_ESTIMATE:
            return CircularMoveEstimate.get_string()
        case MessageId.MOVE_REQUEST:
            return MoveRequest.get_string()
        case MessageId.START_REQUEST:
            return StartRequest.get_string()
        case MessageId.TERMINATE_REQUEST:
            return TerminateRequest.get_string()
        case _:
            raise ValueError(f"[Messages]: Unable to get message name for message with id {message_id}")