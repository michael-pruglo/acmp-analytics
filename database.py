import network, global_leaderboard
import pandas as pd, pickle, atexit, os

_LEADERBOARD_CACHE_FILENAME = "dbcache/leaderboards_cache.h5"
_AC_SUB_CACHE_FILENAME = "dbcache/ac_sub_cache.p"
_GLOBAL_LEADERBOARD_CACHE_FILENAME = "dbcache/global_leaderboard_cache.h5"
def _init_leaderboards_cache():
    return pd.HDFStore(_LEADERBOARD_CACHE_FILENAME, complevel=7, complib='zlib')

_leaderboards_cache = _init_leaderboards_cache()
_ac_sub_cache = {}
_global_leaderboard = pd.read_hdf(_GLOBAL_LEADERBOARD_CACHE_FILENAME, "gl")


def prepare_cache(task_info_list):
    _update_leaderboards_cache(task_info_list)
    _update_ac_sub_cache([t.id for t in task_info_list])

def fetch(task_info_list):
    global _leaderboards_cache
    _leaderboards_cache.close()
    os.remove(_LEADERBOARD_CACHE_FILENAME)
    _leaderboards_cache = _init_leaderboards_cache()
    _ac_sub_cache.clear()
    prepare_cache(task_info_list)

def get_task_leaderboard(task_info):
    key = str(task_info)
    if key not in _leaderboards_cache:
        _leaderboards_cache[key] = network.get_task_leaderboard(task_info)

    return _leaderboards_cache[key]

def get_accepted_submissions(task_no):
    if task_no not in _ac_sub_cache:
        _update_ac_sub_cache([task_no])

    return _ac_sub_cache[task_no]

def construct_global_leaderboard(rat_systems, runs):
    gl = global_leaderboard.calc(list(range(1,1001)), rat_systems, runs)
    gl.to_hdf(_GLOBAL_LEADERBOARD_CACHE_FILENAME, "gl", complevel=7, complib='zlib')

def get_global_leaderboard():
    return _global_leaderboard

def get_global_leaderboard_row(name):
    return _global_leaderboard.loc[_global_leaderboard["name"] == name]



def _update_leaderboards_cache(task_info_list):
    for task_info in task_info_list:
        get_task_leaderboard(task_info)

def _update_ac_sub_cache(id_list):
    id_list = [id for id in id_list if id not in _ac_sub_cache]
    if not len(id_list):
        return
    TASKS_PER_PAGE = 50
    def get_page(id):
        return (id-1)//TASKS_PER_PAGE
    pages = { get_page(id) for id in id_list }
    table = network.get_accepted_submissions(pages)
    table = table[table["id"].isin(id_list)]
    assert(len(table.index)==len(id_list))
    _ac_sub_cache.update(zip(table["id"], table["acc_no"]))

def _close_database():
    _leaderboards_cache.close()
    with open(_AC_SUB_CACHE_FILENAME, 'wb') as f:
        pickle.dump(_ac_sub_cache, f, protocol=pickle.HIGHEST_PROTOCOL)




try:
    with open(_AC_SUB_CACHE_FILENAME, 'rb') as f:
        _ac_sub_cache = pickle.load(f)
except FileNotFoundError:
    _ac_sub_cache = {}

atexit.register(_close_database)
