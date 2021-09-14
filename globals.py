from enum import Enum
Lang = Enum("Lang", "all cpp python pascal java csharp basic go")

SCORE_RANGE = (1.00, 20.00)

from typing import NamedTuple
class TaskInfo(NamedTuple):
    id: int
    lang: Lang
    accepted_submissions: int = 0
    
    def __repr__(self):
        return f"{self.lang.name}{self.id}"


from dataclasses import dataclass, field
@dataclass
class RatingInfo:
    tmx_points: float = 0.0
    elo: float = 0.0
    avg_rank: float = 999.0
    rated_tasks: list = field(default_factory=list)

# settings
PRINT_DIFF          = False
PRINT_LEADERBOARD   = False
PRINT_SME           = False