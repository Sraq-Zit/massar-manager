
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict

@dataclass
class Session:
    id: int
    name: str

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other: 'Session'):
        return self.id == other.id