"""Final summary numbers + the two report figures (PNG 300 dpi + PDF)."""
import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import powai_model as pm

plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.edgecolor': '#52514e', 'axes.labelcolor': '#0b0b0b', 'xtick.color': '#52514e',
                     'ytick.color': '#52514e', 'font.family': 'DejaVu Sans'})
BLUE, ORANGE, AQUA, GRAY, INK, MUTED = '#2a78d6', '#eb6834', '#1baf7a', '#8a8985', '#0b0b0b', '#52514e'
OUT = '../figures/'
import os; os.makedirs(OUT, exist_ok=True)

d = np.load('../results/pareto_two_level.npz'); F, TH = d['F'], d['X']
rob = json.load(open('../results/robust_scan.json'))['results']
RAIN = pm.rain_replicates(R=100, T=25, seed=2026)
RAIN_TEST = pm.rain_replicates(R=100, T=25, seed=777)

policies = {
    'No action': np.array([0.0, 0.0, 99.0]),
    'Planned 8 MLD STP': np.array([0.36, 0.36, 99.0]),
    'Cheapest 100%-reliable': np.array(rob['0.19']['theta']),
    'Compromise': np.array(rob['0.14']['theta']),
    'Activist (max removal)': np.array([1.0, 1.0, 99.0]),
}
summ = {}
for k, th in policies.items():
    row = {'theta': [float(v) for v in th]}
    for tag, rain in (('optimisation_replicates', RAIN), ('fresh_replicates', RAIN_TEST)):
        X, U = pm.simulate_dps(th, rain)
        c, tp, rel, ine = pm.objectives_dps(X, U)
        row[tag] = dict(cost_crore=round(float(c[0]), 1), mean_tp=round(float(tp[0]), 3),
                        reliability=round(float(rel[0]), 3), inertia=round(float(ine[0]), 3),
                        tp_2050_median=round(float(np.median(X[0, :, -1]) * 1e6 / pm.V), 3),
                        mean_load_t=round(float(((1 - U) * pm.A0).mean()), 2))
    summ[k] = row
json.dump(summ, open('../results/final_policies.json', 'w'), indent=1)
print(json.dumps(summ, indent=1))

# ---------------- Figure 1: water and phosphorus budgets ----------------
wb = pm.water_budget(pm.RAIN_MEAN)
rho = wb['outflow'] / pm.V
Xo = pm.X_OBS
P_in = {'Untreated sewage\n(18 MLD × 5 mg/L)': pm.A0, 'Catchment runoff': wb['runoff'] * pm.C_RUN / 1e6,
        'Sediment release\n(internal load)': pm.r_max() * float(pm.hill(Xo))}
P_out = {'Outflow over weir\n(ρ·X)': rho * Xo, 'Net settling to\nsediment (σ·X)': pm.SIGMA * Xo}
W_in = {'Catchment runoff': wb['runoff'] / 1e6, 'Rain on lake': wb['direct_rain'] / 1e6, 'Sewage': wb['sewage'] / 1e6}
W_out = {'Evaporation': wb['evaporation'] / 1e6, 'Outflow over weir': wb['outflow'] / 1e6}

fig, axs = plt.subplots(1, 2, figsize=(11, 4.4))
for ax, ins, outs, unit, title in ((axs[0], W_in, W_out, 'Annual volume (million m³/yr)', '(a) Water budget, mean year (2,250 mm rain)'),
                                   (axs[1], P_in, P_out, 'Annual phosphorus flux (t P/yr)', '(b) Phosphorus budget at calibration (TP 0.93 mg/L)')):
    labels = list(ins) + list(outs); vals = list(ins.values()) + list(outs.values())
    cols = [BLUE] * len(ins) + [ORANGE] * len(outs)
    y = np.arange(len(labels))[::-1]
    ax.barh(y, vals, color=cols, height=0.62, edgecolor='white', linewidth=2)
    for yi, v in zip(y, vals):
        ax.text(v + max(vals) * 0.015, yi, f'{v:.1f}', va='center', color=INK, fontsize=9)
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel(unit); ax.set_title(title, fontsize=10.5, loc='left', color=INK)
    ax.set_xlim(0, max(vals) * 1.15)
    ax.grid(axis='x', color='#e4e3df', linewidth=0.6); ax.set_axisbelow(True)
    ax.text(0.98, 0.04, f'In: {sum(ins.values()):.1f}   Out: {sum(outs.values()):.1f}', transform=ax.transAxes,
            ha='right', fontsize=9, color=MUTED)
from matplotlib.patches import Patch
fig.legend(handles=[Patch(color=BLUE, label='Input'), Patch(color=ORANGE, label='Output')], loc='upper right',
           ncol=2, frameon=False, fontsize=9)
fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig(OUT + 'figure1_budgets.png', dpi=300); fig.savefig(OUT + 'figure1_budgets.pdf'); plt.close(fig)

# ---------------- Figure 2: trade-off and trajectories ----------------
fig, axs = plt.subplots(1, 2, figsize=(11, 4.4))
ax = axs[0]
keep = F[:, 2] >= 0.95
ax.scatter(F[~keep, 0], F[~keep, 1], s=4, color='#d6d5d0', label='Pareto set, reliability < 95%', rasterized=True)
sc = ax.scatter(F[keep, 0], F[keep, 1], s=5, color='#9cc0ec', label='Pareto set, reliability ≥ 95%', rasterized=True)
ax.axhline(pm.X_CRIT * 1e6 / pm.V, color=MUTED, ls='--', lw=1)
ax.text(2, pm.X_CRIT * 1e6 / pm.V + 0.015, 'Threshold 0.19 mg/L (1 t P)', color=MUTED, fontsize=8.5)
marks = {'No action': GRAY, 'Planned 8 MLD STP': ORANGE, 'Cheapest 100%-reliable': '#6250d6',
         'Compromise': BLUE, 'Activist (max removal)': AQUA}
pos = {'No action': (6, 0.87), 'Planned 8 MLD STP': (38, 0.70), 'Cheapest 100%-reliable': (30, 0.30),
       'Compromise': (42, 0.13), 'Activist (max removal)': (58, 0.03)}
for k, col in marks.items():
    r = summ[k]['optimisation_replicates']
    ax.scatter(r['cost_crore'], r['mean_tp'], s=60, color=col, edgecolor='white', linewidth=1.5, zorder=5)
    ax.annotate(f"{k}\nrel. {r['reliability']*100:.0f}%", (r['cost_crore'], r['mean_tp']),
                xytext=pos[k], fontsize=8, color=INK,
                arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.6))
ax.set_xlabel('Present value of P-control cost, 2026–2050 (₹ crore)')
ax.set_ylabel('Mean lake TP, 2026–2050 (mg/L)')
ax.set_title('(a) Trade-off between cost and lake phosphorus', fontsize=10.5, loc='left')
ax.set_ylim(0, 1.05); ax.set_xlim(-2, 115)
ax.legend(loc='upper right', fontsize=8, frameon=False, markerscale=3)
ax.grid(color='#eeede9', linewidth=0.6); ax.set_axisbelow(True)

ax = axs[1]
years = np.arange(2026, 2051)
for k in ('No action', 'Planned 8 MLD STP', 'Compromise', 'Activist (max removal)'):
    X, U = pm.simulate_dps(policies[k], RAIN_TEST)
    C = X[0] * 1e6 / pm.V
    med = np.median(C, axis=0); p10, p90 = np.percentile(C, [10, 90], axis=0)
    ax.fill_between(np.r_[2025, years], np.r_[pm.TP_OBS, p10], np.r_[pm.TP_OBS, p90], color=marks[k], alpha=0.18, lw=0)
    ax.plot(np.r_[2025, years], np.r_[pm.TP_OBS, med], color=marks[k], lw=2, label=k)
ax.axhline(pm.X_CRIT * 1e6 / pm.V, color=MUTED, ls='--', lw=1)
ax.text(2037, 0.205, 'Threshold 0.19 mg/L', color=MUTED, fontsize=8.5)
ax.set_xlabel('Year'); ax.set_ylabel('Lake TP concentration (mg/L)')
ax.set_title('(b) Lake TP under four policies (median, 10–90% band)', fontsize=10.5, loc='left')
ax.set_ylim(0, 1.1); ax.set_xlim(2025, 2050)
ax.legend(loc='upper right', fontsize=8, frameon=False, ncol=2)
ax.grid(color='#eeede9', linewidth=0.6); ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(OUT + 'figure2_tradeoffs.png', dpi=300); fig.savefig(OUT + 'figure2_tradeoffs.pdf'); plt.close(fig)
print('figures written')
