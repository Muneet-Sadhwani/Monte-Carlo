import random
import math

def gbm_path_sampler(S0, r, sigma, T, steps=50):
    dt = T / steps

    def sampler():
        prices = [S0]
        S = S0

        for _ in range(steps):
            Z = random.gauss(0, 1)
            S = S * math.exp(
                (r - 0.5 * sigma**2) * dt + sigma * math.sqrt(dt) * Z
            )
            prices.append(S)

        return prices

    return sampler


def asian_call_payoff(K):
    def payoff(price_path):
        avg_price = sum(price_path) / len(price_path)
        return max(avg_price - K, 0)

    return payoff
