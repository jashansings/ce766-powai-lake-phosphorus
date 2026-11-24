"""
NSGA-II search over 25 annual sewage-P removal fractions u_t (2026-2050), 4 objectives:
min PV cost, min mean TP, max reliability (TP < X_CRIT), max inertia.
The same 100 SYNTHETIC rainfall replicates are used for every evaluation (common random
numbers), so the objective function is deterministic. Three random seeds are run and the
hypervolume is tracked each generation to check convergence.
"""
import json, sys
import numpy as np
from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.optimize import minimize
from pymoo.indicators.hv import HV
from pymoo.core.callback import Callback
import powai_model as pm

T = 25
RAIN = pm.rain_replicates(R=100, T=T, seed=2026)


class Lake(Problem):
    def __init__(self):
        super().__init__(n_var=T, n_obj=4, xl=0.0, xu=1.0)

    def _evaluate(self, x, out, *args, **kwargs):
        X = pm.simulate(x, RAIN)
        c, tp, rel, ine = pm.objectives(x, X)
        out['F'] = np.column_stack([c, tp, -rel, -ine])


# normalisation for hypervolume: cost 0..110, tp 0..1, -rel -1..0, -ine -1..0
LO = np.array([0, 0, -1, -1.0]); HI = np.array([110, 1.0, 0, 0.0])
hv = HV(ref_point=np.ones(4) * 1.01)


from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting


class Track(Callback):
    """Keeps an archive of every non-dominated solution found so far (NSGA-II's
    population can lose good points with 4 objectives) and records its hypervolume."""
    def __init__(self):
        super().__init__(); self.hv = []; self.F = None; self.X = None

    def notify(self, algorithm):
        F = algorithm.pop.get('F'); X = algorithm.pop.get('X')
        if self.F is not None:
            F = np.vstack([self.F, F]); X = np.vstack([self.X, X])
        F, idx = np.unique(np.round(F, 9), axis=0, return_index=True); X = X[idx]
        front = NonDominatedSorting().do(F, only_non_dominated_front=True)
        self.F, self.X = F[front], X[front]
        if algorithm.n_gen % 50 == 0:
            self.hv.append((algorithm.n_gen, float(hv((self.F - LO) / (HI - LO)))))


SEEDED = False


def seed_population(n, rng):
    """Random population plus a few constant policies so the corners are reachable."""
    X = rng.random((n, T))
    if not SEEDED:
        consts = np.linspace(0, 1, 11)
    else:
        consts = np.linspace(0, 1, 101)   # informed start: every constant policy 0.00..1.00
    X[:len(consts)] = consts[:, None]
    return X


if __name__ == '__main__':
    n_gen = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    globals()['SEEDED'] = len(sys.argv) > 2 and sys.argv[2] == 'seeded'
    tag = sys.argv[3] if len(sys.argv) > 3 else 'pareto_openloop'
    results = {}
    allF, allX = [], []
    for seed in (1, 2, 3):
        rng = np.random.default_rng(seed)
        algo = NSGA2(pop_size=200, sampling=seed_population(200, rng))
        cb = Track()
        res = minimize(Lake(), algo, ('n_gen', n_gen), seed=seed, callback=cb, verbose=False)
        F = cb.F.copy(); F[:, 2:] *= -1
        ok = F[:, 2] >= 1 - 1e-9
        print(f'seed {seed}: gens={n_gen}, seeded={globals()["SEEDED"]}, nondominated={len(F)}, max rel={F[:,2].max():.3f}, '
              f'min cost at rel=1: {F[ok,0].min():.2f}, HV trace={[round(h,4) for _,h in cb.hv[::4]]}', flush=True)
        results[seed] = cb.hv
        allF.append(F); allX.append(cb.X)
    F = np.vstack(allF); Xd = np.vstack(allX)
    # merge seeds: keep non-dominated across all
    G = F.copy(); G[:, 2:] *= -1
    nd = np.ones(len(G), bool)
    for i in range(len(G)):
        if nd[i]:
            dom = np.all(G <= G[i], axis=1) & np.any(G < G[i], axis=1)
            if dom.any():
                nd[i] = False
    np.savez(f'../results/{tag}.npz', F=F[nd], X=Xd[nd], hv1=results[1], hv2=results[2], hv3=results[3])
    print('merged nondominated:', nd.sum())
