import random

def coin_toss_sampler():
    return random.choice(["H", "T"])

def f_if_heads(toss):
    return 1 if toss == "H" else 0