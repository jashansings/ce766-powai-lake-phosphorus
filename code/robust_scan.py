"""Re-evaluate candidate 100%-reliable policies (nominal) across 500 Latin-hypercube
parameter sets, recalibrating the settling rate to the reported lake TP each time.
Simple re-evaluation only (no PRIM / scenario discovery)."""
import json, numpy as np
from scipy.stats import qmc
import powai_model as pm
d = np.load('../results/pareto_two_level.npz'); F, X = d['F'], d['X']
RAIN = pm.rain_replicates(R=50, T=25, seed=777)    # fresh replicates, not used in optimisation
lo = np.array([4.0, 1.0, 1.0, 6.0, 0.6]); hi = np.array([8.0, 15.0, 3.0, 10.0, 1.3])
S = qmc.scale(qmc.LatinHypercube(d=5, seed=11).random(500), lo, hi)
ok = (F[:, 2] >= 1 - 1e-9) & (F[:, 3] >= 0.9)
cands = {}
for tp in np.round(np.arange(0.19, 0.049, -0.01), 2):
    s = ok & (F[:, 1] <= tp + 1e-9)
    if s.any():
        i = np.where(s)[0][np.argmin(F[s, 0])]
        cands[f'{tp:.2f}'] = i
named = {'No action': np.array([0, 0, 99.0]), '8 MLD STP': np.array([0.36, 0.36, 99.0]), 'Max removal u=1': np.array([1.0, 1.0, 99.0])}
thetas = {**{k: X[i] for k, i in cands.items()}, **named}
res = {}
wb = pm.water_budget(pm.RAIN_MEAN); rho = wb['outflow'] / pm.V
for name, th in thetas.items():
    rels, tps = [], []
    for c_sew, rel_mg, m, q, tp_obs in S:
        x_obs = tp_obs * pm.V / 1e6
        load = pm.Q_SEW * c_sew / 1e6 + wb['runoff'] * pm.C_RUN / 1e6 + pm.r_max(rel_mg) * pm.hill(x_obs, m, q)
        sigma = load / x_obs - rho
        Xs, U = pm.simulate_dps(th, RAIN, X0=x_obs, sigma=sigma, rel_mg=rel_mg, c_sew=c_sew, m=m, q=q)
        rels.append(float((Xs < pm.X_CRIT).mean())); tps.append(float(Xs.mean() * 1e6 / pm.V))
    rels = np.array(rels)
    nomF = F[cands[name]] if name in cands else None
    res[name] = dict(theta=[round(float(v), 3) for v in th],
                     nominal=None if nomF is None else dict(cost=round(float(nomF[0]), 2), mean_tp=round(float(nomF[1]), 3),
                                                            rel=round(float(nomF[2]), 3), inertia=round(float(nomF[3]), 3)),
                     share_rel_ge_095=round(float((rels >= 0.95).mean()), 3),
                     share_rel_eq_1=round(float((rels >= 1 - 1e-9).mean()), 3),
                     median_rel=round(float(np.median(rels)), 3), p10_rel=round(float(np.percentile(rels, 10)), 3))
    print(name, res[name])
json.dump(dict(ranges=dict(c_sew_mgL=[4, 8], release_mg_m2_d=[1, 15], m_t=[1, 3], q=[6, 10], tp_obs_mgL=[0.6, 1.3]),
               results=res), open('../results/robust_scan.json', 'w'), indent=1)
