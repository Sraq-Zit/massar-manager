
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict
from model.section import Section

if TYPE_CHECKING:
    from model.cycle import Cycle
    from model.education import Education


@dataclass
class Level:
    id: str
    name: str
    education: 'Education'
    cycle: 'Cycle'
    sections: Dict[str, Section] = None

    def __hash__(self) -> int:
        return hash(self.id)