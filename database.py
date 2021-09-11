import network
import pandas as pd
import pickle, atexit

_leaderboards_cache = pd.HDFStore("dbcache/leaderboards_cache.h5")
_ac_sub_cache = {}

def prepare_cache(task_info_list):
    _update_leaderboards_cache(task_info_list)
    _update_ac_sub_cache([t.id for t in task_info_list])

def get_task_leaderboard(task_info):
    key = str(task_info)
    if key not in _leaderboards_cache:
        _leaderboards_cache[key] = network.get_task_leaderboard(task_info)

    return _leaderboards_cache[key]

def get_accepted_submissions(task_no):
    if task_no not in _ac_sub_cache:
        _update_ac_sub_cache([task_no])

    return _ac_sub_cache[task_no]



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
    print("__closing database")
    _leaderboards_cache.close()
    with open("dbcache/ac_sub_cache.p", 'wb') as f:
        pickle.dump(_ac_sub_cache, f, protocol=pickle.HIGHEST_PROTOCOL)




try:
    with open("dbcache/ac_sub_cache.p", 'rb') as f:
        _ac_sub_cache = pickle.load(f)
except FileNotFoundError:
    _ac_sub_cache = {}

atexit.register(_close_database)
