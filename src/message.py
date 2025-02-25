from abc import ABC, abstractmethod

from src.task_handler import TaskHandle, TaskHandler, Task
from src.messages import MessageId, Message

class Producer(ABC):
    """
    Defines a base class to manage the delivery of messages through an
    associated MessageHub.

    The Producer class facilitates the communication by delivering messages
    to a central hub (MessageHub) through a `deliver` function. This enables
    routing or processing of messages to appropriate destinations defined within
    the hub. It acts as an interface for sending messages, ensuring proper
    delivery through the hub.
    """

    def __init__(self, hub: "MessageHub"):
        self._hub: "MessageHub" = hub

    def deliver(self, message: Message) -> None:
        """
        Deliver a message using the MessageHub.

        This method takes a `Message` object and delivers it through the associated hub.

        :param message: The message object to be delivered through the hub.

        :return: None
        """
        self._hub.deliver_message(message)


class Consumer(ABC):
    """
    Defines an abstract base class for a Consumer that interacts with a MessageHub.

    The Consumer serves as a mechanism for consuming and processing messages from
    a central message hub. Implementing classes should define specific behaviors
    for sending messages and retrieving consumed message identifiers.

    :method send: Consume and process a message.
    """
    def __init__(self, hub: "MessageHub"):
        self._hub: "MessageHub" = hub
        self._hub.add_consumer(self)

    @abstractmethod
    def send(self, message: Message):
        """
        Consume and process a message.

        Child classes should override this method to define specific behaviors for
        processing messages.

        Example send message implementation:

        ```python

        def send(self, message: Message):
            match message.uid:
                case MessageIds.SonarReading:
                    sonar: SonarReading = message
                    print(sonar.reading_m)
                    
        ```

        :param message: The message object to be processed by the Consumer.
        :return: None
        """
        pass

    @abstractmethod
    def get_consumed(self) -> list[MessageId]:
        """
        Get the list of message identifiers consumed by this Consumer.
        
        This should be implemented by child classes to return a list of messages they
        desire to consume from the associated MessageHub.

        ```python

        def get_consumed(self) -> list[MessageId]:
            return [
                MessageIds.SONAR_READING,
                MessageIds.MOVE_REQUEST
            ]

        ```
        """
        pass


class MessageHub:
    def __init__(self, task_handler: TaskHandler):
        self.consumers: dict[MessageId, list[Consumer]] = {}
        self.message_queue: list[Message] = []
        self.message_flush_handle: TaskHandle | None = None
        self.task_handler: TaskHandler = task_handler

    def add_consumer(self, consumer: Consumer) -> None:
        """
        Add a consumer to listen for messages on this MessageHub.

        :param consumer: The consumer to add.
        :return: None
        """
        for uid in consumer.get_consumed():
            if uid in self.consumers:
                self.consumers[uid].append(consumer)
            else:
                self.consumers[uid] = [consumer]

    def deliver_message(self, message: Message) -> None:
        """
        Deliver a message to all registered Consumers.

        :param message: The message to deliver to consumers on this MessageHub.
        :return: None
        """
        self.message_queue.append(message)
        if not self.message_flush_handle:
            self.message_flush_handle = self.task_handler.task_delay(Task(lambda _: self.flush_messages()), 0)

    def flush_messages(self) -> None:
        """
        Process and dispatch all messages in the queue to the appropriate consumers.
    
        This function clears the message queue by iterating over all queued messages
        and delivering each to the consumers registered for the message's unique ID.
    
        :return: None
        """
        self.message_flush_handle = None
        messages = self.message_queue
        self.message_queue = []

        for message in messages:
            uid = message.uid
            if uid not in self.consumers:
                continue
            for consumer in self.consumers[uid]:
                consumer.send(message)
