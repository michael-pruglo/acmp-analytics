import pandas as pd, numpy as np, statistics, matplotlib.pyplot as plt
from functools import partial
from math import isclose
import helpers as hlp
from globals import *


pd.options.display.float_format = "{:.2f}".format


class RatingSystem:
    def __init__(self):
        self.rankings = {}

    def rate(self, data_list):
        for task_info, leaderboard in data_list:
            self._rate_task(task_info, leaderboard)
        return self.rankings
    
    def eval_accuracy(self, data_list) -> float:
        return statistics.mean([self._eval_accuracy_task(task_info, leaderboard) for task_info, leaderboard in data_list])

    def _rate_task(self, task_info, leaderboard) -> None:
        pass

    def _eval_accuracy_task(self, task_info, leaderboard) -> float:
        pass


class TMX(RatingSystem):
    def __init__(self):
        RatingSystem.__init__(self)

    def _rate_task(self, task_info, leaderboard) -> None:
        lengths = leaderboard["code_len"]
        dif = _get_task_difficulty(task_info, lengths)
        scores = _get_scores(lengths)
        tmx_points = self._assign_points(dif, scores)
        
        #leaderboard["scores"] = scores
        #leaderboard["tmx_points"] = tmx_points
        #print(leaderboard)
        #plt.plot(scores, tmx_points, 'yo')
        #hlp.plot(scores, partial(self._distrib_f, dif))
        #plt.show()
            
        for name, pts in zip(leaderboard["name"], tmx_points):
            self.rankings.setdefault(name, 0.0)
            self.rankings[name] += pts
    
    def _eval_accuracy_task(self, _, leaderboard) -> float:
        lengths = leaderboard["code_len"]
        scores = _get_scores(lengths)
        overall_ratings = [self.rankings.get(name, 0.0) for name in leaderboard["name"]]
        interp_ratings = [hlp.interpolate_inverse(x, min(overall_ratings), max(overall_ratings), *SCORE_RANGE) for x in overall_ratings]
        norm = np.linalg.norm(np.array(scores)-np.array(interp_ratings))
        
        leaderboard["scores"] = scores
        leaderboard["ov_rating"] = overall_ratings
        leaderboard["exp_scores"] = interp_ratings
        #print(leaderboard)
        #print("norm: ", norm)
        return norm

    def _assign_points(self, difficulty, scores):
        pass


#task diff determines points for the 1st place
class TMX_max(TMX):
    def __init__(self):
        TMX.__init__(self)
        self.distrib_f_k = 1/3

    def _assign_points(self, max_pts, scores):
        return [self._distrib_f(max_pts, x) for x in scores]

    def _distrib_f(self, max_score, x):
        return max_score*(1 - self.distrib_f_k*np.log(x))

#task diff determines prize pool for all 20
class TMX_const(TMX_max):
    def __init__(self):
        TMX_max.__init__(self)

    def _assign_points(self, prize_pool, scores):
        first = super()._assign_points(prize_pool, scores)
        return [x*prize_pool/sum(first) for x in first]

#task diff considers player ratings
class TMX_reflexive(TMX):
    def __init__(self):
        TMX.__init__(self)


class ELO(RatingSystem):
    pass



def _get_task_difficulty(info, code_len_column):
    def get_acc_sub_coef(acc):
        A = 9.5
        B = 0.043429
        return A+B*np.log(acc)
    def get_code_len_coef(lengths):
        m = lengths.median()
        A = 0.000391
        B = 0.000014
        coef = 10 - A*m - B*m*m
        return max(coef, 1)

    acc_sub_coef = get_acc_sub_coef(info.accepted_submissions)
    code_len_coef = get_code_len_coef(code_len_column)
    #print(f"Task #{info.id} difficulty:")
    #print(f"  acc_sub         = {info.accepted_submissions:7} [x{acc_sub_coef:.2f}]")
    #print(f"  code_len median = {code_len_column.median():7.2f} [x{code_len_coef:.2f}]")
    #print(f"  total = {(acc_sub_coef*code_len_coef):.2f}")
    return acc_sub_coef * code_len_coef

def _get_scores(code_len_column):
    code_len_column = _deal_with_ties(list(code_len_column))
    interp_scores = [hlp.interpolate(x, min(code_len_column), max(code_len_column), *SCORE_RANGE) for x in code_len_column]
    return interp_scores

def _deal_with_ties(scores):
    i = 0
    sum_before = sum(scores)
    while i < len(scores)-1:
        j = i
        while j+1 < len(scores) and scores[j] == scores[j+1]:
            j += 1
        if j > i:
            PERCENT_SPREAD = 20
            for k, delta in zip(range(i, j+1), np.linspace(-PERCENT_SPREAD/200, PERCENT_SPREAD/200, num=j-i+1)):
                scores[k] += delta
        i = j+1
    
    assert(isclose(sum(scores), sum_before))
    return scores   
