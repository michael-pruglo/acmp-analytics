from rating_system import RatingSystemLogic, Rating
from globals import *
import trueskill, pandas as pd
from typing import List

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


#broken and not very appropriate: no margin of victory
class TrueSkill(RatingSystemLogic):
    RatingT = TrueSkillRating

    def _calc_updated_ranks_impl(self, curr_ranks:List[Rating], task_info:TaskInfo, leaderboard:pd.DataFrame) -> List[Rating]:
        scores = leaderboard["scores"]
        leaderboard_is_sorted = all(scores[i] <= scores[i+1] for i in range(len(scores)-1))
        assert(leaderboard_is_sorted)

        wrapped_rankings = [[rank.val] for rank in curr_ranks]
        upd_rankings = trueskill.rate(wrapped_rankings)
        unwrapped_results = [self.RatingT(tpl[0]) for tpl in upd_rankings]

        return unwrapped_results

