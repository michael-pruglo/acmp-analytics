import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import helpers as hlp
from functools import partial
from math import isclose
from globals import RatingInfo


class RatingSystem:
    def __init__(self):
        self.rankings = {}

    def rate(self, data_list):
        for task_info, leaderboard in data_list:
            self._rate_task(task_info, leaderboard)
        return self.rankings

    def _rate_task(self, task_info, leaderboard) -> None:
        pass


#task diff determines points for the 1st place
class TMX_max(RatingSystem):
    def __init__(self):
        RatingSystem.__init__(self)
        self.distrib_f_k = 1/3

    def _rate_task(self, task_info, leaderboard):
        lengths = leaderboard["code_len"]
        dif = _get_task_difficulty(task_info, lengths)
        scores = _get_scores(lengths)
        tmx_points = self._assign_points(dif, scores)
        for name, pts in zip(leaderboard["name"], tmx_points):
            self.rankings.setdefault(name, 0.0)
            self.rankings[name] += pts

    def _assign_points(self, max_pts, scores):
        return [self._distrib_f(max_pts, x) for x in scores]

    def _distrib_f(self, max_score, x):
        return max_score*(1 - self.distrib_f_k*np.log(x))

#task diff determines prize pool for all 20
class TMX_const(RatingSystem):
    pass

#task diff considers player ratings
class TMX_reflexive(RatingSystem):
    pass

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
    print(f"Task #{info.id} difficulty:")
    print(f"  acc_sub         = {info.accepted_submissions:7} [x{acc_sub_coef:.2f}]")
    print(f"  code_len median = {code_len_column.median():7.2f} [x{code_len_coef:.2f}]")
    print(f"  total = {(acc_sub_coef*code_len_coef):.2f}")
    return acc_sub_coef * code_len_coef

def _get_scores(code_len_column):
    code_len_column = _deal_with_ties(list(code_len_column))
    SCORE_RANGE = (1.00, 10.00)
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
            PERCENT_SPREAD = 30
            for k, delta in zip(range(i, j+1), np.linspace(-PERCENT_SPREAD/200, PERCENT_SPREAD/200, num=j-i+1)):
                scores[k] += delta
        i = j+1
    
    assert(isclose(sum(scores), sum_before))
    return scores



"""
            pd.options.display.float_format = "{:.2f}".format
            print("interp_len:", hlp.pretty(scores))
            leaderboard["tmx_rating"] = [self.rankings[name].tmx_points for name in leaderboard["name"]]
            print(leaderboard)
            hlp.plot(scores, partial(self._distrib_f, dif))
            #plt.show()
    
    def show_rankings(self):
        sorted_ranking = sorted(self.rankings.items(), key=lambda x: x[1].tmx_points, reverse=True)
        row_format = "{0:>4}  {1:<40} {2:>10} {3:>11} {4:>9}"

        print("Rankings: ")
        print(row_format.format("rank", "name", "tmx_points", "rated_tasks", "avg_rank"))
        for i, (name, rating_info) in enumerate(sorted_ranking):
            print(row_format.format(
                i+1,
                name, 
                f"{rating_info.tmx_points:.3f}", 
                len(rating_info.rated_tasks), 
                f"{rating_info.avg_rank:.3f}"
            ))









    def _update_rankings_tmx(self, task_id, data):
        for i, (name, tmx_points) in enumerate(data):
            rating_info = RatingInfo() if name not in self.rankings else self.rankings[name]
            rating_info.tmx_points += tmx_points
            n = len(rating_info.rated_tasks)
            rating_info.avg_rank = (rating_info.avg_rank*n + i+1)/(n+1)
            rating_info.rated_tasks.append(task_id)
            self.rankings[name] = rating_info

"""      
