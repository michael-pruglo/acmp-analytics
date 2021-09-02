from enum import Enum
Lang = Enum("Lang", "all cpp python pascal java csharp basic go")

from typing import NamedTuple
class TaskInfo(NamedTuple):
    id: int
    lang: Lang