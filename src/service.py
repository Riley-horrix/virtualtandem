from abc import ABC, abstractmethod


class Service(ABC):
    """
    Represents a class that has a stoppable / start-able state.

    Should be a Consumer and consume Start and Terminate messages.

    ```python
    def send(self, message: Message) -> None:
        if isinstance(message, TerminateRequest):
            self.stop()
        if isinstance(message, StartRequest):
            self.start()

    def get_consumed(self) -> list[MessageId]:
        return [
            MessageId.TERMINATE_REQUEST,
            MessageId.START_REQUEST,
        ]
    ```
    """
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass