import numpy as np, statistics, matplotlib.pyplot as plt
from functools import partial
from collections import defaultdict
from math import isclose, sqrt
from globals import *
import helpers as hlp

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

    def __init__(self, AS_C=0.5, AS_A=9.333, AS_B=0.056, LEN_C=0.7, LEN_A=.2e-6, PS_A=0.6, PS_C=0, combiner:Combiner=CombinerWeightedSum()):
        self.AS_C = AS_C
        self.AS_A = AS_A
        self.AS_B = AS_B
        self.LEN_C = LEN_C
        self.LEN_A = LEN_A
        self.PS_A = PS_A
        self.PS_C = PS_C
        self.combiner = combiner

    def get_task_difficulty(self, task_info:TaskInfo, leaderboard, ranking_mean):
        acc_sub_score = self._get_acc_sub_score(task_info.accepted_submissions)
        code_len_score = self._get_code_len_score(leaderboard["code_len"])
        player_strength_score = self._get_player_strength_score(leaderboard["rankings"], ranking_mean) if self.PS_C else 0.0

        total = self.combiner.combine_components([
            ( self.AS_C,    acc_sub_score ),
            ( self.LEN_C,   code_len_score ),
            ( self.PS_C,    player_strength_score ),
        ])

        if PRINT_DIFF:
            _a = task_info.accepted_submissions
            _b = leaderboard["code_len"].median()
            _c = leaderboard["rankings"]
            print(f"Task #{task_info.id} difficulty:")
            print(f"  ac_sub:     {acc_sub_score:.2f} \t {_a}")
            print(f"  code_len:   {code_len_score:.2f} \t {_b:.2f}")
            print(f"  player_str: {player_strength_score:.2f} \t {_c.mean():.2f}", hlp.pretty(_c, 1), f"overall_mean: {ranking_mean:.2f}")
            print(f"total: {total:.2f}")

        return total

    def _get_acc_sub_score(self, acc):
        return min([self.AS_A + self.AS_B * np.log(acc), 0.284*sqrt(acc), acc**2/15000])

    def _get_code_len_score(self, lengths):
        m = lengths.median()
        coef = 10 - self.LEN_A * m * m * m
        return max(coef, 0)

    #practically it flopped, so keeping PS_C=0 for now
    def _get_player_strength_score(self, rankings, overall_rankings_mean):
        dm = statistics.mean(rankings) - overall_rankings_mean
        return np.clip(5 + self.PS_A * dm, *DifficultyManager._COMPONENT_RANGE)


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

    def get_rating_deltas(self, task_diff, scores, rankings):
        pass

#task diff determines points for the 1st place
class TMX_max(DeltaManager):
    def __init__(self, distrib_f_k=0.29):
        DeltaManager.__init__(self)
        self.distrib_f_k = distrib_f_k

    def get_rating_deltas(self, max_pts, scores, _):
        return [self._distrib_f(max_pts, x) for x in scores]

    def _distrib_f(self, max_score, x):
        return max_score*(1 - self.distrib_f_k*np.log(x))

#task diff determines prize pool for all 20
class TMX_const(TMX_max):
    def __init__(self):
        TMX_max.__init__(self)

    def get_rating_deltas(self, prize_pool, scores, _):
        first = super().get_rating_deltas(prize_pool, scores, _)
        return [x*prize_pool/sum(first) for x in first]

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
        return 1 / ( 1 + 10**(-(rat_a-rat_b)/self.sigma) )

#Margin Of Victory:
# http://www2.stat-athens.aueb.gr/~jbn/conferences/MathSport_presentations/plenary%20talks/P3%20-%20Kovalchik%20-%20Extensions%20of%20the%20Elo%20Rating%20System%20for%20Margin%20of%20Victory.pdf
# https://rdrr.io/github/GIGTennis/elomov/src/R/linear.R
class MOV(ELO):
    def __init__(self, stdev=7):
        super().__init__(sigma=25*stdev, k=stdev)

    def get_outcome(self, score_a, score_b):
        return score_b - score_a

    def _get_estimate(self, rat_a:float, rat_b:float):
        return (rat_a-rat_b) / self.sigma


#Simple Multiplayer ELO: http://www.tckerrigan.com/Misc/Multiplayer_Elo/
class SME(DeltaManager):
    def __init__(self, elo_mgr:ELO=ELO()):
        super().__init__()
        self.elo_mgr = elo_mgr

    def default_rating(self):
        return self.elo_mgr.default_rating()

    def get_rating_deltas(self, task_diff, scores, rankings):
        deltas = [0.0 for _ in scores]
        for i in range(len(scores)-1):
            outcome = self.elo_mgr.get_outcome(scores[i], scores[i+1])
            dr = self.elo_mgr.get_dr(rankings[i], rankings[i+1], task_diff, outcome)
            deltas[i]   += dr
            deltas[i+1] -= dr
        return deltas

#SME Everyone vs Everyone: matches all possible pairs instead of directly up and down
class SME_EvE(SME):
    def __init__(self, elo_mgr: ELO):
        elo_mgr.k /= 19
        super().__init__(elo_mgr)

    def get_rating_deltas(self, task_diff, scores, rankings):
        deltas = [0.0 for _ in scores]
        for i in range(len(scores)-1):
            for j in range(i+1, len(scores)):
                outcome = self.elo_mgr.get_outcome(scores[i], scores[j])
                dr = self.elo_mgr.get_dr(rankings[i], rankings[j], task_diff, outcome)
                deltas[i] += dr
                deltas[j] -= dr
        return deltas

class SME_avgn(SME):
    def get_rating_deltas(self, task_diff, scores, rankings):
        deltas = [0.0 for _ in scores]
        for i in range(len(scores)):
            if i > 0:
                outcome = self.elo_mgr.get_outcome(scores[i], statistics.mean(scores[:i]))
                deltas[i] += self.elo_mgr.get_dr(rankings[i], statistics.mean(rankings[:i]), task_diff, outcome)
            if i < len(scores)-1:
                outcome = self.elo_mgr.get_outcome(scores[i], statistics.mean(scores[i+1:]))
                deltas[i] += self.elo_mgr.get_dr(rankings[i], statistics.mean(rankings[i+1:]), task_diff, outcome)
        return deltas

class SME_avg2(SME):
    def get_rating_deltas(self, task_diff, scores, rankings):
        deltas = [0.0 for _ in scores]
        for i in range(len(scores)):
            outcome = hlp.interpolate_inverse(scores[i], *SCORE_RANGE, 0.0, 1.0)
            deltas[i] = self.elo_mgr.get_dr(rankings[i], statistics.mean(rankings), task_diff, outcome)
        return deltas



class RatingSystem:
    def __init__(self, diff_mgr:DifficultyManager, scoring_mgr:ScoringManager, delta_mgr:DeltaManager, description="n/a"):
        self.diff_mgr = diff_mgr
        self.scoring_mgr = scoring_mgr
        self.delta_mgr = delta_mgr
        self.rankings = defaultdict(self.delta_mgr.default_rating)
        self.description = description

    def rate(self, data_list):
        for task_info, leaderboard in data_list:
            leaderboard["rankings"] = [self.rankings[name] for name in leaderboard["name"]]
            overall_rankings_mean = statistics.mean(self.rankings.values())
            scores = self.scoring_mgr.get_scores(leaderboard)
            
            task_diff = self.diff_mgr.get_task_difficulty(task_info, leaderboard, overall_rankings_mean)
            dr = self.delta_mgr.get_rating_deltas(task_diff, scores, leaderboard["rankings"])
            for name, delta in zip(leaderboard["name"], dr):
                self.rankings[name] += delta
            
            if PRINT_LEADERBOARD:
                leaderboard["scores"] = scores
                leaderboard["deltas"] = dr
                print(leaderboard)
                #hlp.plot(scores, partial(self.delta_mgr._distrib_f, task_diff))
                #plt.show()

        return self.rankings
    
    def eval_accuracy(self, data_list) -> float:
        return statistics.mean([self._eval_accuracy_task(task_info, leaderboard) for task_info, leaderboard in data_list])

    def reset(self) -> None:
        self.rankings = defaultdict(self.delta_mgr.default_rating)

    def _eval_accuracy_task(self, _, leaderboard) -> float:
        leaderboard["rankings"] = [self.rankings[name] for name in leaderboard["name"]]
        overall_rankings_range = ( min(self.rankings.values()), max(self.rankings.values()) )
        scores = self.scoring_mgr.get_scores(leaderboard)

        interp_ratings = [hlp.interpolate_inverse(x, *overall_rankings_range, *SCORE_RANGE) for x in leaderboard["rankings"]]
        norm = np.linalg.norm(np.array(scores)-np.array(interp_ratings))
        
        return norm
  
