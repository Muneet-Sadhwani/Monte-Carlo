import random
import math
import numpy as np

def gbm_terminal_sampler(S0, r, sigma, T):
    def sampler():
        Z = random.gauss(0, 1)
        ST = S0 * math.exp(
            (r - 0.5 * sigma**2) * T + sigma * math.sqrt(T) * Z
        )
        return ST
    return sampler


def return_from_price(S0):
    def f(ST):
        return (ST - S0) / S0
    return f


def compute_var(returns, alpha=0.95):
    return -np.percentile(returns, (1 - alpha) * 100)
