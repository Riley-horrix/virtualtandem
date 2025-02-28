from src.message import Consumer, Producer, Message, MessageHub
from src.messages import MessageId


class WorldSimController(Consumer, Producer):
    """
    The WorldSimController class is responsible for managing the communication
    between the virtual simulated world and the 'physical' controller.
    """
    def __init__(self, hub: MessageHub):
        Consumer.__init__(self, hub)
        Producer.__init__(self, hub)

    def send(self, message: Message):
        pass

    def get_consumed(self) -> list[MessageId]:
        return [
            MessageId.VIRTUAL_SONAR_REQUEST
        ]
