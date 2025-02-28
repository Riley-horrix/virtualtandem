import math

from src.lib.configuration import Configurable, Configuration, ConfigurationException
from src.message import Consumer, Producer, MessageHub
from src.messages import MessageId, Message, NavigationEstimate, MoveRequest
from src.service import Service
from src.task_handler import TaskHandler, Task, TaskHandle

from src.drivers.brickpi3 import bp_global_context, BrickPi3

class MotorController(Service, Consumer, Producer, Configurable):
    def __init__(self, hub: MessageHub, task_handler: TaskHandler):
        Consumer.__init__(self, hub)
        Producer.__init__(self, hub)
        Configurable.__init__(self, "MotorController")

        self.bp: BrickPi3 = bp_global_context

        self.task_handler = task_handler

        self.nav_estimate: NavigationEstimate | None = None
        self.move_request: MoveRequest        | None = None

        self.emit_handle: TaskHandle | None = None
        self.interval_ms: int = 0

        self.left_motor_port: int = 0
        self.right_motor_port: int = 0

        self.max_power: float = 0.0
        self.max_dps: float = 0.0

        self.encoder_cps: int = 0

        self.turn_encoder_a: float = 0.0
        self.turn_encoder_b: float = 0.0
        self.move_encoder_a: float = 0.0
        self.move_encoder_b: float = 0.0

        self.wheel_radius: float = 0.0
        self.wheel_base: float = 0.0

        self.left_motor_encoder: int = 0
        self.right_motor_encoder: int = 0

    def initialise(self, conf: Configuration = None):
        Configurable.initialise(self, conf)
        self.interval_ms = self.get_conf_num("interval_ms")

        self.left_motor_port = self.port_str_to_port(self.get_conf_str("left_motor_port"))
        self.right_motor_port = self.port_str_to_port(self.get_conf_str("right_motor_port"))

        self.max_power = self.get_conf_num_f("max_power")
        self.max_dps = self.get_conf_num_f("max_dps")

        self.bp.set_motor_limits(self.left_motor_port, self.max_power, self.max_dps)
        self.bp.set_motor_limits(self.right_motor_port, self.max_power, self.max_dps)

        self.bp.reset_motor_encoder(self.left_motor_port)
        self.bp.reset_motor_encoder(self.right_motor_port)

        self.left_motor_encoder = 0
        self.right_motor_encoder = 0

        self.turn_encoder_a = self.get_conf_num_f("turn_encoder_a")
        self.turn_encoder_b = self.get_conf_num_f("turn_encoder_b")
        self.move_encoder_a = self.get_conf_num_f("move_encoder_a")
        self.move_encoder_b = self.get_conf_num_f("move_encoder_b")

        self.encoder_cps = self.get_conf_num("encoder_cps")

        self.wheel_radius = self.get_conf_num_f("wheel_radius")
        self.wheel_base = self.get_conf_num_f("wheel_base")

    def port_str_to_port(self, port_str: str) -> int:
        if port_str == "port_A":
            return self.bp.PORT_A
        elif port_str == "port_B":
            return self.bp.PORT_B
        elif port_str == "port_C":
            return self.bp.PORT_C
        elif port_str == "port_D":
            return self.bp.PORT_D
        else:
            raise ConfigurationException(f"[MotorController]: Invalid motor port string: {port_str}")

    def send(self, message: Message):
        if isinstance(message, NavigationEstimate):
            self.nav_estimate = message
        if isinstance(message, MoveRequest):
            self.move_request = message

    def get_consumed(self) -> list[MessageId]:
        return [
            MessageId.NAVIGATION_ESTIMATE,
            MessageId.MOVE_REQUEST,
        ]

    def loop(self, handle: TaskHandle):
        # Read encoder offsets, send motor commands and emit move and turn estimates
        if self.nav_estimate is None or self.move_request is None:
            return

        left_encoder = self.bp.get_motor_encoder(self.left_motor_port)
        right_encoder = self.bp.get_motor_encoder(self.right_motor_port)

        if left_encoder is None or right_encoder is None:
            return

        current_heading = self.nav_estimate.theta
        requested_move = self.move_request.theta

        if abs(current_heading - requested_move) > 1.0:
            self.request_turn(left_encoder, right_encoder)
        else:
            self.request_move(left_encoder, right_encoder)

    def request_turn(self) -> None:
        """
        Send turn commands to the motors.
        :return: None
        """
        pass

    def request_move(self, left_encoder: int, right_encoder: int) -> None:
        """
        Send a straight move command to the motors.
        :return: None
        """
        distance = self.move_request.distance
        encoder_turns = self.encoder_cps * distance / (self.wheel_radius * self.wheel_radius * math.pi)
        encoder_turns = round(encoder_turns * self.turn_encoder_a + self.turn_encoder_b)
        self.bp.set_motor_position(self.left_motor_port, left_encoder + encoder_turns)
        self.bp.set_motor_position(self.right_motor_port, right_encoder + encoder_turns)


    def start(self):
        self.stop()
        self.emit_handle = self.task_handler.task_interval(Task(self.loop), self.interval_ms)

    def stop(self):
        if self.emit_handle is not None:
            self.emit_handle.cancel()
            self.emit_handle = None
