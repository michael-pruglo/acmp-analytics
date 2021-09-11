from rating_system import RatingSystem
from globals import *
import database

class Client:
    def __init__(self):
        self.rating_system = RatingSystem()

    def rate(self, task_list, lang):
        database.prepare_cache([TaskInfo(id, lang) for id in task_list])
        data_map = {}
        for id in task_list:
            info = TaskInfo(id, lang, database.get_accepted_submissions(id))
            data_map[info] = database.get_task_leaderboard(info)
        self.rating_system.rate(data_map)

    def show_difficulty(self, task_list, lang):
        database.prepare_cache([TaskInfo(id, lang) for id in task_list])
        diff_map = {}
        for id in task_list:
            info = TaskInfo(id, lang, database.get_accepted_submissions(id))
            table = database.get_task_leaderboard(info)
            diff_map[id] = self.rating_system._get_task_difficulty(info, table["code_len"])
        for k,v in sorted(diff_map.items(), key=lambda p:p[1], reverse=True):
            print(k,v)

    def show_rankings(self):
        self.rating_system.show_rankings()



if __name__ == "__main__":
    c = Client()
    #c.set_range(range(1,10), Lang.cpp)
    #c.show_rated_table(TaskInfo(8, Lang.cpp))
    c.rate([14,45,72], Lang.cpp)
    c.show_rankings()

