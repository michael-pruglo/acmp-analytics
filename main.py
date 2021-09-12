import pandas as pd
from rating_system import *
import rating_system_evaluator, database

def fetch_all(lang):
    database.fetch([TaskInfo(id, lang) for id in range(1, 1001)])

def prepare_local_cache():
    fetch_all(Lang.cpp)
    rating_system_evaluator._cache_accuracy_dist_graph(1000000)


if __name__ == "__main__":
    pd.options.display.float_format = "{:.2f}".format

    rating_system_evaluator.evaluate([
        RatingSystem(DifficultyManager(), ScoringManager(), TMX_max()),
        RatingSystem(DifficultyManager(), ScoringManager(), TMX_const()),
    ])