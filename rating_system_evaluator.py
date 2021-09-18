import random, statistics, pickle, numpy as np, matplotlib.pyplot as plt
from globals import *
from rating_system import RatingSystem
import database, helpers as hlp

@dataclass
class RatingHistory:
    mean: float = 0.0
    std: float = 0.0
    history: list = field(default_factory=list)

    def add_rating(self, val):
        self.history.append(val)
        self.mean = statistics.mean([float(x) for x in self.history])
        if len(self.history) > 1:
            self.std = statistics.pstdev([float(x) for x in self.history], self.mean)


def evaluate(rat_systems, runs_p=1, runs_nonp=10, tasks=1000):
    with open(_ACCURACY_DIST_GRAPH_FILENAME, 'rb') as f:
        pickle.load(f)
    colors = ["C"+str(i) for i in range(1, len(rat_systems)+1)]

    for rs, color in zip(rat_systems, colors):
        if runs_p:    _eval_class(rs, tasks, True,  runs_p,    color)
        if runs_nonp: _eval_class(rs, tasks, False, runs_nonp, color)

    plt.legend()
    plt.show()



def _eval_class(rat_sys:RatingSystem, task_no, persistent=True, runs=1, graphing_color="#3ded97"):
    ratings: dict[str, RatingHistory] = {}
    data =_load_data(task_no)
    training_data, eval_data = _split_data(data)
    accuracies = []
    for i in range(runs):
        if i%10==0: print(f"{rat_sys.description}: run {i:>4}/{runs:>4}")
        
        if persistent:
            random.shuffle(training_data)
        else:
            training_data, eval_data = _split_data(data)
        rat_sys.reset()
        run_ratings = rat_sys.rate(training_data)
        accuracies.append(rat_sys.eval_accuracy(eval_data))
        for name, rating in run_ratings.items():
            ratings.setdefault(name, RatingHistory()).add_rating(rating)
    _print_results(rat_sys.description, ratings, accuracies, persistent, graphing_color)

def _load_data(task_no=1000):
    data = []
    ids = random.sample(range(1,1001), task_no) if task_no<1000 else list(range(1,1001))
    for id in ids:
        task_info = TaskInfo(id, Lang.cpp, database.get_accepted_submissions(id))
        leaderboard = database.get_task_leaderboard(task_info)
        data.append((task_info, leaderboard))
    return data

def _split_data(data):
    TRAINING_TASKS = len(data)*9//10
    random.shuffle(data)
    return data[:TRAINING_TASKS], data[TRAINING_TASKS:]

def _print_results(rs_name, ratings, accuracies, persistent, graphing_color):
    avg_accuracy = statistics.mean(accuracies)
    def _print_header():
        print("\n\n"+"="*111)
        print(f"rating system: {rs_name}")
        print(f"accuracy:      {avg_accuracy:.3f}")
        print(f"stdev:         {statistics.mean([rh.std for rh in ratings.values()]):.3f}")
        print()
    
    def _print_rankings():
        for i, (name, hist) in enumerate(sorted(ratings.items(), key=lambda x: x[1].mean, reverse=True)[:20]):
            print(f"{i+1:>3} {name:<32} {hist.mean:>12.3f} {hist.std:>10.2f}    ", hist.history)
    
    def _plot_vertical_lines():
        if persistent:
            plt.axvline(avg_accuracy, color=graphing_color, linestyle="-.", label=rs_name + " persistent")
        else:
            print("\n\n", hlp.pretty(accuracies))
            bins = 10
            l = len(accuracies)
            if l < 10:
                bins = l
            elif l >= 100:
                bins = l//10 
            plt.hist(accuracies, bins, density=True, color=graphing_color, label=rs_name, alpha=0.65)
        

    _print_header()
    _print_rankings()
    _plot_vertical_lines()


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

    fig_handle = plt.figure("accuracy distribution", figsize=(17,5))
    plt.hist(norms, 300, density=True)
    mu = statistics.mean(norms)
    std = statistics.stdev(norms)
    plt.axvline(mu, color='orange', label="mean")
    plt.axvline(mu-3*std,   color='y')
    plt.axvline(mu-2*std,   color='y')
    plt.axvline(mu-1*std,   color='y')
    plt.axvline(mu+1*std,   color='y')
    plt.axvline(mu+2*std,   color='y')
    plt.axvline(mu+3*std,   color='y')
    with open(_ACCURACY_DIST_GRAPH_FILENAME, 'wb') as f:
        pickle.dump(fig_handle, f) 
    print("success")
