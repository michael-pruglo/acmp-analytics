from rating_system import RatingSystem
import pandas as pd
from dataclasses import dataclass
from collections import defaultdict
from typing import List
from globals import *
import database

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

def _prepare_data(task_ids: List[int]):
    data = []
    for id in task_ids:
        task_info = TaskInfo(id, Lang.cpp, database.get_accepted_submissions(id))
        leaderboard = database.get_task_leaderboard(task_info)
        data.append((task_info, leaderboard))
    return data

def _construct_leaderboard(dataframes: List[pd.DataFrame], columns_to_sort_by:List[str]) -> pd.DataFrame:
    global_leaderboard = pd.concat(dataframes, axis=1)
    global_leaderboard.insert(loc=0, column="name", value=global_leaderboard.index)
    global_leaderboard.sort_values(columns_to_sort_by, ascending=False, inplace=True)
    global_leaderboard.index = range(1, len(global_leaderboard.index)+1)

    return global_leaderboard




def calc(task_ids: List[int], rat_systems: List[RatingSystem], runs=5) -> pd.DataFrame:
    data = _prepare_data(task_ids)

    dataframes = []
    for rat_sys in rat_systems:
        rating_dict = rat_sys.rate_multiple_runs(data, runs)
        dataframes.append(pd.DataFrame.from_dict(rating_dict, orient='index', columns=[rat_sys.description], dtype=float))
    
    dataframes.append(Statistics.collect(data))
    
    return _construct_leaderboard(dataframes, [r.description for r in rat_systems])


#todo: print task leaderboards with rank info
#todo: add breaking 100 bonus