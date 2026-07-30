import math
import matplotlib.pyplot as plt

def monte_carlo_engine(f, sampler, n_samples):
    values = []

    for _ in range(n_samples):
        x = sampler()
        values.append(f(x))

    mean = sum(values) / n_samples
    variance = sum((v - mean) ** 2 for v in values) / (n_samples - 1)
    std_error = math.sqrt(variance / n_samples)

    ci_low = mean - 1.96 * std_error
    ci_high = mean + 1.96 * std_error

    return mean, variance, std_error, (ci_low, ci_high)

def monte_carlo_antithetic(f, sampler, n_samples):
    values = []

    for _ in range(n_samples):
        x1, x2 = sampler()
        v1 = f(x1)
        v2 = f(x2)
        values.append((v1+v2) / 2)

    mean = sum(values) / n_samples
    variance = sum((v - mean) ** 2 for v in values) / (n_samples - 1)
    std_error = math.sqrt(variance / n_samples)

    return mean, variance, std_error

def run_convergence(f, sampler, checkpoints):
    results = []

    for n in checkpoints:
        mean, var, se, (ci_low, ci_high) = monte_carlo_engine(f, sampler, n)
        results.append((n, mean, se))

    return results

def run_experiment(name, sampler, f, true_value=None):
    print(f"\n--- {name} ---")

    sample_sizes = [100, 500, 1000, 5000, 10_000, 100_000]
    estimates = []
    ns = []

    for n in sample_sizes:
        mean, var, se, (low, high)= monte_carlo_engine(f, sampler, n)
        estimates.append(mean)
        ns.append(n)

        print(f"N = {n:6d} | Estimate = {mean:.5f} | SE = {se:.5f}")

    plt.figure(figsize=(8, 4))
    plt.plot(ns, estimates, marker="o", label="Monte Carlo Estimate")

    if true_value is not None:
        plt.axhline(true_value, color="red", linestyle="--", label="True Value")

    plt.xlabel("Number of Samples")
    plt.ylabel("Estimate")
    plt.title(f"Convergence: {name}")
    plt.legend()
    plt.grid(True)
    plt.show()

    return mean, low, high, se

def run_experiment_antithetic(name, sampler, f, true_value=None):
    print(f"\n--- {name} ---")

    sample_sizes = [100, 500, 1000, 5000, 10_000, 100_000]
    estimates = []
    ns = []

    for n in sample_sizes:
        mean, var, se = monte_carlo_antithetic(f, sampler, n)
        estimates.append(mean)
        ns.append(n)

        print(f"N = {n:6d} | Estimate = {mean:.5f} | SE = {se:.5f}")

    plt.figure(figsize=(8, 4))
    plt.plot(ns, estimates, marker="o", label="Monte Carlo Estimate")

    if true_value is not None:
        plt.axhline(true_value, color="red", linestyle="--", label="True Value")

    plt.xlabel("Number of Samples")
    plt.ylabel("Estimate")
    plt.title(f"Convergence: {name}")
    plt.legend()
    plt.grid(True)
    plt.show()

    return mean, se