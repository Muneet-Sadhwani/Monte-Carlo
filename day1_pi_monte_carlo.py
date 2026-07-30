import random
import math
import matplotlib.pyplot as plt

def estimate_pi(n_samples):
    inside_circle = 0

    for _ in range(n_samples):
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)

        if x**2 + y**2 <= 1:
            inside_circle += 1

    pi_estimate = 4 * inside_circle / n_samples
    return pi_estimate

# Trying different sample sizes
sample_sizes = [100, 1_000, 10_000, 100_000]

for n in sample_sizes:
    estimate = estimate_pi(n)
    error = abs(estimate - math.pi)

    print(f"N = {n:>7} | pi = {estimate:.6f} | error = {error:.6f}")

estimates = []
ns = range(100, 1_00_000, 500)

for n in ns:
    estimates.append(estimate_pi(n))

plt.plot(ns, estimates, label="Monte Carlo Estimate")
plt.axhline(math.pi, color="red", linestyle="--", label="True pi")
plt.xlabel("Number of sample")
plt.ylabel("Estimated pi")
plt.legend()
plt.show()
