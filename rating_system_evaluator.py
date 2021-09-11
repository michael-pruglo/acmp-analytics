import random, statistics
from globals import *
import database

@dataclass
class RatingHistory:
    mean: float = 0.0
    variance: float = 0.0
    history: list = field(default_factory=list)

    def add_rating(self, val):
        self.history.append(val)
        self.mean = statistics.mean(self.history)
        if len(self.history) > 1:
            self.variance = statistics.variance(self.history, self.mean)


def evaluate(rs_class):
    RUNS = 5
    ratings: dict[str, RatingHistory] = {}
    training_data, eval_data = _prepare_data()
    for i in range(1, RUNS+1):
        random.shuffle(training_data)
        run_ratings = rs_class().rate(training_data)
        for name, rating in run_ratings.items():
            ratings.setdefault(name, RatingHistory()).add_rating(rating)
    _print_results(rs_class.__name__, ratings, _calc_accuracy(ratings, eval_data), _calc_variance(ratings))



def _prepare_data():
    TASK_NO = 10
    TRAINING_TASKS = TASK_NO*9//10
    data = []
    ids = list(range(1, TASK_NO+1))
    random.shuffle(ids)
    for id in ids:
        task_info = TaskInfo(id, Lang.cpp, database.get_accepted_submissions(id))
        leaderboard = database.get_task_leaderboard(task_info)
        data.append((task_info, leaderboard))
    return data[:TRAINING_TASKS+1], data[TRAINING_TASKS+1:]

def _calc_accuracy(ratings, eval_data):
    for _, leaderboard in eval_data:
        return 0.0
    return 0.0

def _calc_variance(ratings):
    return statistics.mean([rh.variance for rh in ratings.values()])
        
def _print_results(rs_name, ratings, accuracy, variance):
    print("\n\n"+"="*111)
    print(f"rating system: {rs_name}")
    print(f"accuracy:      {accuracy:.3f}")
    print(f"variance:      {variance:.3f}")
    for name, hist in sorted(ratings.items(), key=lambda x: x[1].mean, reverse=True):
        print(f"{name:<32} {hist.mean:>12.3f} {hist.variance:>10.2f} ", str([f"{i:>8.2f}" for i in hist.history]).replace("'", ""))
