import random

def pi_sampler_point_in_square():
    x = random.uniform(0, 1)
    y = random.uniform(0, 1)

    return (x, y)

def f_inside_circle(point):
    x, y = point
    return 1 if x ** 2 + y ** 2 <=1 else 0
