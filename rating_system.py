import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import helpers as hlp
from functools import partial

DIFF_RANGE = (3.00, 10.00)
SCORE_RANGE = (1.00, 10.00)
LOG_CURVE_K = 1/3

class RatingSystem:
    def __init__(self):
        pass


    def rate(self, data_map):
        acc_subm = [td.accepted_submissions for td in data_map]
        for info, leaderboard in data_map.items():
            difficulty = hlp.interpolate(info.accepted_submissions, min(acc_subm), max(acc_subm), *DIFF_RANGE)
            leaderboard["tmx_points"] = self._rate_task(difficulty, leaderboard["code_len"])
            
            pd.options.display.float_format = "{:.2f}".format
            print("subm: ", info.accepted_submissions, '[', min(acc_subm), max(acc_subm), ']=', difficulty)
            print(leaderboard)
            plt.show()


    def _rate_task(self, difficulty, scores):
        interp_scores = [hlp.interpolate(x, min(scores), max(scores), *SCORE_RANGE) for x in scores]
        #deal with ties
        tmx_points = [self._distrib_f(difficulty, x) for x in interp_scores]
        
        print("interp_len:", hlp.pretty(interp_scores))
        hlp.plot(interp_scores, partial(self._distrib_f, difficulty))
        
        return tmx_points


    def _distrib_f(self, max_score, x):
        return max_score*(1 - LOG_CURVE_K*np.log(x))
