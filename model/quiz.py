
from dataclasses import dataclass


@dataclass
class Quiz:
    id: int
    name: str

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other: 'Quiz'):
        return self.id == other.id