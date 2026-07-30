import random
import math

def antithetic_point_in_square():
    x = random.uniform(0,1)
    y = random.uniform(0,1)

    point_1 = (x, y)
    point_2 = (1-x, 1-y)

    return point_1, point_2 

def gbm_antithetic_sampler(S0, r, sigma, T):
    def sampler():
        Z = random.gauss(0, 1)

        ST1 = S0 * math.exp(
            (r - 0.5 * sigma**2) * T + sigma * math.sqrt(T) * Z
        )

        ST2 = S0 * math.exp(
            (r - 0.5 * sigma**2) * T - sigma * math.sqrt(T) * Z
        )

        return ST1, ST2

    return sampler

import numpy as np

def control_variate_estimator(payoffs, controls, control_mean):
    payoffs = np.array(payoffs)
    controls = np.array(controls)

    cov = np.cov(payoffs, controls, ddof=1)
    c = cov[0, 1] / cov[1, 1]

    adjusted = payoffs + c * (control_mean - controls)

    mean = adjusted.mean()
    se = adjusted.std(ddof=1) / np.sqrt(len(adjusted))

    return mean, se
