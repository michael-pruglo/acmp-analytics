import helpers as hlp
from rating_system import Rating, RatingSystemLogic, DifficultyManager
from globals import *
import pandas as pd, numpy as np
from typing import List


#task diff determines points for the 1st place
class TMX_max(RatingSystemLogic):
    def __init__(self, difficulty_mgr:DifficultyManager=DifficultyManager(), distrib_f_k=0.29) -> None:
        super().__init__()
        self.diff_mgr = difficulty_mgr
        self.distrib_f_k = distrib_f_k

    def _calc_updated_ranks_impl(self, curr_ranks: List[Rating], task_info: TaskInfo, leaderboard:pd.DataFrame) -> List[Rating]:
        deltas = self._calc_rank_deltas()
        return [ curr_r + dr for curr_r, dr in zip(curr_ranks, deltas)]

    def _calc_rank_deltas(self, task_info: TaskInfo, leaderboard:pd.DataFrame) -> List[float]:
        task_diff = self.diff_mgr.get_task_difficulty(task_info, leaderboard)
        scores = leaderboard["scores"]
        deltas = self._distribute_points(task_diff, scores)
        deltas = self._apply_breaking_100_bonus(deltas, leaderboard["code_len"])
        return deltas
        
    def _distribute_points(self, task_diff:float, scores:List[float]) -> List[float]:
        return [self._distrib_f(task_diff, x) for x in scores]

    def _distrib_f(self, max_score:float, x:float) -> float:
        return max_score*(1 - self.distrib_f_k*np.log(x))

    def _apply_breaking_100_bonus(self, deltas:List[float], codelengths:List[int]):
        if codelengths.median() >= 100 and codelengths[0] < 100:
            if PRINT_LEADERBOARD:
                print("Breaking 100 applies!\nprev:  ", hlp.pretty(deltas,2))
            for i, len in enumerate(codelengths):
                if len < 100:
                    deltas[i] *= 1.1
            if PRINT_LEADERBOARD:
                print("after :", hlp.pretty(deltas,2))
        return deltas


#task diff determines prize pool for all 20
class TMX_const(TMX_max):
    def _distribute_points(self, task_diff:float, scores:List[float]) -> List[float]:
        first = super()._distribute_points(task_diff, scores)
        interp_k = task_diff / sum(first)
        return [float(x) * interp_k for x in first]
