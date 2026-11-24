"""
NSGA-II direct policy search (Quinn et al., 2017): the lever is a closed-loop rule
u_t = f(X_t) with 2 radial basis functions (6 parameters), not 25 separate annual values.
Same 100 SYNTHETIC rainfall replicates for every evaluation. 3 seeds; archive hypervolume
recorded every 50 generations; result checked against a brute-force policy family.
"""
import sys, json
import numpy as np
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.indicators.hv import HV
from pymoo.core.callback import Callback
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting
import powai_model as pm

T = 25
RAIN = pm.rain_replicates(R=100, T=T, seed=2026)
RULE = sys.argv[2] if len(sys.argv) > 2 else 'two_level'
if RULE == 'rbf':
    pm.RULE = pm.dps_rule
    NB = pm.N_RBF
    XL = np.r_[np.zeros(NB), np.full(NB, 0.05), np.zeros(NB)]
    XU = np.r_[np.full(NB, 2.0), np.full(NB, 2.0), np.full(NB, 1.5)]
else:   # two-level rule: u_low, u_high, X_switch (t)
    XL = np.array([0.0, 0.0, 0.5]); XU = np.array([1.0, 1.0, 5.0])


class LakeDPS(Problem):
    def __init__(self):
        super().__init__(n_var=len(XL), n_obj=4, xl=XL, xu=XU)

    def _evaluate(self, x, out, *args, **kwargs):
        X, U = pm.simulate_dps(x, RAIN)
        c, tp, rel, ine = pm.objectives_dps(X, U)
        out['F'] = np.column_stack([c, tp, -rel, -ine])


LO = np.array([0, 0, -1, -1.0]); HI = np.array([110, 1.0, 0, 0.0])
hv = HV(ref_point=np.ones(4) * 1.01)


class Track(Callback):
    def __init__(self):
        super().__init__(); self.hv = []; self.F = None; self.X = None

    def notify(self, algorithm):
        F = algorithm.pop.get('F'); X = algorithm.pop.get('X')
        if self.F is not None:
            F = np.vstack([self.F, F]); X = np.vstack([self.X, X])
        F, idx = np.unique(np.round(F, 9), axis=0, return_index=True); X = X[idx]
        front = NonDominatedSorting().do(F, only_non_dominated_front=True)
        self.F, self.X = F[front], X[front]
        if algorithm.n_gen % 50 == 0 or algorithm.n_gen == 1:
            ok = self.F[:, 2] <= -1 + 1e-9
            self.hv.append((int(algorithm.n_gen), float(hv((self.F - LO) / (HI - LO))),
                            float(self.F[ok, 0].min()) if ok.any() else None))


if __name__ == '__main__':
    n_gen = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    allF, allX, traces = [], [], {}
    for seed in (1, 2, 3, 4, 5):
        cb = Track()
        minimize(LakeDPS(), NSGA2(pop_size=100), ('n_gen', n_gen), seed=seed, callback=cb)
        F = cb.F.copy(); F[:, 2:] *= -1
        traces[seed] = cb.hv
        print(f'seed {seed}: archive={len(F)}, trace (gen, HV, min cost at 100% rel) = {cb.hv}', flush=True)
        allF.append(F); allX.append(cb.X)
    F = np.vstack(allF); Xd = np.vstack(allX)
    G = F.copy(); G[:, 2:] *= -1
    front = NonDominatedSorting().do(G, only_non_dominated_front=True)
    np.savez(f'../results/pareto_{RULE}.npz', F=F[front], X=Xd[front])
    json.dump(traces, open(f'../results/convergence_{RULE}.json', 'w'), indent=1)
    print('merged nondominated:', len(front))
