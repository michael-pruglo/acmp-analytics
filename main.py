from globals import *
import rating_system_evaluator
from rating_system import TMX_max
import database

def fetch_all(lang):
    database.fetch([TaskInfo(id, lang) for id in range(1, 1001)])

def prepare_local_cache():
    fetch_all(Lang.cpp)
    rating_system_evaluator._cache_accuracy_dist_graph(1000000)


if __name__ == "__main__":
    rating_system_evaluator.evaluate(TMX_max)
