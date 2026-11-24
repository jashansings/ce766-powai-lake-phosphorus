"""
Brute-force benchmark for the optimizer: a simple two-level closed-loop rule
u = u_hi if X_t > X_s else u_lo, evaluated on a full grid, plus the open-loop family
(u in year 1 = u1, constant c afterwards). Reports the cheapest policy reaching each
reliability target, to compare with the NSGA-II Pareto set.
"""
import json, numpy as np, powai_model as pm
RAIN = pm.rain_replicates(R=100, T=25, seed=2026)
P = RAIN / 1000.0; q_run = pm.RUNOFF_COEF * P * pm.A_CATCH
rho = (q_run + P * pm.A_LAKE + pm.Q_SEW - pm.EVAP * pm.A_LAKE) / pm.V
Y = q_run * pm.C_RUN / 1e6; k = rho + pm.SIGMA; ek = np.exp(-k)
grid = [(lo, hi, xs) for lo in np.round(np.arange(0.5, 1.001, 0.01), 2)
        for hi in np.round(np.arange(0.8, 1.001, 0.01), 2) for xs in (1.0, 1.5, 2.0, 3.0, 4.0)]
G = np.array(grid); N = len(G)
X = np.full((N, 100), pm.X_OBS); Xo = np.empty((N, 100, 25)); Uo = np.empty_like(Xo)
for t in range(25):
    u = np.where(X > G[:, 2:3], G[:, 1:2], G[:, 0:1])
    L = (1 - u) * pm.A0 + Y[None, :, t] + pm.r_max() * pm.hill(X)
    X = X * ek[None, :, t] + L / k[None, :, t] * (1 - ek[None, :, t])
    Xo[:, :, t] = X; Uo[:, :, t] = u
cost, tp, rel, ine = pm.objectives_dps(Xo, Uo)
fam_ol = json.load(open('../results/family_check.json'))
FR = np.load('../results/pareto_rbf.npz')['F']; F = np.load('../results/pareto_two_level.npz')['F']
out = {}
for target in (0.90, 0.95, 0.99, 1.0):
    ok = rel >= target - 1e-9; i = np.argmin(np.where(ok, cost, np.inf))
    okn = F[:, 2] >= target - 1e-9
    out[str(target)] = dict(two_level_rule_min_cost=round(float(cost[i]), 2), rule=[float(v) for v in G[i]],
                            open_loop_family_min_cost=fam_ol[str(target) if str(target) in fam_ol else '1.0']['family_min_cost'],
                            nsga_two_level_min_cost=round(float(F[okn, 0].min()), 2) if okn.any() else None,
                            nsga_rbf_min_cost=round(float(FR[FR[:, 2] >= target - 1e-9, 0].min()), 2))
json.dump(out, open('../results/family_check_dps.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
