from numpy import inner
import pandas as pd
from rating_system import *
import rating_system_evaluator, database

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

def show_leaderboard(task_id, lang=Lang.cpp):
    info = TaskInfo(task_id, lang, database.get_accepted_submissions(task_id))
    leaderboard = database.get_task_leaderboard(info)
    DifficultyManager().get_task_difficulty(info, leaderboard, verbose=True)
    gl = database.get_global_leaderboard()
    leaderboard = leaderboard.merge(gl, on="name")
    print(leaderboard)

def evaluate():
    rating_system_evaluator.evaluate([
       #RatingSystem(TMX_max(), description="tmx max"),
       RatingSystem(TMX_const(), description="tmx const"),
       #RatingSystem(SME_EvE(ELO()), description="elo eve"),
       #RatingSystem(TrueSkill(), ScoringManager(deal_with_ties=False), description="TrueSkill"),

    ],
    0, 1, tasks=30)

def print_global_leaderboard(recalc:bool=False):
    if recalc:
        database.construct_global_leaderboard(rat_systems = [
                RatingSystem(SME_EvE(MOV()), description="       Elo"),
                RatingSystem(TMX_const(), description="Skill points"),
            ],
            runs = 100
        )
    gl = database.get_global_leaderboard()#.sort_values("       Elo", ascending=False)
    print(gl.head(50))
    print("\n\n\n\n")
    print(database.get_global_leaderboard_row("Пругло Михаил"))

def update():
    fetch_all()
    print_global_leaderboard(recalc=True)

 
if __name__ == "__main__":
    pd.options.display.float_format = "{:.2f}".format

    #update()
    show_leaderboard(267)
