import abc
from typing import *

from mabooia.collections.mutable import LinkedList


class Observer(abc.ABC):
    @abc.abstractmethod
    def notify(self, event=None):
        pass


class ObservableBase(abc.ABC):
    _list = None

    @abc.abstractmethod
    def unsubscribe(self, observer: Observer | Callable):
        pass

    def unsubscribe_all(self):
        self._observers.clear()

    @abc.abstractmethod
    def notify_all(self, event=None):
        pass

    @property
    def _observers(self) -> LinkedList:
        if self._list is None:
            self._list = LinkedList()

        return self._list


class Observable(ObservableBase):
    def subscribe(self, observer: Observer | Callable):
        self._observers.append(observer)
        return self

    def unsubscribe(self, observer: Observer | Callable):
        self._observers.remove(observer)
        return self

    def notify_all(self, event=None):
        for observer in self._observers:
            if isinstance(observer, Observer):
                observer.notify(event)
            else:
                observer(event)
