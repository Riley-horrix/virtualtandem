from src.lib.configuration import Configurable, Configuration
from src.lib.math_utils import distance, signed_angle_between

from src.message import Consumer, Producer, MessageHub, MessageId
from src.messages import Message, NavigationEstimate, TerminateRequest, MoveRequest, StartRequest
from src.service import Service
from src.task_handler import TaskHandle, TaskHandler, Task


class Navigator(Consumer, Producer, Configurable, Service):
    """
    The Navigator class is responsible for managing navigation tasks for a robot. 
    It consumes navigation position estimates and processes them to emit move requests 
    for the robot's movement. This class acts as a middle layer ensuring that position 
    estimates are appropriately handled and translated into actionable movement commands.

    It can take in a list of waypoints and use them to emit move requests.
    """
    def __init__(self, hub: MessageHub, task_handler: TaskHandler):
        Configurable.__init__(self, "Navigator")
        Consumer.__init__(self, hub)
        Producer.__init__(self, hub)

        self.task_handler: TaskHandler = task_handler
        self.waypoints: list[tuple[float, float]] = []
        self.emit_handle: TaskHandle | None = None
        self.waypoint_index: int = 0
        self.waypoint_threshold: float = 0.0
        self.interval_ms: int = 0
        self.nav_estimate: NavigationEstimate | None = None

        self.startup_wait: int = 0
        self.waypoint_wait: int = 0
        self.terminate_wait: int = 0

    def initialise(self, conf: Configuration = None):
        Configurable.initialise(self, conf)

        waypoints_x = self.get_conf_list_f("waypoints_x")
        waypoints_y = self.get_conf_list_f("waypoints_y")

        if len(waypoints_x) != len(waypoints_y):
            raise ValueError("[Navigator]: waypoints_x and waypoints_y must be the same length")

        self.waypoints = list(zip(waypoints_x, waypoints_y))

        self.interval_ms = self.get_conf_num("interval_ms")
        self.waypoint_threshold = self.get_conf_num_f("waypoint_threshold")

        self.startup_wait = self.get_conf_num_f("startup_wait")
        self.waypoint_wait = self.get_conf_num_f("waypoint_wait")
        self.terminate_wait = self.get_conf_num_f("stop_wait")

    def send(self, message: Message):
        if isinstance(message, NavigationEstimate):
            self.nav_estimate = message
        if isinstance(message, TerminateRequest):
            self.stop()
        if isinstance(message, StartRequest):
            self.task_handler.task_delay(Task(lambda _: self.start()), self.startup_wait)

    def get_consumed(self) -> list[MessageId]:
        return [
            MessageId.NAVIGATION_ESTIMATE,
            MessageId.START_REQUEST,
            MessageId.TERMINATE_REQUEST,
        ]

    def emit_move_request(self):
        if self.nav_estimate is None:
            return
        current_position = (self.nav_estimate.x, self.nav_estimate.y)
        current_waypoint = self.waypoints[self.waypoint_index]

        # Goal reached check
        if distance(current_waypoint, current_position) < self.waypoint_threshold:
            self.waypoint_index += 1
            if self.waypoint_index >= len(self.waypoints):
                current_waypoint = self.waypoints[self.waypoint_index]
                self.stop()
                self.task_handler.task_delay(Task(lambda _: self.start()), self.waypoint_wait)
            else:
                # If waypoints reached then terminate the robot
                self.task_handler.task_delay(Task(lambda _: self.deliver(TerminateRequest())), self.terminate_wait)

            # When waypoint reached, send a request to not move
            self.deliver(MoveRequest(self.nav_estimate.theta, 0.0))
            return

        relative_waypoint = (current_waypoint[0] - current_position[0], current_waypoint[1] - current_position[1])
        angle_to_waypoint = signed_angle_between((0, 1), relative_waypoint)
        self.deliver(MoveRequest(angle_to_waypoint, distance(current_waypoint, current_position)))

    def start(self) -> None:
        self.stop()
        self.emit_handle = self.task_handler.task_interval(Task(lambda _: self.emit_move_request), self.interval_ms)

    def stop(self) -> None:
        if self.emit_handle is not None:
            self.emit_handle.cancel()
            self.emit_handle = None
