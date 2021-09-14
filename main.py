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

    #rating_system_evaluator.evaluate([
    #    RatingSystem(DifficultyManager(AS_C=0.05, LEN_C=0.7, PS_C=1.0), ScoringManager(), TMX_const(), description="1"),
    #    RatingSystem(DifficultyManager(AS_C=0.1, LEN_C=0.7, PS_C=1.0), ScoringManager(), TMX_const(), description="2"),
    #    RatingSystem(DifficultyManager(AS_C=0.2, LEN_C=0.7, PS_C=1.0), ScoringManager(), TMX_const(), description="3"),
    #    RatingSystem(DifficultyManager(AS_C=0.3, LEN_C=0.7, PS_C=1.0), ScoringManager(), TMX_const(), description="4"),
    #    RatingSystem(DifficultyManager(AS_C=0.4, LEN_C=0.7, PS_C=1.0), ScoringManager(), TMX_const(), description="5"),
    #    RatingSystem(DifficultyManager(AS_C=0.5, LEN_C=0.7, PS_C=1.0), ScoringManager(), TMX_const(), description="6"),
    #],
    #0, 100)
    rating_system_evaluator.evaluate([
       RatingSystem(DifficultyManager(AS_C=0.5, LEN_C=0.7, PS_C=1.0), ScoringManager(), SME(),     description="sme"),
       RatingSystem(DifficultyManager(AS_C=0.5, LEN_C=0.7, PS_C=1.0), ScoringManager(), SME_EvE(410, 35), description="sme eve"),
    ],
    0, 30, tasks=1000)

    #show_potentials()
