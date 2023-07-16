from dataclasses import dataclass


@dataclass
class Education:
    id: str
    name: str

    def __hash__(self) -> int:
        return hash(self.id)