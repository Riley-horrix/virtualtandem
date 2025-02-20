import unittest

from src.message import *

from src.lib.utils import Ref

class Reading(Message):
    def __init__(self, x: float, y: float):
        super().__init__(0)

        self.x = x
        self.y = y

    def __eq__(self, other):
        return other.x == self.x and other.y == self.y


class Sensor(Producer):
    def __init__(self, hub: MessageHub, task_handler: TaskHandler):
        super().__init__(hub)
        self.task_handler = task_handler
        # Send 5 messages
        self.repetitions: Ref[int] = Ref(0)

        def send_messages(handle: TaskHandle):
            if self.repetitions.value == 5:
                handle.cancel()
                return
            hub.deliver_message(Reading(float(self.repetitions.value), float(self.repetitions.value * 2.0)))
            self.repetitions.value += 1

        task_handler.task_interval(Task(send_messages), 10)


class Receiver(Consumer):
    def __init__(self, hub: MessageHub, message_count: list[int], messages_received: list[Message]):
        super().__init__(hub)
        self.message_count: list[int] = message_count
        self.messages_received: list[Message] = messages_received

    def get_consumed(self) -> list[int]:
        return [0]

    def send(self, message: Message):
        match message.uid:
            case 0:
                self.message_count[0] += 1
                self.messages_received.append(message)

class TestMessageHub(unittest.TestCase):
    def test_can_pass_messages(self):
        message_count: list[int] = [0]
        messages_received: list[Message] = []

        task_handler = TaskHandler()
        hub = MessageHub(task_handler)
        rec = Receiver(hub, message_count, messages_received)
        prod = Sensor(hub, task_handler)

        task_handler.start()

        self.assertListEqual(message_count, [5])
        self.assertListEqual(messages_received, [
            Reading(0.0, 0.0),
            Reading(1.0, 2.0),
            Reading(2.0, 4.0),
            Reading(3.0, 6.0),
            Reading(4.0, 8.0),
        ])

    def test_can_pass_messages_to_multiple_consumers(self):
        message_count: list[int] = [0]
        messages_received: list[Message] = []

        task_handler = TaskHandler()
        hub = MessageHub(task_handler)

        rec1 = Receiver(hub, message_count, messages_received)
        rec2 = Receiver(hub, message_count, messages_received)
        rec3 = Receiver(hub, message_count, messages_received)

        prod = Sensor(hub, task_handler)

        task_handler.start()

        self.assertListEqual(message_count, [15])

    def test_can_pass_messages_from_multiple_producers(self):
        message_count: list[int] = [0]
        messages_received: list[Message] = []

        task_handler = TaskHandler()
        hub = MessageHub(task_handler)

        rec = Receiver(hub, message_count, messages_received)

        prod1 = Sensor(hub, task_handler)
        prod2 = Sensor(hub, task_handler)

        task_handler.start()

        self.assertListEqual(message_count, [10])


if __name__ == '__main__':
    unittest.main()