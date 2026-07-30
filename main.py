import math
#import sys
#import os

#sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scenarios.pi_estimation import pi_sampler_point_in_square, f_inside_circle
from scenarios.coin_toss import coin_toss_sampler, f_if_heads
from scenarios.european_option import gbm_sampler, european_call_payoff

from engine.mc_engine import run_experiment,run_experiment_antithetic
from engine.variance_reduction import antithetic_point_in_square

from analysis.black_scholes import black_scholes_call

from engine.variance_reduction import gbm_antithetic_sampler
from engine.mc_engine import monte_carlo_antithetic

sampler_option = gbm_sampler(100, 0.05, 0.2, 1.0)
payoff = european_call_payoff(110)

mean, ci_low, ci_high, se = run_experiment(
    name="European Call Option",
    sampler=sampler_option,
    f=payoff,
    true_value=None
)

option_price = math.exp(-0.05 * 1.0) * mean

print("\n--- European Call Option (Monte Carlo) ---")
print(f"Option Price ≈ {option_price:.4f}")
print(f"Standard Error ≈ {se:.4f}")
print(f"95% CI ≈ ({ci_low:.4f}, {ci_high:.4f})")

bs_price = black_scholes_call(100, 110, 0.05, 0.2, 1.0)

print("\n--- Validation ---")
print(f"Monte Carlo Price ≈ {option_price:.4f}")
print(f"Black–Scholes Price ≈ {bs_price:.4f}")

anti_sampler = gbm_antithetic_sampler(100, 0.05, 0.2, 1.0)

mean_anti, se_anti = run_experiment_antithetic(
    name="Antithetic ",
    sampler=anti_sampler,
    f=payoff,
    true_value=None
)

price_std = math.exp(-0.05 * 1.0) * mean
price_anti = math.exp(-0.05 * 1.0) * mean_anti

print("\n--- Variance Reduction Comparison ---")
print(f"Standard MC Price ≈ {price_std:.4f}, SE ≈ {se:.5f}")
print(f"Antithetic MC Price ≈ {price_anti:.4f}, SE ≈ {se_anti:.5f}")

# run_experiment(
#     name="Pi Estimation",
#     sampler=pi_sampler_point_in_square,
#     f=f_inside_circle,
#     true_value=math.pi / 4
# )

# run_experiment_antithetic(
#     name="Pi Estimation",
#     sampler=antithetic_point_in_square,
#     f=f_inside_circle,
#     true_value=math.pi / 4
# )

# run_experiment(
#     name="Coin Toss Probability",
#     sampler=coin_toss_sampler,
#     f=f_if_heads,
#     true_value=0.5
# )