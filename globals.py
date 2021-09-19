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


# settings
PRINT_DIFF          = False
PRINT_LEADERBOARD   = False
PRINT_SME           = False