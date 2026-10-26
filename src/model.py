"""
CE 766: Watershed Management - Course Project
Powai Lake Phosphorus Mass Balance Model
Reformulating the Lake Problem under Deep Uncertainty (2017–2025)
Author: Jashanpreet Singh (23B0985)
"""

import math
import random
import csv

class PowaiLakeModel:
    def __init__(
        self,
        b=0.48,           # Loss rate (yr^-1) through permanent burial and flushing
        r=12.0,           # Maximum sediment recycling rate (tons/yr)
        m=2.4,            # Half-saturation constant (tons)
        q=8.0,            # Hill coefficient / recycling steepness exponent
        mu_y=0.704,       # Mean of log natural inflow (ln(tons/yr)) -> exp(0.704) ~ 2.02 t/yr
        sigma_y=0.35,     # Std dev of log natural inflow
        X_crit=1.0,       # Critical eutrophication threshold (tons TP, ~0.10 mg/L)
        volume_m3=5.25e6, # Effective lake volume (m^3)
        area_km2=2.10     # Water spread area (km^2)
    ):
        self.b = b
        self.r = r
        self.m = m
        self.q = q
        self.mu_y = mu_y
        self.sigma_y = sigma_y
        self.X_crit = X_crit
        self.volume_m3 = volume_m3
        self.area_km2 = area_km2

    def sediment_recycling(self, X):
        """Internal sediment phosphorus recycling term: r * X^q / (m^q + X^q)."""
        if X <= 0:
            return 0.0
        # Prevent numerical overflow for high exponent q
        if X / self.m > 3.0:
            return self.r
        X_q = X ** self.q
        m_q = self.m ** self.q
        return self.r * (X_q / (m_q + X_q))

    def step(self, X_t, a_t, Y_t):
        """Compute phosphorus stock for next year X_{t+1}."""
        rec = self.sediment_recycling(X_t)
        X_next = X_t + a_t + Y_t - self.b * X_t + rec
        return max(0.01, X_next)

    def sample_natural_inflow(self):
        """Sample annual natural runoff phosphorus load Y_t from lognormal distribution."""
        z = random.gauss(0, 1)
        return math.exp(self.mu_y + self.sigma_y * z)

    def simulate(self, X0, a_series, n_replicates=100, seed=42):
        """
        Simulate lake phosphorus trajectory over a given planning horizon.
        a_series: list of anthropogenic inputs for each year.
        """
        random.seed(seed)
        horizon = len(a_series)
        replicates = []

        for rep in range(n_replicates):
            traj = [X0]
            X = X0
            for t in range(horizon):
                Y_t = self.sample_natural_inflow()
                X = self.step(X, a_series[t], Y_t)
                traj.append(X)
            replicates.append(traj)

        return replicates

def run_baseline_simulation():
    """Run 25-year baseline simulation (2026-2050) without interventions (a = 18.0 t/yr)."""
    model = PowaiLakeModel()
    horizon = 25
    a_baseline = [18.0] * horizon
    X0 = 12.5 # Initial phosphorus stock in 2025 (tons TP, ~2.38 mg/L)
    n_reps = 100

    replicates = model.simulate(X0, a_baseline, n_replicates=n_reps, seed=42)

    # Compute yearly summary statistics
    years = list(range(2025, 2025 + horizon + 1))
    summary = []
    for t_idx, yr in enumerate(years):
        vals = [replicates[rep][t_idx] for rep in range(n_reps)]
        vals.sort()
        mean_val = sum(vals) / len(vals)
        std_val = math.sqrt(sum((v - mean_val) ** 2 for v in vals) / (len(vals) - 1))
        p10 = vals[int(0.10 * len(vals))]
        p50 = vals[int(0.50 * len(vals))]
        p90 = vals[int(0.90 * len(vals))]
        exceed_pct = sum(1 for v in vals if v > model.X_crit) / len(vals) * 100.0
        summary.append({
            'year': yr,
            'mean': mean_val,
            'std': std_val,
            'p10': p10,
            'median': p50,
            'p90': p90,
            'exceedance_pct': exceed_pct
        })

    # Save to CSV
    csv_path = 'data/baseline_simulation_results.csv'
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['year', 'mean', 'std', 'p10', 'median', 'p90', 'exceedance_pct'])
        writer.writeheader()
        for row in summary:
            writer.writerow(row)

    print(f"Baseline simulation completed: {n_reps} replicates over {horizon} years.")
    print(f"Year 2025: X = {summary[0]['mean']:.2f} t")
    print(f"Year 2030: X = {summary[5]['mean']:.2f} t (p10: {summary[5]['p10']:.2f}, p90: {summary[5]['p90']:.2f})")
    print(f"Year 2050: X = {summary[-1]['mean']:.2f} t (p10: {summary[-1]['p10']:.2f}, p90: {summary[-1]['p90']:.2f})")
    print(f"Eutrophication exceedance: {summary[-1]['exceedance_pct']:.1f}%")
    return model, summary, replicates

if __name__ == '__main__':
    run_baseline_simulation()
