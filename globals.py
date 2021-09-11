from enum import Enum
Lang = Enum("Lang", "all cpp python pascal java csharp basic go")

from typing import NamedTuple
class TaskInfo(NamedTuple):
    id: int
    lang: Lang
    accepted_submissions: int = 0
    
    def __hash__(self):
        return hash((self.id, self.lang))

    def __eq__(self, other):
        return (self.id, self.lang) == (other.id, other.lang)

    def __ne__(self, other):
        return not(self == other)


from dataclasses import dataclass, field
@dataclass
class RatingInfo:
    tmx_points: float = 0.0
    elo: float = 0.0
    avg_rank: float = 999.0
    rated_tasks: list = field(default_factory=list)

