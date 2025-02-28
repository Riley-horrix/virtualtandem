from abc import ABC, abstractmethod


class Service(ABC):
    """
    Represents a class that has a stoppable / start-able state.
    """
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass