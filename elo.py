import helpers as hlp
from rating_system import Rating, RatingSystemLogic, DifficultyManager
from globals import *
import statistics, pandas as pd
from typing import List


class EloRating(Rating):
    def default_val():
        return 1500.0


class ELO:
    def __init__(self, sigma=200, k=32):
        self.sigma = sigma
        self.k = k
        
    def default_rating(self):
        return 1500.0

    def get_outcome(self, score_a, score_b):
        if score_a < score_b: return 1
        if score_a > score_b: return 0
        return 0.5

    def get_dr(self, rat_a:float, rat_b:float, task_diff:float, outcome:float=1):
        exp = self._get_estimate(rat_a, rat_b)
        k = self.k * hlp.interpolate(task_diff, *DifficultyManager._DIFF_RANGE, 0.0, 1.0)
        dr = k  * (outcome - exp)
        if PRINT_SME:
            print(f"Match (rank={float(rat_a):>8.2f}) {outcome:.1f} vs (rank={float(rat_b):>8.2f}): exp={exp:.2f} k={k:.2f} dr={dr:>10.3f}")
        return dr
    
    def _get_estimate(self, rat_a:float, rat_b:float):
        return 1 / ( 1 + 10**(-(float(rat_a)-float(rat_b))/self.sigma) )

#Margin Of Victory:
# http://www2.stat-athens.aueb.gr/~jbn/conferences/MathSport_presentations/plenary%20talks/P3%20-%20Kovalchik%20-%20Extensions%20of%20the%20Elo%20Rating%20System%20for%20Margin%20of%20Victory.pdf
# https://rdrr.io/github/GIGTennis/elomov/src/R/linear.R
class MOV(ELO):
    def __init__(self, stdev=7):
        super().__init__(sigma=25*stdev, k=stdev)

    def get_outcome(self, score_a, score_b):
        return score_b - score_a

    def _get_estimate(self, rat_a:float, rat_b:float):
        return (float(rat_a)-float(rat_b)) / self.sigma



#Simple Multiplayer ELO: http://www.tckerrigan.com/Misc/Multiplayer_Elo/
class SME(RatingSystemLogic):
    RatingT = EloRating

    def __init__(self, elo_mgr:ELO=ELO(), difficulty_mgr:DifficultyManager=DifficultyManager()):
        super().__init__()
        self.elo_mgr = elo_mgr
        self.diff_mgr = difficulty_mgr

    def _calc_updated_ranks_impl(self, curr_ranks: List[Rating], task_info: TaskInfo, leaderboard: pd.DataFrame) -> List[Rating]:
        scores = leaderboard["scores"]
        task_diff = self.diff_mgr.get_task_difficulty(task_info, leaderboard)
        deltas = self._get_rating_deltas(task_diff, scores, curr_ranks)
        return [EloRating(curr + dr) for curr, dr in zip(curr_ranks, deltas)]

    def _get_rating_deltas(self, task_diff:float, scores:List[float], curr_ranks:List[Rating]) -> List[float]:
        deltas = [0.0 for _ in scores]
        for i in range(len(scores)-1):
            outcome = self.elo_mgr.get_outcome(scores[i], scores[i+1])
            dr = self.elo_mgr.get_dr(curr_ranks[i], curr_ranks[i+1], task_diff, outcome)
            deltas[i]   += dr
            deltas[i+1] -= dr
        return deltas

#SME Everyone vs Everyone: matches all possible pairs instead of directly up and down
class SME_EvE(SME):
    def __init__(self, elo_mgr: ELO):
        elo_mgr.k /= 19
        super().__init__(elo_mgr)

    def _get_rating_deltas(self, task_diff: float, scores: List[float], curr_ranks: List[Rating]) -> List[float]:
        deltas = [0.0 for _ in scores]
        for i in range(len(scores)-1):
            for j in range(i+1, len(scores)):
                outcome = self.elo_mgr.get_outcome(scores[i], scores[j])
                dr = self.elo_mgr.get_dr(curr_ranks[i], curr_ranks[j], task_diff, outcome)
                deltas[i] += dr
                deltas[j] -= dr
        return deltas

class SME_avgn(SME):
    def _get_rating_deltas(self, task_diff: float, scores: List[float], curr_ranks: List[Rating]) -> List[float]:
        deltas = [0.0 for _ in scores]
        for i in range(len(scores)):
            if i > 0:
                outcome = self.elo_mgr.get_outcome(scores[i], statistics.mean(scores[:i]))
                deltas[i] += self.elo_mgr.get_dr(curr_ranks[i], statistics.mean(curr_ranks[:i]), task_diff, outcome)
            if i < len(scores)-1:
                outcome = self.elo_mgr.get_outcome(scores[i], statistics.mean(scores[i+1:]))
                deltas[i] += self.elo_mgr.get_dr(curr_ranks[i], statistics.mean(curr_ranks[i+1:]), task_diff, outcome)
        return deltas

class SME_avg2(SME):
    def _get_rating_deltas(self, task_diff: float, scores: List[float], curr_ranks: List[Rating]) -> List[float]:
        deltas = [0.0 for _ in scores]
        for i in range(len(scores)):
            outcome = hlp.interpolate_inverse(scores[i], *SCORE_RANGE, 0.0, 1.0)
            deltas[i] = self.elo_mgr.get_dr(curr_ranks[i], statistics.mean(curr_ranks), task_diff, outcome)
        return deltas

