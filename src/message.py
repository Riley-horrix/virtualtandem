from abc import ABC, abstractmethod

from src.lib.time_utils import current_time_ms

from src.task_handler import TaskHandle, TaskHandler, Task


class Message:
    def __init__(self, uid: int):
        self.uid: int = uid

class TimedMessage(Message):
    def __init__(self, uid: int):
        super().__init__(uid)
        self.time: int = current_time_ms()


class Producer:
    def __init__(self, hub: "MessageHub"):
        self._hub: "MessageHub" = hub

    def deliver(self, message: Message):
        self._hub.deliver_message(message)


class Consumer(ABC):
    def __init__(self, hub: "MessageHub"):
        self._hub: "MessageHub" = hub
        self._hub.add_consumer(self)

    @abstractmethod
    def send(self, message: Message):
        pass

    @abstractmethod
    def get_consumed(self) -> list[int]:
        pass

class MessageHub:
    def __init__(self, task_handler: TaskHandler):
        self.consumers: dict[int, list[Consumer]] = {}
        self.message_queue: list[Message] = []
        self.message_flush_handle: TaskHandle | None = None
        self.task_handler: TaskHandler = task_handler

    def add_consumer(self, consumer: Consumer):
        for uid in consumer.get_consumed():
            if uid in self.consumers:
                self.consumers[uid].append(consumer)
            else:
                self.consumers[uid] = [consumer]

    def deliver_message(self, message: Message):
        self.message_queue.append(message)
        if not self.message_flush_handle:
            self.message_flush_handle = self.task_handler.task_delay(Task(lambda _: self.flush_messages()), 0)

    def flush_messages(self):
        self.message_flush_handle = None
        messages = self.message_queue
        self.message_queue = []

        for message in messages:
            uid = message.uid
            for consumer in self.consumers[uid]:
                consumer.send(message)
