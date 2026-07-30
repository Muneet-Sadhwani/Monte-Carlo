import random
import math

def gbm_sampler(S0, r, sigma, T):

    def sampler():
        Z=random.gauss(0,1)
        ST=S0*math.exp(
            (r - 0.5 * sigma**2) * T + sigma * math.sqrt(T) * Z           
        )
        return ST

    return sampler

def european_call_payoff(K):

    def payoff(ST):
        return max(ST - K, 0)
    
    return payoff