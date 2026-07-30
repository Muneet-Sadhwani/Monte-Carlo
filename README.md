# Monte Carlo Simulation Engine

This project implements a reusable Monte Carlo simulation engine
with multiple scenarios including probability estimation and
financial applications.

The engine separates:
- Random scenario generation (sampler)
- Outcome evaluation (payoff / indicator)
- Aggregation & convergence analysis

Monte Carlo prices were validated against the analytical Black–Scholes formula and converged within statistical error bounds