from dataclasses import dataclass, field


@dataclass
class Item:
    name: str
    count: int
    tags: list[type] = field(default_factory=list)
