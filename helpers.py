import numpy as np, matplotlib.pyplot as plt
from math import isclose

def pretty(list_of_floats, precision=3) -> str:
    return str([f"{s:.{precision}f}" for s in list_of_floats]).replace("'", "")

def interpolate(x:float, min_orig:float, max_orig:float, min_target:float, max_target:float) -> float:
    if min_orig==max_orig:
        return (max_target+min_target)/2
    return (x-min_orig)/(max_orig-min_orig)*(max_target-min_target) + min_target

def interpolate_inverse(x:float, min_orig:float, max_orig:float, min_target:float, max_target:float) -> float:
    if min_orig==max_orig:
        return (max_target+min_target)/2
    return max_target - (x-min_orig)/(max_orig-min_orig)*(max_target-min_target)

def plot(x_list, f) -> None:
    x_axis = np.linspace(min(x_list)*.9, max(x_list)*1.1)
    plt.plot(
        x_axis, [f(x) for x in x_axis],
        x_list, [f(x) for x in x_list], 'yo',
    )

def is_in_range(x, min, max) -> bool:
    return min < x < max or isclose(x, min) or isclose(x, max)


if __name__ == "__main__":
    assert(interpolate(71,0,100,0,10)==7.1)
    assert(interpolate(80,80,80,5,7)==6)