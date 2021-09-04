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

    def show_rankings(self):
        print(self.rating_system.get_ratings())



if __name__ == "__main__":
    c = Client()
    #c.set_range(range(1,10), Lang.cpp)
    #c.show_rated_table(TaskInfo(8, Lang.cpp))
    c.rate([950], Lang.cpp)
    print("Rankings after:")
    #print(c.show_rankings())
    