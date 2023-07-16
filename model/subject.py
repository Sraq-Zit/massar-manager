
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Set


if TYPE_CHECKING:
    from model.session import Session
    from model.level import Level


@dataclass
class Subject:
    id: int
    name: str
    levels: Set['Level']
    sessions: Dict[str, 'Session']

    def __str__(self):
        return self.name
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other: 'Subject'):
        return self.id == other.id
    