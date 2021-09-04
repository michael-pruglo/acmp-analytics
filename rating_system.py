import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

diff_range = (1.00, 10.00)
score_range = (1.00, 10.00)

class RatingSystem:
    def __init__(self):
        self.ratings = pd.DataFrame(columns=["name", "rating", "rated tasks"])
        
    def rate(self, data_map):
        acc_subm = [td.accepted_submissions for td in data_map]
        min_subm = min(acc_subm)
        max_subm = max(acc_subm)
        for info, leaderboard in data_map.items():
            difficulty = _interpolate(info.accepted_submissions, min_subm, max_subm, *diff_range)
            print(info.accepted_submissions, min_subm, max_subm, difficulty)
            self._rate_task(difficulty, leaderboard)

    def _rate_task(self, difficulty, leaderboard):
        min_score = min(leaderboard["code_len"])
        max_score = max(leaderboard["code_len"])
        interp_scores = [_interpolate(x, min_score, max_score, *score_range) for x in leaderboard["code_len"]]
        #deal with ties
        rated_scores = [self._distrib_f(difficulty, x) for x in interp_scores]
        print(leaderboard)
        print(interp_scores)
        print(rated_scores)
        _visualize(interp_scores, difficulty, self._distrib_f)

    def _distrib_f(self, max_score, x):
        return max_score - max_score/3*math.log(x)

    def get_ratings(self):
        return self.ratings

    def _update_ratings(self, task_info, table_with_points):
        for i, row in table_with_points.iterrows():
            name = row["name"]
            pass #if self.ratings.contains name:

def _interpolate(x, min_orig, max_orig, min_target, max_target):
    if min_orig==max_orig:
        return (max_target+min_target)/2
    return (x-min_orig)/(max_orig-min_orig)*(max_target-min_target) + min_target

def _visualize(x_list, diff, f):
    x_axis = np.linspace(*score_range)
    plt.plot(x_list, [f(diff, x) for x in x_list], 'ro', x_axis, [f(diff, x) for x in x_axis])
    plt.show()

if __name__ == "__main__":
    assert(_interpolate(71,0,100,0,10)==7.1)
    assert(_interpolate(80,80,80,5,7)==6)