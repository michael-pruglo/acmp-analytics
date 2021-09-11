import network
import pandas as pd

leaderboards_cache = pd.HDFStore("dbcache/leaderboards_cache.h5")
ac_sub_cache = {}

def prepare_cache(task_info_list):
    _update_leaderboards_cache(task_info_list)
    _update_ac_sub_cache([t.id for t in task_info_list])

def get_task_leaderboard(task_info):
    key = str(task_info)
    if key not in leaderboards_cache:
        leaderboards_cache[key] = network.get_task_leaderboard(task_info)

    return leaderboards_cache[key]

def get_accepted_submissions(task_no):
    if task_no not in ac_sub_cache:
        _update_ac_sub_cache([task_no])

    return ac_sub_cache[task_no]



def _update_leaderboards_cache(task_info_list):
    for task_info in task_info_list:
        get_task_leaderboard(task_info)

def _update_ac_sub_cache(id_list):
    TASKS_PER_PAGE = 50
    def get_page(id):
        return (id-1)//TASKS_PER_PAGE
    pages = { get_page(id) for id in id_list }
    table = network.get_accepted_submissions(pages)
    table = table[table["id"].isin(id_list)]
    assert(len(table.index)==len(id_list))
    ac_sub_cache.update(zip(table["id"], table["acc_no"]))
