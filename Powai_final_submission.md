# How much sewage phosphorus must be removed to restore Powai Lake?

CE 766 Watershed Management, final project. Jashanpreet Singh (23B0985)

## 1. Problem statement

Powai Lake (19.13°N, 72.91°E) is a 2.1 km² artificial lake beside IIT Bombay. It drains a 6.61 km² urbanised catchment and receives about 18 million litres per day (MLD) of untreated sewage through nullahs. In 2018–2020, total phosphorus (TP) at the lake centre averaged 0.93 mg/L, which is hypereutrophic. I ask what fraction of sewage phosphorus must be removed each year in 2026–2050 to keep TP below 0.19 mg/L (1 t of P) at the lowest cost. The stakeholders are the BMC, which pays; residents and activists; fishers and lake users; and IIT Bombay.

Changes from my preliminary report:

1. It understated the sewage load. 18 t/yr from 18 MLD implies only 2.7 mg/L TP in raw sewage. I assume 5 mg/L, which gives 32.9 t/yr. Its 1 t threshold is 0.19 mg/L, not 0.10.
2. Its b = 0.48/yr ignored flushing, but the water residence time is 0.31 years. I now build explicit water and phosphorus budgets and calibrate settling to observed TP. With these changes, the claimed "hysteresis trap" disappears.
3. Its rainfall and NDCI series were synthetic, not IMD or Sentinel-2 data. I now label the rainfall synthetic and drop NDCI.
4. Interventions now enter as the removal fraction u.
5. I dropped PRIM.
6. My class MOO run (250 generations, 10 Pareto points) stopped at 0.96 reliability. I now check convergence, and the optimizer reaches 100%.
7. I write in the first person.

## 2. Data

- **Lake geometry.** The area is 2.1 km² and the catchment is 6.61 km² (Lekshmi et al., 2021). I assumed a mean depth of 2.5 m, which gives a volume V of 5.25 million m³.
- **Observed lake TP.** Lekshmi et al. (2021) sampled the lake monthly from April 2018 to March 2020. I calibrate to their lake-centre mean of 0.93 mg/L.
- **Sewage.** The flow is 18 MLD (BMC figure). I assumed a TP concentration of 5 mg/L.
- **Rainfall (synthetic).** I generated annual totals from a normal distribution with mean 2,250 mm and standard deviation 400 mm, clipped to 1,300–3,800 mm. This gives 100 replicates of 25 years. The rainfall and Sentinel-2 files in my preliminary repository were also random-generator output, so I do not treat them as observations.
- **Resolution.** The model runs on an annual time step, and the lake is a single well-mixed box.

## 3. Methodology

**Model.** I use an annual phosphorus mass balance with sediment recycling (Carpenter et al., 1999), integrated exactly over each year because a loss rate near 8/yr makes the discrete form X − bX negative.

```
X(t+1) = X(t)·exp(−k_t) + (L_t / k_t)·(1 − exp(−k_t))
L_t    = (1 − u_t)·A0 + Y_t + r·X(t)^q / (m^q + X(t)^q)
k_t    = Q_out,t / V + σ
Q_out,t = C·P_t·A_c + P_t·A_L + Q_s − E·A_L
Y_t    = C·P_t·A_c·c_r
```

The terms are:

- X: P stored in the lake (t)
- u_t: fraction of sewage P removed (the lever)
- A0 = Q_s·c_s: untreated sewage load (c_s = 5 mg/L), 32.9 t/yr
- Q_s: sewage flow, 6.57 million m³/yr
- Y_t: runoff P load
- C: runoff coefficient, 0.60 (assumed)
- P_t: rainfall (m); A_c, A_L: catchment and lake areas
- E: evaporation, 1.6 m/yr (assumed)
- c_r: runoff TP, 0.22 mg/L (assumed)
- r: maximum sediment release, 5 mg/m²/day × A_L = 3.83 t/yr (assumed)
- m = 2 t, q = 8: recycling half-saturation and steepness; σ: net settling rate

**Calibration.** I set σ so that the steady state under today's loads equals the observed 0.93 mg/L (X_obs = 4.88 t). This gives σ = 4.70 per year, a settling velocity of 11.8 m/yr and a phosphorus retention of 0.59.

**XLRM.**

- **X (uncertainties):** sewage TP 4–8 mg/L; sediment release 1–15 mg/m²/day; m 1–3 t; q 6–10; observed TP 0.6–1.3 mg/L (σ recalibrated each time); rainfall.
- **L (lever):** a closed-loop rule (direct policy search; Quinn et al., 2017). u_t = u_high if X_t > X_s, otherwise u_low (three decision variables). The planned 8 MLD plant is u = 0.36 (8 of 18 MLD treated from 5 to 1 mg/L, effluent assumed, returned to the lake). Full diversion with tertiary treatment is u = 1.
- **R:** the equations above.
- **M (objectives):**
  - Minimise present-value cost, Σ(5.3·u + 2.0·u²)/1.05^t in ₹ crore (assumed ₹8,000 per ML treated, plus ₹2 crore/yr for tertiary P removal at u = 1).
  - Minimise mean TP.
  - Maximise reliability: share of years and replicates with X < 1 t.
  - Maximise inertia: share of years where u changes by 0.1 or less.

**Optimisation.** NSGA-II (pymoo 0.6.2), population 100, 1,000 generations, 5 seeds, the same 100 rainfall replicates for every evaluation. I checked convergence with the hypervolume and a brute-force grid of rules.

## 4. Results

**Budgets (Figure 1).** In a mean year, inflows are runoff (8.9 million m³), rain on the lake (4.7) and sewage (6.6). Evaporation removes 3.4 and the weir outflow carries 16.9, so the water residence time is only 0.31 years. Sewage supplies 32.9 of the 38.6 t/yr of phosphorus input, against 2.0 from runoff and 3.8 from sediment. Settling removes 23.0 t/yr and outflow 15.7. Under nominal values the lake has a single equilibrium, because recycling can rise by at most 3.8 t/yr per tonne of stored P while losses rise by 7.9. The bistable "trap" in my preliminary report came from ignoring flushing.

**Convergence.** My first formulation optimised 25 separate annual values of u. Its hypervolume flattened, but the cheapest 100%-reliable policy it found cost ₹97.3 crore. A simple brute-force rule achieved the same reliability for ₹86.6 crore, so that run had not converged even though the hypervolume looked flat. With the three-variable rule, four of five seeds reached ₹86.4–87.0 crore and one stalled at ₹92.1 crore. The merged Pareto set beats the brute-force benchmark at every reliability level. The same failure probably explains my class MOO exercise, where 250 generations gave only 10 Pareto points and a best reliability of 0.96. **100% reliability is achievable.**

**Policies (Figure 2):**

| Policy | PV cost (₹ crore) | Mean TP (mg/L) | Reliability |
|---|---|---|---|
| No action | 0 | 0.93 | 0% |
| Planned 8 MLD STP | 32.1 | 0.65 | 0% |
| Cheapest 100%-reliable (u_low 0.83, 0.96 while X > 4.3 t) | 86.4 | 0.18 | 100% |
| **Compromise** (u_low 0.88, 0.99 while X > 3.7 t) | 93.4 | 0.14 | 100% |
| Activist (u = 1 always) | 108.0 | 0.05 | 100% |

These numbers hold on 100 fresh rainfall replicates. I then re-evaluated the policies across 500 sampled parameter sets. Reliability stayed at 95% or above in 48% of sets for the cheapest policy, 87% for the compromise and 97% for the activist policy. It was 0% for both no action and the 8 MLD plant.

## 5. Discussion

The planned 8 MLD plant is necessary but far from enough. It removes only about a third of the sewage phosphorus, and lake TP settles near 0.65 mg/L, more than three times the threshold. Because the lake flushes about three times a year, it responds within one or two years to load cuts. The binding constraint is therefore how much sewage is removed, not legacy sediment. About 85–90% of the sewage P has to be kept out of the lake, which means intercepting almost all 18 MLD rather than treating 8 MLD of it.

**Why the activist should accept the compromise.** The activist's ideal of removing everything maximises reliability and minimises mean TP at the same time. In my class exercise I accepted 0.96 reliability as the activist. Here the compromise gives up nothing on reliability, which is 100%, so the extra ₹14.6 crore (16%) only buys lower TP, from 0.14 to 0.05 mg/L, for a lake that is already below the threshold. That money pays for removing the last 12% of the load, which needs tertiary treatment at the highest marginal cost. Across the uncertain parameter sets, the activist policy raises the share that stays at least 95% reliable from 87% to 97%. That is a ten-point gain for 16% more money. The compromise also differs from the cheapest 100%-reliable policy, which I reject. That policy runs only 0.01 mg/L below the threshold and drops below 95% reliability in about half of the plausible parameter sets. The compromise adds ₹7 crore (8%) and nearly doubles that robustness. It also asks the BMC for near-complete removal only while lake P is high, in the first year, and then holds at 88%. That is easier to finance and keeps the lake well below the threshold. A cheaper reliable plan is also more likely to be funded and sustained, which matters to the activist too.

**Limitations.** The rainfall is synthetic. The calibration rests on one mean TP value. Sewage concentration, runoff coefficient, evaporation, sediment release and costs are assumed. The single-box annual model ignores seasonal monsoon flushing and spatial differences between nullah mouths and the lake centre. The next steps are real IMD rainfall, a measured sewage TP and flow survey, and monthly calibration against the 2018–2020 data.

## 6. References and repository

1. Carpenter, S.R., Ludwig, D., & Brock, W.A. (1999). Management of eutrophication for lakes subject to potentially irreversible change. *Ecological Applications*, 9(3), 751–771.
2. Quinn, J.D., Reed, P.M., & Keller, K. (2017). Direct policy search for robust multi-objective management of deeply uncertain socio-ecological tipping points. *Environmental Modelling & Software*, 92, 125–141. https://doi.org/10.1016/j.envsoft.2017.02.017
3. Lekshmi, B., Saha, D., Sutar, R.S., et al. (2021). Science & technology agenda for blue-green spaces inspired by citizen science: Case for rejuvenation of Powai Lake. *Sustainability*, 13(18), 10061. https://doi.org/10.3390/su131810061

Code and data: https://github.com/jashansings/ce766-powai-lake-phosphorus

---

**Figure 1.** (a) Annual water budget for a mean rainfall year (million m³/yr). (b) Phosphorus budget at calibration to the observed 0.93 mg/L (t P/yr). File: `figures/figure1_budgets.png`.

**Figure 2.** (a) Pareto set from NSGA-II: present-value cost against mean lake TP, with the named policies marked. (b) Lake TP trajectories on 100 fresh synthetic rainfall replicates (median and 10–90% band). File: `figures/figure2_tradeoffs.png`.
