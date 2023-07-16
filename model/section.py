
from dataclasses import dataclass
import shutil
from typing import TYPE_CHECKING, Dict
from model.student import Student

if TYPE_CHECKING:
    from model.level import Level



@dataclass
class Section:
    id: str
    name: str
    level: 'Level'
    students: Dict[str, Student] = None

    def __hash__(self) -> int:
        return hash(self.id)
    
    def __str__(self) -> str:
        width = shutil.get_terminal_size().columns
        title = f'{self.name} ({self.level.name})'
        title = title.center(width, '=')
        return f'{title}\n' + \
                '\n'.join(map(str, self.students.values())) + \
                '\n' + (width * '=') + '\n'