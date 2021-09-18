import numpy as np, pandas as pd, statistics, matplotlib.pyplot as plt, trueskill
from functools import partial
from collections import defaultdict
from math import isclose, sqrt
from globals import *
from typing import DefaultDict, List
import helpers as hlp

class Rating:
    def __init__(self, val=None) -> None:
        self.val = val if val else self.__class__.default_val()
    def default_val():
        return 0.0
    def __float__(self):
        return self.val
    def __add__(self, f:float):
        return float(self) + f
    def __sub__(self, f:float):
        return float(self) - f
    def __gt__(self, f:float):
        return float(self) > f
    def __lt__(self, f:float):
        return float(self) < f
    def __eq__(self, f:float):
        return float(self) == f
    def __str__(self) -> str:
        return f"{self.val:.2f}"
    def __repr__(self) -> str:
        return f"{self.val:.2f}"

class EloRating(Rating):
    def default_val():
        return 1500.0
class TrueSkillRating(Rating):
    def default_val():
        return trueskill.Rating()
    def __str__(self) -> str:
        return f"TrueSkill(μ={self.val.mu:>5.2f} σ={self.val.sigma:>5.2f} float:{float(self):>5.2f})"
    def __repr__(self) -> str:
        return f"TrueSkill(μ={self.val.mu:>5.2f} σ={self.val.sigma:>5.2f} float:{float(self):>5.2f})"
    def __float__(self):
        return trueskill.expose(self.val)
class TrueSkillRatingMean(TrueSkillRating):
    def __float__(self):
        return self.val.mu

class Combiner:
    def combine_components(self, comp_list):
        pass
class CombinerWeightedSum(Combiner):
    def combine_components(self, comp_list):
        total = max_possible = 0.0
        for coef, val in comp_list:
            assert(hlp.is_in_range(val, *DifficultyManager._COMPONENT_RANGE))
            total += coef * val
            max_possible += coef * DifficultyManager._COMPONENT_RANGE[1]
        return hlp.interpolate(total, 0.0, max_possible, *DifficultyManager._DIFF_RANGE)
#deprecated: less logical and tested to be less effective than weighted sum
class CombinerMult(Combiner):
    def combine_components(self, comp_list):
        total = max_possible = 1.0
        for coef, val in comp_list:
            assert(hlp.is_in_range(val, *DifficultyManager._COMPONENT_RANGE))
            if coef>0 and val>0:
                total *= coef * val
                max_possible *= coef * DifficultyManager._COMPONENT_RANGE[1]
        return hlp.interpolate(total, 1.0, max_possible, *DifficultyManager._DIFF_RANGE)

class DifficultyManager:
    _COMPONENT_RANGE = (0, 10)
    _DIFF_RANGE = (0, 100)

    def __init__(self, AS_C=0.5, AS_A=9.333, AS_B=0.056, LEN_C=0.7, LEN_A=.2e-6, PS_A=0.6, combiner:Combiner=CombinerWeightedSum()):
        self.AS_C = AS_C
        self.AS_A = AS_A
        self.AS_B = AS_B
        self.LEN_C = LEN_C
        self.LEN_A = LEN_A
        self.PS_A = PS_A
        self.combiner = combiner

    def get_task_difficulty(self, task_info:TaskInfo, leaderboard:pd.DataFrame):
        acc_sub_score = self._get_acc_sub_score(task_info.accepted_submissions)
        code_len_score = self._get_code_len_score(leaderboard["code_len"])

        total = self.combiner.combine_components([
            ( self.AS_C,    acc_sub_score ),
            ( self.LEN_C,   code_len_score ),
        ])

        if PRINT_DIFF:
            _a = task_info.accepted_submissions
            _b = leaderboard["code_len"].median()
            print(f"Task #{task_info.id} difficulty:")
            print(f"  ac_sub:     {acc_sub_score:.2f} \t {_a}")
            print(f"  code_len:   {code_len_score:.2f} \t {_b:.2f}")
            print(f"total: {total:.2f}")

        return total

    def _get_acc_sub_score(self, acc):
        return min([self.AS_A + self.AS_B * np.log(acc), 0.284*sqrt(acc), acc**2/15000])

    def _get_code_len_score(self, lengths):
        m = lengths.median()
        coef = 10 - self.LEN_A * m * m * m
        return max(coef, 0)

class ScoringManager:
    def __init__(self, percent_spread=15, deal_with_ties=True):
        self.percent_spread = percent_spread
        self.deal_with_ties = deal_with_ties

    def get_scores(self, leaderboard):
        code_len_column = list(leaderboard["code_len"])
        if self.deal_with_ties:
            code_len_column = self._deal_with_ties(code_len_column)
        interp_scores = [hlp.interpolate(x, min(code_len_column), max(code_len_column), *SCORE_RANGE) for x in code_len_column]
        return interp_scores
    
    def _deal_with_ties(self, scores):
        i = 0
        sum_before = sum(scores)
        while i < len(scores)-1:
            j = i
            while j+1 < len(scores) and scores[j] == scores[j+1]:
                j += 1
            if j > i:
                for k, delta in zip(range(i, j+1), np.linspace(-self.percent_spread/200, self.percent_spread/200, num=j-i+1)):
                    scores[k] += delta
            i = j+1
        
        assert(isclose(sum(scores), sum_before))
        return scores 


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
            print(f"Match (rank={rat_a:>8.2f}) {outcome:.1f} vs (rank={rat_b:>8.2f}): exp={exp:.2f} k={k:.2f} dr={dr:>10.3f}")
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




class RatingSystemLogic:
    RatingT = Rating

    def calc_updated_ranks(self, curr_ranks:List[Rating], task_info:TaskInfo, leaderboard:pd.DataFrame) -> List[Rating]:
        assert(len(curr_ranks) == len(leaderboard.index))
        assert("scores" in leaderboard.columns)
        return self._calc_updated_ranks_impl(curr_ranks, task_info, leaderboard)

    def _calc_updated_ranks_impl(self, curr_ranks:List[Rating], task_info:TaskInfo, leaderboard:pd.DataFrame) -> List[Rating]:
        pass

#task diff determines points for the 1st place
class TMX_max(RatingSystemLogic):
    def __init__(self, difficulty_mgr:DifficultyManager=DifficultyManager(), distrib_f_k=0.29) -> None:
        super().__init__()
        self.diff_mgr = difficulty_mgr
        self.distrib_f_k = distrib_f_k

    def _calc_updated_ranks_impl(self, curr_ranks: List[Rating], task_info: TaskInfo, leaderboard:pd.DataFrame) -> List[Rating]:
        max_pts = self.diff_mgr.get_task_difficulty(task_info, leaderboard)
        return [ curr_r + self._distrib_f(max_pts, x) for curr_r, x in zip(curr_ranks, leaderboard["scores"]) ]

    def _distrib_f(self, max_score, x):
        return max_score*(1 - self.distrib_f_k*np.log(x))
#task diff determines prize pool for all 20
class TMX_const(TMX_max):
    def _calc_updated_ranks_impl(self, curr_ranks: List[Rating], task_info: TaskInfo, leaderboard: pd.DataFrame) -> List[Rating]:
        prize_pool = self.diff_mgr.get_task_difficulty(task_info, leaderboard)
        first = super()._calc_updated_ranks_impl(curr_ranks, task_info, leaderboard)
        return [ curr_r + x*prize_pool/sum(first) for curr_r, x in zip(curr_ranks, first)]


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


class TrueSkill(RatingSystemLogic):
    RatingT = TrueSkillRating

    def _calc_updated_ranks_impl(self, curr_ranks:List[Rating], task_info:TaskInfo, leaderboard:pd.DataFrame) -> List[Rating]:
        scores = leaderboard["scores"]
        leaderboard_is_sorted = all(scores[i] <= scores[i+1] for i in range(len(scores)-1))
        assert(leaderboard_is_sorted)

        wrapped_rankings = [[curr_ranks[0].val] for rank in curr_ranks]
        upd_rankings = trueskill.rate(wrapped_rankings)
        unwrapped_results = [self.RatingT(tpl[0]) for tpl in upd_rankings]

        return unwrapped_results





class RatingSystem:
    def __init__(self, logic:RatingSystemLogic, scoring_mgr:ScoringManager=ScoringManager(), description="n/a"):
        self.logic = logic
        self.scoring_mgr = scoring_mgr
        self.rankings : DefaultDict[str, Rating] = defaultdict(logic.RatingT)
        self.description = description

    def rate(self, data_list) -> DefaultDict[str, Rating]:
        for task_info, leaderboard in data_list:
            leaderboard["scores"] = self.scoring_mgr.get_scores(leaderboard)
            curr_ranks = [self.rankings[name] for name in leaderboard["name"]]
            new_ranks = self.logic.calc_updated_ranks(curr_ranks, task_info, leaderboard)
            for name, new_r in zip(leaderboard["name"], new_ranks):
                self.rankings[name] = new_r

            if PRINT_LEADERBOARD:
                leaderboard["curr_ranks"] = curr_ranks
                leaderboard["new_ranks"] = new_ranks
                print(leaderboard)
 
        return self.rankings

    def eval_accuracy(self, data_list) -> float:
        return statistics.mean([self._eval_accuracy_task(task_info, leaderboard) for task_info, leaderboard in data_list])

    def reset(self) -> None:
        self.rankings = defaultdict(self.logic.RatingT)

    def _eval_accuracy_task(self, _, leaderboard) -> float:
        curr_ranks = [self.rankings[name] for name in leaderboard["name"]]
        scores = self.scoring_mgr.get_scores(leaderboard)
        exp_scores = [
            hlp.interpolate_inverse(float(x), float(min(curr_ranks)), float(max(curr_ranks)), *SCORE_RANGE) 
            for x in curr_ranks
        ]
        norm = np.linalg.norm(np.array(scores)-np.array(exp_scores))

        if PRINT_LEADERBOARD:
            leaderboard["curr_ranks"] = leaderboard["new_ranks"] = curr_ranks
            leaderboard["scores"] = scores
            leaderboard["exp_scores"] = exp_scores
            print(leaderboard)

        return norm

