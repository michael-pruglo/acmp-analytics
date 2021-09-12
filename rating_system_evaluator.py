import random, statistics, pickle, numpy as np, matplotlib.pyplot as plt
from globals import *
import database, helpers as hlp

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
    RUNS = 1
    ratings: dict[str, RatingHistory] = {}
    training_data, eval_data = _prepare_data()
    accuracy = 0.0
    for i in range(1, RUNS+1):
        random.shuffle(training_data)
        #print("RUN # ", i, "\ntr data:", [t[0].id for t in training_data], "eval_data:", [t[0].id for t in eval_data])
        rat_sys = rs_class()
        run_ratings = rat_sys.rate(training_data)
        accuracy += rat_sys.eval_accuracy(eval_data) / RUNS
        for name, rating in run_ratings.items():
            ratings.setdefault(name, RatingHistory()).add_rating(rating)
    _print_results(rs_class.__name__, ratings, accuracy, _calc_variance(ratings))



def _prepare_data():
    TASK_NO = 200
    TRAINING_TASKS = TASK_NO*9//10
    data = []
    ids = list(range(1, TASK_NO+1))
    random.shuffle(ids)
    for id in ids:
        task_info = TaskInfo(id, Lang.cpp, database.get_accepted_submissions(id))
        leaderboard = database.get_task_leaderboard(task_info)
        data.append((task_info, leaderboard))
    return data[:TRAINING_TASKS], data[TRAINING_TASKS:]

def _calc_variance(ratings):
    return statistics.mean([rh.variance for rh in ratings.values()])
        
def _print_results(rs_name, ratings, accuracy, variance):
    def _print_header():
        print("\n\n"+"="*111)
        print(f"rating system: {rs_name}")
        print(f"accuracy:      {accuracy:.3f}")
        print(f"variance:      {variance:.3f}")
        print()
    
    def _print_rankings():
        for i, (name, hist) in enumerate(sorted(ratings.items(), key=lambda x: x[1].mean, reverse=True)[:30]):
            print(f"{i+1:>3} {name:<32} {hist.mean:>12.3f} {hist.variance:>10.2f}    ", hlp.pretty(hist.history, 2))
    
    def _plot():
        with open(_ACCURACY_DIST_GRAPH_FILENAME, 'rb') as f:
            pickle.load(f)
            plt.axvline(accuracy, color='#3ded97', label="curr")
            plt.legend()
            plt.show()
    
    _print_header()
    _print_rankings()
    _plot()


_ACCURACY_DIST_GRAPH_FILENAME = "dbcache/accuracy_dist.p"
def _cache_accuracy_dist_graph(N = 10000):
    SCORES_NO = 20

    def get_scores():
        v = np.random.default_rng().uniform(SCORE_RANGE[0]+1e-6, SCORE_RANGE[1]+1e-6, SCORES_NO-2)
        v = np.insert(v, np.random.randint(0, len(v)), SCORE_RANGE[0])
        v = np.insert(v, np.random.randint(0, len(v)), SCORE_RANGE[1])
        return v

    print("caching accurasy dist graph... ", end="", flush=True)
    standard = np.sort(get_scores())
    norms = []
    for _ in range(0, N):
        curr = get_scores()
        random.shuffle(curr)
        norms.append(np.linalg.norm(standard-curr))
    
    scores = np.linspace(*SCORE_RANGE, SCORES_NO)
    v_opposite = np.linalg.norm(scores-np.flip(scores))

    fig_handle = plt.figure("accuracy distribution")
    plt.hist(norms, 300, density=True)
    plt.axvline(statistics.mean(norms),     color='y', label="mean")
    plt.axvline(statistics.median(norms),   color='y', label="median")
    plt.axvline(v_opposite,                 color='r', label="worst")
    with open(_ACCURACY_DIST_GRAPH_FILENAME, 'wb') as f:
        pickle.dump(fig_handle, f) 
    print("success")

