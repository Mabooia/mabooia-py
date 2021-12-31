from enum import Enum


class Currency(Enum):
    UNKNOWN = 0
    USD = 1
    CAD = 2

    def __str__(self):
        return self.name
