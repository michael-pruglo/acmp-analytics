import helpers as hlp
from globals import *
import pandas as pd, numpy as np
from math import isclose, sqrt


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

    def get_task_difficulty(self, task_info:TaskInfo, leaderboard:pd.DataFrame, verbose:bool=False) -> float:
        acc_sub_score = self._get_acc_sub_score(task_info.accepted_submissions)
        code_len_score = self._get_code_len_score(leaderboard["code_len"])

        total = self.combiner.combine_components([
            ( self.AS_C,    acc_sub_score ),
            ( self.LEN_C,   code_len_score ),
        ])

        if PRINT_DIFF or verbose==True:
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
