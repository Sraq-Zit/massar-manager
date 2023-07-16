
from dataclasses import dataclass
from datetime import datetime
import shutil
from typing import TYPE_CHECKING, Dict, Tuple




if TYPE_CHECKING:
    from model.section import Section
    from model.subject import Subject
    from model.session import Session
    from model.quiz import Quiz


@dataclass
class Student:
    id: str
    image: str
    name: str
    birthday: datetime
    gender: str
    section: 'Section'
    grades: Dict[Tuple['Subject', 'Session', 'Quiz'], str] = None

    @property
    def avg(self) -> float:
        if not self.grades:
            return 0
        return sum(map(float, self.grades.values())) / len(self.grades)

    def __hash__(self) -> int:
        return hash(self.id)
        
    def __str__(self) -> str:
        cols = 4

        # get terminal width
        width = shutil.get_terminal_size().columns
        width = width - cols * 2 # 3 * 2 spaces
        width = width - len(self.id) - 1 # 1 space
        # make sure the name is not too long and pad spaces if needed
        name = self.name[:width].ljust(width // cols)
        gender = self.gender[:width].center(width // (cols * 2))
        birthday = self.birthday.strftime('%d/%m/%Y')[:width].center(width // (cols * 2))
        section_name = self.section.name[:width].center(width // cols)

        grades  = ' '.join(map(str, self.grades.values())).center(width // cols)

        return f'{self.id} {name}  {gender}  {birthday}  {grades}  {section_name}'
    
    def __repr__(self) -> str:
        return str(self)