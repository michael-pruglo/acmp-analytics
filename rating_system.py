from globals import *
from rating_system_tools import *
import pandas as pd, statistics, random
from typing import List, DefaultDict
from collections import defaultdict

class Rating:
    def __init__(self, val=None) -> None:
        self.val = val if val else self.__class__.default_val()
    def default_val():
        return 0.0
    def __float__(self):
        return self.val
    def __add__(self, f:float):
        return float(self) + f
    def __sub__(self, other):
        return float(self) - float(other)
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

class RatingSystemLogic:
    RatingT = Rating

    def calc_updated_ranks(self, curr_ranks:List[Rating], task_info:TaskInfo, leaderboard:pd.DataFrame) -> List[Rating]:
        assert(len(curr_ranks) == len(leaderboard.index))
        assert("scores" in leaderboard.columns)
        return self._calc_updated_ranks_impl(curr_ranks, task_info, leaderboard)

    def _calc_updated_ranks_impl(self, curr_ranks:List[Rating], task_info:TaskInfo, leaderboard:pd.DataFrame) -> List[Rating]:
        pass


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
                leaderboard["dranks"] = [float(new)-float(old) for new,old in zip(new_ranks,curr_ranks)]
                print(leaderboard)
 
        return self.rankings

    def rate_multiple_runs(self, data_list, runs:int) -> DefaultDict[str, Rating]:
        result_dict = defaultdict(float)
        for i in range(runs):
            if i%10==0: print(f"rate_multiple_runs {self.description}: run {i:>4}/{runs:>4}")
            self.reset()
            random.shuffle(data_list)
            for name, rat in self.rate(data_list).items():
                result_dict[name] += float(rat) / runs
        return result_dict

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

