import numpy as np, statistics
from collections import defaultdict
from math import isclose
from globals import *
import helpers as hlp

class DifficultyManager:
    _COMPONENT_RANGE = (0, 10)
    _DIFF_RANGE = (0, 100)

    def __init__(self, AS_C=1, AS_A=9.333, AS_B=0.056, LEN_C=1, LEN_A=0.000391, LEN_B=0.000014, PS_C=0):
        self.AS_C = AS_C
        self.AS_A = AS_A
        self.AS_B = AS_B
        self.LEN_C = LEN_C
        self.LEN_A = LEN_A
        self.LEN_B = LEN_B
        self.PS_C = PS_C

    def get_task_difficulty(self, task_info:TaskInfo, leaderboard, ranking_range):
        acc_sub_score = self._get_acc_sub_score(task_info.accepted_submissions)
        code_len_score = self._get_code_len_score(leaderboard["code_len"])
        player_strength_score = self._get_player_strength_score(leaderboard["rankings"], ranking_range) if self.PS_C else 0.0

        total = self._combine_components([
            ( self.AS_C,    acc_sub_score ),
            ( self.LEN_C,   code_len_score ),
            ( self.PS_C,    player_strength_score ),
        ])

        return total
    
    def _combine_components(self, comp_list):
        total = max_possible = 0.0
        for coef, val in comp_list:
            assert(hlp.is_in_range(val, *DifficultyManager._COMPONENT_RANGE))
            total += coef * val
            max_possible += coef * DifficultyManager._COMPONENT_RANGE[1]
        return hlp.interpolate(total, 0.0, max_possible, *DifficultyManager._DIFF_RANGE)

    def _get_acc_sub_score(self, acc):
        return self.AS_A + self.AS_B * np.log(acc)

    def _get_code_len_score(self, lengths):
        m = lengths.median()
        coef = 10 - self.LEN_A * m - self.LEN_B * m * m
        return max(coef, 1)

    def _get_player_strength_score(self, rankings, ranking_range):
        mean = statistics.mean(rankings)
        return hlp.interpolate(mean, *ranking_range, *DifficultyManager._COMPONENT_RANGE)


class ScoringManager:
    def __init__(self, percent_spread=15):
        self.percent_spread = percent_spread

    def get_scores(self, leaderboard):
        code_len_column = self._deal_with_ties(list(leaderboard["code_len"]))
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


class DeltaManager:
    def default_rating(self):
        return 0.0

    def get_rating_deltas(self, task_diff, scores):
        pass

#task diff determines points for the 1st place
class TMX_max(DeltaManager):
    def __init__(self, distrib_f_k=1/3):
        DeltaManager.__init__(self)
        self.distrib_f_k = distrib_f_k

    def get_rating_deltas(self, max_pts, scores):
        return [self._distrib_f(max_pts, x) for x in scores]

    def _distrib_f(self, max_score, x):
        return max_score*(1 - self.distrib_f_k*np.log(x))

#task diff determines prize pool for all 20
class TMX_const(TMX_max):
    def __init__(self):
        TMX_max.__init__(self)

    def get_rating_deltas(self, prize_pool, scores):
        first = super().get_rating_deltas(prize_pool, scores)
        return [x*prize_pool/sum(first) for x in first]

class ELO(DeltaManager):
    pass




class RatingSystem:
    def __init__(self, diff_mgr:DifficultyManager, scoring_mgr:ScoringManager, delta_mgr:DeltaManager):
        self.diff_mgr = diff_mgr
        self.scoring_mgr = scoring_mgr
        self.delta_mgr = delta_mgr
        self.rankings = defaultdict(self.delta_mgr.default_rating)

    def rate(self, data_list):
        for task_info, leaderboard in data_list:
            leaderboard["rankings"] = [self.rankings[name] for name in leaderboard["name"]]
            overall_rankings_range = ( min(self.rankings.values()), max(self.rankings.values()) )
            scores = self.scoring_mgr.get_scores(leaderboard)
            
            task_diff = self.diff_mgr.get_task_difficulty(task_info, leaderboard, overall_rankings_range)
            dr = self.delta_mgr.get_rating_deltas(task_diff, scores)
            for name, delta in zip(leaderboard["name"], dr):
                self.rankings[name] += delta

        return self.rankings
    
    def eval_accuracy(self, data_list) -> float:
        return statistics.mean([self._eval_accuracy_task(task_info, leaderboard) for task_info, leaderboard in data_list])

    def _eval_accuracy_task(self, _, leaderboard) -> float:
        leaderboard["rankings"] = [self.rankings[name] for name in leaderboard["name"]]
        overall_rankings_range = ( min(self.rankings.values()), max(self.rankings.values()) )
        scores = self.scoring_mgr.get_scores(leaderboard)

        interp_ratings = [hlp.interpolate_inverse(x, *overall_rankings_range, *SCORE_RANGE) for x in leaderboard["rankings"]]
        norm = np.linalg.norm(np.array(scores)-np.array(interp_ratings))
        
        return norm
  
