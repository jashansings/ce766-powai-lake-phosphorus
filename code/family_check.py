"""
Convergence check independent of NSGA-II: exhaustively evaluate the 2-parameter family
"u in year 1 = u1, u in years 2-25 = c" on a 101 x 101 grid and report, for each target
reliability, the cheapest policy. If NSGA-II has converged, its Pareto set should be at
least as good as this family everywhere.
"""
import json
import numpy as np
import powai_model as pm

RAIN = pm.rain_replicates(R=100, T=25, seed=2026)
g = np.linspace(0, 1, 101)
U = np.array([[u1] + [c] * 24 for u1 in g for c in g])
X = pm.simulate(U, RAIN)
cost, tp, rel, ine = pm.objectives(U, X)
d = np.load('../results/pareto_openloop.npz'); F = d['F']
out = {}
for target in (0.90, 0.95, 0.96, 0.99, 1.0):
    ok = rel >= target - 1e-9
    i = np.argmin(np.where(ok, cost, np.inf))
    okn = F[:, 2] >= target - 1e-9
    out[str(target)] = dict(family_min_cost=round(float(cost[i]), 2), family_u1=float(U[i, 0]),
                            family_c=float(U[i, 1]), family_tp=round(float(tp[i]), 3),
                            nsga_min_cost=round(float(F[okn, 0].min()), 2) if okn.any() else None)
json.dump(out, open('../results/family_check.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
