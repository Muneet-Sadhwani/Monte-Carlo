import numpy as np
import math

def correlated_gbm_sampler(
    S0_1, S0_2,
    r, sigma_1, sigma_2,
    T, rho
):
    """
    Generates correlated terminal prices for two assets.
    """

    # Correlation matrix
    corr = np.array([
        [1.0, rho],
        [rho, 1.0]
    ])

    # Cholesky decomposition
    L = np.linalg.cholesky(corr)

    def sampler():
        Z = np.random.normal(size=2)
        correlated_Z = L @ Z

        ST1 = S0_1 * math.exp(
            (r - 0.5 * sigma_1**2) * T
            + sigma_1 * math.sqrt(T) * correlated_Z[0]
        )

        ST2 = S0_2 * math.exp(
            (r - 0.5 * sigma_2**2) * T
            + sigma_2 * math.sqrt(T) * correlated_Z[1]
        )

        return ST1, ST2

    return sampler

def portfolio_return_payoff(w1, w2, S0_1, S0_2):
    """
    Computes portfolio return from two assets.
    """

    def payoff(ST):
        ST1, ST2 = ST

        portfolio_initial = w1 * S0_1 + w2 * S0_2
        portfolio_final = w1 * ST1 + w2 * ST2

        return (portfolio_final - portfolio_initial) / portfolio_initial

    return payoff
