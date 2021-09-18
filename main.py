import pandas as pd
from dataclasses import dataclass
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

def evaluate():
    rating_system_evaluator.evaluate([
       #RatingSystem(TMX_max(), description="tmx max"),
       RatingSystem(TMX_const(), description="tmx const"),
       #RatingSystem(SME_EvE(ELO()), description="elo eve"),
       #RatingSystem(TrueSkill(), ScoringManager(deal_with_ties=False), description="TrueSkill"),

    ],
    0, 1, tasks=30)


class Statistics:
    @dataclass
    class SRow:
        tasks: int = 0
        gold: int = 0
        silver: int = 0
        bronze: int = 0
        avg_rating: float = 0.0
        def add_ranked_task(self, rank):
            self.tasks += 1
            if rank == 1: self.gold += 1
            if rank == 2: self.silver += 1
            if rank == 3: self.bronze += 1
            self.avg_rating = (self.avg_rating*(self.tasks-1) + rank) / self.tasks
            

    def collect(data) -> pd.DataFrame:
        stats = defaultdict(Statistics.SRow)
        for _, leaderboard in data:
            for _, row in leaderboard.iterrows():
                stats[row["name"]].add_ranked_task(row["rank"])
        return pd.DataFrame.from_dict(stats, orient='index', columns=["tasks", "gold", "silver", "bronze", "avg_rating"])


if __name__ == "__main__":
    pd.options.display.float_format = "{:.2f}".format

    data = []
    for id in range(7, 11):
        task_info = TaskInfo(id, Lang.cpp, database.get_accepted_submissions(id))
        leaderboard = database.get_task_leaderboard(task_info)
        data.append((task_info, leaderboard))
    
    rat_systems = [
        RatingSystem(TMX_const(), description="Skill points"),
        RatingSystem(SME_EvE(MOV()), description="       Elo"),
    ]
    dataframes = []
    for rat_sys in rat_systems:
        rating_dict = rat_sys.rate(data)
        dataframes.append(pd.DataFrame.from_dict(rating_dict, orient='index', columns=[rat_sys.description], dtype=float))
    dataframes.append(Statistics.collect(data))
    global_leaderboard = pd.concat(dataframes, axis=1)

    print(global_leaderboard.sort_values([r.description for r in rat_systems], ascending=False))
        



    