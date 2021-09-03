from rating_system import RatingSystem
from globals import *
import database

class Client:
    def __init__(self):
        self.rating_system = RatingSystem()

    def set_range(self, range, lang):
        tables = []
        for task_no in range:
            task_info = TaskInfo(task_no, lang)
            table_tuple = (task_info, database.get_table(task_info))
            tables.append(table_tuple) 
        self.rating_system.recalc_ratings(tables)

    def show_table(self, task_info):
        print(database.get_table(task_info))

    def show_rated_table(self, task_info):
        table = database.get_table(task_info)
        print(self.rating_system.get_rated_table(table))

    def show_rankings(self):
        print(self.rating_system.get_ratings())



if __name__ == "__main__":
    c = Client()
    #c.set_range(range(1,10), Lang.cpp)
    #c.show_rated_table(TaskInfo(8, Lang.cpp))
    l = [7,145,146,938]
    database._update_ac_sub_cache(l)
    for i in l:
        print(i, database.get_accepted_submissions(i))