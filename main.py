import pandas as pd, matplotlib.pyplot as plt
import rating_system_evaluator, database
from rating_system import *
from elo import *
from skill_points import *

def fetch_all(lang=Lang.cpp):
    database.fetch([TaskInfo(id, lang) for id in range(1, 1001)])

def prepare_local_cache():
    fetch_all()
    rating_system_evaluator._cache_accuracy_dist_graph(1000000)

def show_potentials(n=100):
    dmap = {}
    for id in range(1, 1001):
        info = TaskInfo(id, Lang.cpp, database.get_accepted_submissions(id))
        leaderboard = database.get_task_leaderboard(info)
        sol = "+" if "Пругло Михаил" in list(leaderboard["name"]) else "unsolved"
        diff = DifficultyManager().get_task_difficulty(info, leaderboard, (0,0))
        dmap[id] = (diff, sol)
    for id, (diff, s) in sorted(dmap.items(), key=lambda x: x[1][0], reverse=True)[:n]:
        print(f"{id:>4} {diff:>10.2f} {s}")

def show_rivalry(name1:str, name2:str, n=200):
    dmap = {}
    for id in range(1, 1001):
        info = TaskInfo(id, Lang.cpp, database.get_accepted_submissions(id))
        leaderboard = database.get_task_leaderboard(info)
        if all(name in list(leaderboard["name"]) for name in [name1, name2]):
            diff = DifficultyManager().get_task_difficulty(info, leaderboard, (0,0))
            leaderboard["scores"] = ScoringManager().get_scores(leaderboard)
            head_to_head = leaderboard[leaderboard["name"].isin([name1, name2])]
            dmap[id] = (diff, head_to_head)
    for id, (diff, hth) in sorted(dmap.items(), key=lambda x: x[1][0], reverse=True)[:n]:
        print(f"{id:>4} {diff:>10.2f}")
        print(hth)
        print()

def show_leaderboard(task_id, lang=Lang.cpp, reload:bool=False):
    if reload==True:
        database.update_one_task(TaskInfo(task_id, lang))
    info = TaskInfo(task_id, lang, database.get_accepted_submissions(task_id))
    leaderboard = database.get_task_leaderboard(info)
    scores = leaderboard["scores"] = ScoringManager().get_scores(leaderboard)
    diff = DifficultyManager().get_task_difficulty(info, leaderboard, verbose=True)
    pts = leaderboard["pts_earned"] = TMX_const()._calc_rank_deltas(info, leaderboard)
    gl = database.get_global_leaderboard()
    gl.insert(0, "player's global rank", gl.index)
    leaderboard = leaderboard.merge(gl, on="name")
    print(leaderboard)
    
    plt.clf()
    plt.title(f"Task #{task_id}")
    plt.xlabel("score")
    plt.xticks(range(1,21))
    plt.ylabel("skill points")
    plt.yticks( range(1, int(max(pts)+1)+1) )
    plt.grid(alpha=0.5, linestyle='dashed')
    plt.plot(scores, pts, 'ro')
    for i, name in enumerate(leaderboard["name"]):
        plt.annotate(f"{name}: {pts[i]:.2f}", (scores[i],pts[i]), xytext=(scores[i]+1.4,pts[i]+.1), arrowprops={'arrowstyle':'->'})
    interp_k = diff / sum(TMX_max()._distribute_points(diff, scores))
    hlp.plot(scores, lambda x: TMX_max()._distrib_f(diff, x)*interp_k )
    plt.show()

def evaluate():
    rating_system_evaluator.evaluate([
       #RatingSystem(TMX_max(), description="tmx max"),
       RatingSystem(TMX_const(), description="tmx const"),
       #RatingSystem(SME_EvE(ELO()), description="elo eve"),
       #RatingSystem(TrueSkill(), ScoringManager(deal_with_ties=False), description="TrueSkill"),

    ],
    0, 1, tasks=30)

def show_global_leaderboard(recalc:bool=False):
    if recalc==True:
        database.construct_global_leaderboard(rat_systems = [
                RatingSystem(SME_EvE(MOV()), description="       Elo"),
                RatingSystem(TMX_const(), description="Skill points"),
            ],
            runs = 100
        )
    gl = database.get_global_leaderboard()#.sort_values("       Elo", ascending=False)
    print(gl.head(50))
    print("\n\n\n\n")
    #print(database.get_global_leaderboard_row("Пругло Михаил"))

    plt.clf()
    plot_threshold = 1550
    main_col = "       Elo"
    assert(main_col in gl)
    plot_data = [g for g in gl[main_col] if g>plot_threshold]
    plt.title(f"PDF for players with elo>{plot_threshold}\n({len(plot_data)} of them)")
    plt.hist(plot_data, 100, density=True)
    plt.show()

def update():
    fetch_all()
    show_global_leaderboard(recalc=True)

def show_worst(n=300):
    rmap = {}
    for id in range(1, 1001):
        info = TaskInfo(id, Lang.cpp, database.get_accepted_submissions(id))
        leaderboard = database.get_task_leaderboard(info)
        if "Пругло Михаил" in list(leaderboard["name"]):
            scores = ScoringManager().get_scores(leaderboard)
            rank = leaderboard[leaderboard["name"]=="Пругло Михаил"].index[0]
            rmap[id] = scores[rank] if rank>0 else scores[0]-scores[1]
    for id, rat in sorted(rmap.items(), key=lambda item: item[1], reverse=True)[:n]:
        comment = ""
        if id in [40, 79, 86, 108, 195, 513, 539, 554, 756, 903]: comment = "cheats"
        if id in [335, 115, 368, 976]: comment = "long"
        if id in [3, 8, 15, 59, 92, 312, 462, 606, 697, 766, 777, 778, 794, 839, 907, 929, 942, 943, 948, 970]: comment = "tie best, seems to be optimized"
        if id in [7, 499, 548]: comment = ":("
        print(f"{id:>4} {rat:.2f} {comment}")

 
if __name__ == "__main__":
    pd.options.display.float_format = "{:.2f}".format

    #update()
    #WARNING show_global_leaderboard(recalc=True)

    #show_global_leaderboard()
    show_leaderboard(263, reload=True)
    #show_potentials(400)
    show_worst()
    #show_rivalry("Пругло Михаил", "Хворых Павел")
