import numpy as np
import matplotlib.pyplot as plt

def pretty(list_of_floats, precision=3):
    return str([f"{s:.{precision}f}" for s in list_of_floats]).replace("'", "")

def interpolate(x, min_orig, max_orig, min_target, max_target):
    if min_orig==max_orig:
        return (max_target+min_target)/2
    return (x-min_orig)/(max_orig-min_orig)*(max_target-min_target) + min_target

def plot(x_list, f):
    x_axis = np.linspace(min(x_list)*.9, max(x_list)*1.1)
    plt.plot(x_list, [f(x) for x in x_list], 'ro',
             x_axis, [f(x) for x in x_axis])

if __name__ == "__main__":
    assert(interpolate(71,0,100,0,10)==7.1)
    assert(interpolate(80,80,80,5,7)==6)