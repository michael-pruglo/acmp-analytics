import pandas as pd

class RatingSystem:
    def __init__(self):
        self.ratings = pd.DataFrame(columns=["name", "elo", "rated tasks"])
        
    def recalc_ratings(self, tables_data_list):
        for task_info, table in tables_data_list:
            table_with_points = self._award_points(table)
            self._update_ratings(task_info, table_with_points)

    def get_ratings(self):
        return self.ratings

    def get_rated_table(self, table):
        return self._award_points(table)



    def _award_points(self, table):
        table["points"] = 21-table["rank"]
        return table

    def _update_ratings(self, task_info, table_with_points):
        for i, row in table_with_points.iterrows():
            name = row["name"]
            pass #if self.ratings.contains name:
