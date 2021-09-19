import pandas as pd
from rating_system import *
import rating_system_evaluator, database, global_leaderboard

def fetch_all(lang=Lang.cpp):
    database.fetch([TaskInfo(id, lang) for id in range(1, 1001)])

def prepare_local_cache():
    fetch_all()
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

def evaluate():
    rating_system_evaluator.evaluate([
       #RatingSystem(TMX_max(), description="tmx max"),
       RatingSystem(TMX_const(), description="tmx const"),
       #RatingSystem(SME_EvE(ELO()), description="elo eve"),
       #RatingSystem(TrueSkill(), ScoringManager(deal_with_ties=False), description="TrueSkill"),

    ],
    0, 1, tasks=30)

def print_global_leaderboard():
    gl = global_leaderboard.calc(
        task_ids = list(range(1,1001)),
        rat_systems = [
            RatingSystem(TMX_const(), description="Skill points"),
            RatingSystem(SME_EvE(MOV()), description="       Elo"),
        ],
        runs = 10
    )
    print(gl.head(50))




if __name__ == "__main__":
    pd.options.display.float_format = "{:.2f}".format

    fetch_all()
    print_global_leaderboard()
