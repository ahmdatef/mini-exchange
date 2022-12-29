import abc


class Consumer(abc.ABC):
    @abc.abstractmethod
    def connect(self, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def disconnect(self, **kwargs) -> None:
        pass
