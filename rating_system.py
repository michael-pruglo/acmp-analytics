import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import helpers as hlp
from functools import partial

ACC_SUB_COEF_RANGE = (3.00, 10.00)
SCORE_RANGE = (1.00, 10.00)

class RatingSystem:
    def __init__(self):
        pass

    def rate(self, data_map):
        for info, leaderboard in data_map.items():
            dif = self._get_task_difficulty(info, leaderboard["code_len"])
            scores = self._get_scores(leaderboard["code_len"])
            leaderboard["tmx_points"] = self._rate_task(dif, scores)
            
            pd.options.display.float_format = "{:.2f}".format
            print("interp_len:", hlp.pretty(scores))
            print(leaderboard)
            hlp.plot(scores, partial(self._distrib_f, dif))
            plt.show()


    def _get_task_difficulty(self, info, code_len_column):
        def get_acc_sub_coef(acc):
            A = 9.5
            B = 0.043429
            return A+B*np.log(acc)
        def get_code_len_coef(lengths):
            m = lengths.median()
            A = 0.000391
            B = 0.000014
            return 10 - A*m - B*m*m

        acc_sub_coef = get_acc_sub_coef(info.accepted_submissions)
        code_len_coef = get_code_len_coef(code_len_column)
        print( "Difficulty:")
        print(f"  acc_sub         = {info.accepted_submissions:7} [x{acc_sub_coef:.2f}]")
        print(f"  code_len median = {code_len_column.median():7.2f} [x{code_len_coef:.2f}]")
        print(f"  total = {(acc_sub_coef*code_len_coef):.2f}")
        return acc_sub_coef * code_len_coef

    def _get_scores(self, code_len_column):
        interp_scores = [hlp.interpolate(x, min(code_len_column), max(code_len_column), *SCORE_RANGE) for x in code_len_column]
        #deal with ties
        return interp_scores

    def _rate_task(self, max_pts, scores):
        tmx_points = [self._distrib_f(max_pts, x) for x in scores]
        return tmx_points

    def _distrib_f(self, max_score, x):
        K = 1/3
        return max_score*(1 - K*np.log(x))
