import math
import time
import numpy as np
from engine.mc_engine import monte_carlo_engine, monte_carlo_antithetic
from engine.variance_reduction import gbm_antithetic_sampler, control_variate_estimator
from analysis.black_scholes import black_scholes_call

from scenarios.european_option import (
    gbm_sampler,
    european_call_payoff
)

from scenarios.asian_option import (
    gbm_path_sampler,
    asian_call_payoff
)

from scenarios.var import (
    gbm_terminal_sampler,
    return_from_price,
    compute_var
)

from scenarios.correlated_assets import (
    correlated_gbm_sampler,
    portfolio_return_payoff
)

# -------------------------
# BLACK SCHOLES VALIDATION
# -------------------------

def price_european_call_with_validation(
    S0, K, r, sigma, T, n_samples,
    antithetic=False,
    control_variate=False   # 🔹 NEW
):
    start = time.time()

    result = price_european_call(
        S0, K, r, sigma, T, n_samples,
        antithetic=antithetic,
        control_variate=control_variate   # 🔹 PASS THROUGH
    )

    price = float(result["price"])
    bs_price = black_scholes_call(S0, K, r, sigma, T)

    runtime_ms = (time.time() - start) * 1000

    return {
        "price": price,
        "standard_error": result["standard_error"],
        "ci_low": result["ci_low"],
        "ci_high": result["ci_high"],
        "cv_price": result["cv_price"],                   # 🔹 NEW
        "cv_standard_error": result["cv_standard_error"], # 🔹 NEW
        "black_scholes": bs_price,
        "absolute_error": abs(price - bs_price),
        "runtime_ms": runtime_ms
    }


# -------------------------
# CORRELATED PORTFOLIO
# -------------------------
def correlated_portfolio_var(
    S0_1, S0_2,
    sigma_1, sigma_2,
    w1, w2,
    r, T,
    rho,
    n_samples,
    alpha=0.95
):
    sampler = correlated_gbm_sampler(
        S0_1, S0_2,
        r, sigma_1, sigma_2,
        T, rho
    )

    payoff = portfolio_return_payoff(
        w1, w2, S0_1, S0_2
    )

    returns = [payoff(sampler()) for _ in range(n_samples)]
    var_value = -np.percentile(returns, (1 - alpha) * 100)
    print(var_value)

    return {
        "VaR": var_value,
        "confidence": alpha,
        "correlation": rho,
        "samples": n_samples
    }

# -------------------------
# EUROPEAN CALL
# -------------------------
def price_european_call(
    S0, K, r, sigma, T, n_samples,
    antithetic=False,
    control_variate=False   # 🔹 NEW
):
    start = time.perf_counter()

    payoff_fn = european_call_payoff(K)

    payoffs = []
    controls = []   # 🔹 NEW (for control variate)

    if antithetic:
        sampler = gbm_antithetic_sampler(S0, r, sigma, T)
        mean, _, se = monte_carlo_antithetic(
            payoff_fn, sampler, n_samples
        )
        ci_low = ci_high = mean
    else:
        sampler = gbm_sampler(S0, r, sigma, T)

        for _ in range(n_samples):
            ST = sampler()
            payoffs.append(payoff_fn(ST))
            controls.append(ST)   # 🔹 store control

        mean = sum(payoffs) / n_samples
        variance = sum((p - mean) ** 2 for p in payoffs) / (n_samples - 1)
        se = (variance ** 0.5) / (n_samples ** 0.5)

        ci_low = mean - 1.96 * se
        ci_high = mean + 1.96 * se

        # 🔹 CONTROL VARIATE ADJUSTMENT
        cv_mean = None
        cv_se = None

        if control_variate:
            control_mean = S0 * math.exp(r * T)

            pay = np.array(payoffs)
            ctrl = np.array(controls)

            cov = np.cov(pay, ctrl, ddof=1)
            c = cov[0, 1] / cov[1, 1]

            adjusted = pay + c * (control_mean - ctrl)

            cv_mean = adjusted.mean()
            cv_se = adjusted.std(ddof=1) / (n_samples ** 0.5)

    discount = math.exp(-r * T)

    runtime_ms = (time.perf_counter() - start) * 1000

    return {
        "price": discount * mean,
        "standard_error": se,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "cv_price": discount * cv_mean if control_variate else None,   # 🔹 NEW
        "cv_standard_error": cv_se if control_variate else None,        # 🔹 NEW
        "runtime_ms": runtime_ms
    }

# -------------------------
# ASIAN CALL
# -------------------------
def price_asian_call(
    S0, K, r, sigma, T, n_samples, steps=50
):
    start = time.perf_counter()

    sampler = gbm_path_sampler(S0, r, sigma, T, steps)
    payoff = asian_call_payoff(K)

    mean, _, se, (ci_low, ci_high) = monte_carlo_engine(
        payoff, sampler, n_samples
    )

    price = math.exp(-r * T) * mean
    runtime_ms = (time.perf_counter() - start) * 1000

    return {
        "price": price,
        "standard_error": se,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "runtime_ms": runtime_ms
    }


# -------------------------
# VALUE AT RISK
# -------------------------
def compute_var_simulation(
    S0, r, sigma, T, n_samples, alpha=0.95
):
    start = time.perf_counter()

    sampler = gbm_terminal_sampler(S0, r, sigma, T)
    f = return_from_price(S0)

    returns = [f(sampler()) for _ in range(n_samples)]
    var_value = compute_var(returns, alpha)

    runtime_ms = (time.perf_counter() - start) * 1000

    return {
        "VaR": var_value,
        "confidence": alpha,
        "runtime_ms": runtime_ms
    }


# -------------------------
# DISPATCHER (SINGLE ENTRY)
# -------------------------
def run_simulation(scenario: str, params: dict):
    print("SCENARIO:", scenario)
    print("PARAMS RECEIVED:", params)

    if scenario == "european_call":
        return price_european_call_with_validation(**params)

    if scenario == "asian_call":
        return price_asian_call(**params)

    if scenario == "var":
        return compute_var_simulation(**params)
    
    if scenario == "correlated_var":
        return correlated_portfolio_var(
            S0_1=params["S0_1"],
            S0_2=params["S0_2"],
            sigma_1=params["sigma_1"],
            sigma_2=params["sigma_2"],
            w1=params["w1"],
            w2=params["w2"],
            r=params["r"],
            T=params["T"],
            rho=params["rho"],
            n_samples=params["n_samples"]
        )

    raise ValueError("Unknown scenario")
