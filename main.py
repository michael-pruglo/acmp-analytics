import pandas as pd
from rating_system import *
import rating_system_evaluator, database

def fetch_all(lang):
    database.fetch([TaskInfo(id, lang) for id in range(1, 1001)])

def prepare_local_cache():
    fetch_all(Lang.cpp)
    rating_system_evaluator._cache_accuracy_dist_graph(1000000)

def show_potentials():
    dmap = {}
    for id in range(1, 1001):
        info = TaskInfo(id, Lang.cpp, database.get_accepted_submissions(id))
        leaderboard = database.get_task_leaderboard(info)
        sol = "+" if "Пругло Михаил" in list(leaderboard["name"]) else "unsolved"
        diff = DifficultyManager().get_task_difficulty(info, leaderboard, (0,0))
        dmap[id] = (diff, sol)
    for id, (diff, s) in sorted(dmap.items(), key=lambda x: x[1][0], reverse=True):
        print(f"{id:>4} {diff:>10.2f} {s}")


if __name__ == "__main__":
    pd.options.display.float_format = "{:.2f}".format

    rating_system_evaluator.evaluate([
       #RatingSystem(DifficultyManager(), ScoringManager(), TMX_max(), description="tmx max"),
       #RatingSystem(DifficultyManager(), ScoringManager(), TMX_const(), description="tmx const"),
       #RatingSystem(DifficultyManager(), ScoringManager(), SME(), description="sme"),
       #RatingSystem(DifficultyManager(), ScoringManager(), SME(MOV()), description="sme mov"),
       #RatingSystem(DifficultyManager(), ScoringManager(), SME_EvE(ELO(410, 35)), description="sme eve"),
       #RatingSystem(DifficultyManager(), ScoringManager(), SME_EvE(MOV()), description="sme eve mov"),
       #RatingSystem(DifficultyManager(), ScoringManager(), SME_avgn(), description="sme avgn"),
       #RatingSystem(DifficultyManager(), ScoringManager(), SME_avgn(MOV()), description="sme avgn mov"),
       #RatingSystem(DifficultyManager(), ScoringManager(), SME_avg2(), description="sme avg2"),
       #RatingSystem(DifficultyManager(), ScoringManager(), SME_avg2(MOV()), description="sme avg2 mov"),
       RatingSystem(DifficultyManager(), ScoringManager(deal_with_ties=False), TrueSkill(), description="trueskill"),
    ],
    0, 10, tasks=1000)

