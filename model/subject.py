
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
        if getattr(self, 'id', None) is None:
            return 0
        return hash(self.id)
    
    def __eq__(self, other: 'Subject'):
        return self.id == other.id
    