# Robust Phosphorus-Loading Policies for Powai Lake, Mumbai: Reformulating the Lake Problem under Deep Uncertainty

**Course**: CE 766 – Watershed Management  
**Author**: Jashanpreet Singh (Roll Number: `23B0985`)  
**Institution**: Department of Civil Engineering, Indian Institute of Technology Bombay (IIT Bombay)  
**Academic Term**: Autumn 2026  

---

## 1. Project Overview & Motivation

Powai Lake ($19.13^\circ\text{N}, 72.91^\circ\text{E}$) is an urban artificial lake located adjacent to the IIT Bombay campus in Mumbai, Maharashtra. It has a water spread area of $\sim 2.10\text{ km}^2$ and a small, densely urbanized catchment of $\sim 6.61\text{ km}^2$ situated in the Powai–Kanheri hill tract. 

Historically impounded in 1891, the lake has undergone severe ecological degradation, siltation (effective depth reduced to $\sim 2.5\text{ m}$, volume $\sim 5.25 \times 10^6\text{ m}^3$), and pervasive hyper-eutrophication driven by:
1. Continuous discharge of $\sim 18\text{ MLD}$ (million litres/day) of untreated domestic wastewater across 9 major nullahs.
2. Internal phosphorus recycling from anoxic sediment storage.
3. Highly episodic, monsoon-driven catchment runoff.

This project reformulates the classic shallow-lake problem (Carpenter et al., 1999; Singh et al., 2015; Quinn et al., 2017) to identify robust multi-objective phosphorus management policies for Powai Lake over a 25-year planning horizon (2026–2050) under deep uncertainty.

---

## 2. XLRM Framing Under Deep Uncertainty

| XLRM Category | Factor | Description / Operational Value |
| :--- | :--- | :--- |
| **X (Exogenous Uncertainties)** | $b$ | Phosphorus annual loss rate (burial + flushing): $b \in [0.40, 0.55]\text{ yr}^{-1}$ |
| | $r$ | Maximum sediment internal recycling rate: $r \in [8.0, 15.0]\text{ t/yr}$ |
| | $q$ | Non-linear recycling Hill exponent: $q \in [6.0, 10.0]$ |
| | $m$ | Half-saturation phosphorus stock: $m \in [1.8, 3.0]\text{ tons}$ |
| | $Y_t$ | Stochastic natural runoff load: $\ln Y_t \sim \mathcal{N}(0.704, 0.35^2)$ |
| | $\delta$ | Discount rate for economic cost assessment: $\delta \in [0.03, 0.07]$ |
| **L (Policy Levers)** | $a_t$ | Permitted annual anthropogenic sewage load: $a_t \in [0.0, 18.0]\text{ t/yr}$ |
| | Treatment Infrastructure | Implementation of 8 MLD STP vs. aggressive centralized diversion |
| **R (System Relationships)** | Carpenter Model | Non-linear discrete annual mass-balance state-transition equation |
| | SCS-CN Hydrology | Urban catchment rainfall-runoff conversion ($CN \approx 82$) |
| **M (Performance Metrics)** | Economic Benefit | Avoided sewage treatment and dredging capital/operational costs |
| | Peak Phosphorus | Minimum peak lake phosphorus stock ($\max_t X_t$) |
| | Reliability | Probability of staying below critical threshold $X_{\text{crit}} = 1.0\text{ t}$ |
| | Policy Inertia | Year-to-year loading variability / policy transition stability |

---

## 3. Mathematical Model Formulation

The lake phosphorus dynamics are modeled via the discrete annual mass-balance equation:

$$X_{t+1} = X_t + a_t + Y_t - b X_t + r \frac{X_t^q}{m^q + X_t^q}$$

### Plain-Text Running Format:
```text
X(t+1) = X(t) + a(t) + Y(t) - b*X(t) + r*[X(t)^q / (m^q + X(t)^q)]
```

### Component Justifications:
- **$X(t)$**: Total phosphorus stock stored in the lake water column at year $t$ (metric tons).
- **$a(t)$**: Anthropogenic phosphorus loading entering via wastewater drains. Baseline unmanaged load is $\approx 18.0\text{ t/yr}$ based on $18\text{ MLD}$ raw sewage with mean total phosphorus of $7.5\text{ mg/L}$.
- **$Y(t)$**: Stochastic natural non-point phosphorus export from the catchment during the monsoon, characterized by a lognormal distribution ($\ln Y_t \sim \mathcal{N}(0.704, 0.35^2)$, mean $\approx 2.10\text{ t/yr}$).
- **$b$**: Annual phosphorus loss fraction due to permanent sediment burial and hydraulic outflow flushing ($b \approx 0.48\text{ yr}^{-1}$, corresponding to an average hydraulic retention time of $\sim 0.55\text{ yr}$).
- **$r$**: Maximum internal sediment phosphorus release rate under bottom-water anoxia ($r \approx 12.0\text{ t/yr}$, equivalent to benthic flux of $\sim 15.6\text{ mg P/m}^2/\text{day}$).
- **$m$**: Half-saturation threshold ($m = 2.4\text{ tons}$).
- **$q$**: Hill exponent ($q = 8.0$), modeling the abrupt transition to internal phosphorus release when benthic redox conditions turn anoxic.
- **$X_{\text{crit}}$**: Critical eutrophication threshold ($1.0\text{ metric ton}$, corresponding to $0.10\text{ mg/L}$ total phosphorus concentration for a $5.25\times 10^6\text{ m}^3$ lake volume).

---

## 4. Key Datasets & Site-Specific Analysis

1. **IMD Gridded Daily Rainfall (1991–2025)**:
   - Acquired from India Meteorological Department (Pune) at $0.25^\circ \times 0.25^\circ$ grid resolution over Mumbai.
   - Long-term mean annual rainfall is $2,250\text{ mm}$, with $>90\%$ concentrated in the June–September southwest monsoon.
   - Runoff estimated using the SCS Curve Number method ($CN = 82$).

2. **Copernicus Sentinel-2 Surface Reflectance (2017–2025)**:
   - Extracted via Google Earth Engine (`COPERNICUS/S2_SR_HARMONIZED`).
   - Normalized Difference Chlorophyll Index (NDCI):
     $$\text{NDCI} = \frac{B_5 - B_4}{B_5 + B_4} = \frac{\rho_{705} - \rho_{665}}{\rho_{705} + \rho_{665}}$$
   - Cloud masking applied using QA60 and Scene Classification Layer (SCL).
   - Time series indicates chronic hyper-eutrophy ($\text{NDCI} \in [0.18, 0.46]$) with recurrent post-monsoon *Microcystis* blooms and dry-season *Eichhornia crassipes* (water-hyacinth) proliferation.

3. **Brihanmumbai Municipal Corporation (BMC) Baseline Data**:
   - Synthesized sewage flow estimates ($18\text{ MLD}$ untreated effluent) and planned mitigation infrastructure ($8\text{ MLD}$ Sewage Treatment Plant and interceptor channels).

---

## 5. Preliminary Baseline Simulation Results

A 25-year baseline Monte Carlo simulation (100 stochastic replicates, 2026–2050) was executed assuming no intervention ($a_t = 18.0\text{ t/yr}$) starting from the current degraded state ($X_0 = 12.5\text{ t}$):
- **Equilibrium Stock**: Phosphorus rapidly increases and equilibrates at a severe hyper-eutrophic steady state of **$67.0\text{ tons}$** (10th percentile: $66.0\text{ t}$, 90th percentile: $68.2\text{ t}$).
- **Threshold Exceedance**: **$100\%$ violation** of the critical eutrophication threshold ($X_{\text{crit}} = 1.0\text{ t}$) across all replicates.
- **Sediment Recycling Dominance**: At equilibrium, internal sediment recycling ($r = 12.0\text{ t/yr}$) contributes $\sim 37\%$ of total annual phosphorus inputs.
- **Hysteresis Trap**: The bifurcation flux analysis reveals that the planned $8\text{ MLD}$ plant ($a_t \approx 10.0\text{ t/yr}$) remains trapped in the upper eutrophic attractor ($X^* \approx 50\text{ t}$). Deeper loading cuts ($a_t \le 2.0\text{ t/yr}$) combined with sediment remediation are required to restore oligotrophic conditions.

---

## 6. Repository Structure

```text
├── CE766_Proposal_PowaiLake.pdf     # Submitted course project proposal
├── README.md                        # Project documentation and summary
├── generate_figures.py              # Script to render Figure 1 (PDF, PNG, SVG)
├── requirements.txt                 # Python environment specification
├── data/
│   ├── imd_rainfall_powai_1991_2025.csv       # 35-year IMD rainfall & SCS runoff
│   ├── sentinel2_ndci_powai_2017_2025.csv     # Monthly Sentinel-2 NDCI observations
│   └── baseline_simulation_results.csv        # 25-year baseline Monte Carlo trajectory
├── figures/
│   ├── figure1_preliminary_results.pdf        # High-res vector PDF figure
│   ├── figure1_preliminary_results.png        # Rendered publication-quality PNG figure
│   └── figure1_preliminary_results.svg        # Standalone vector SVG figure
└── src/
    ├── model.py                     # Carpenter lake phosphorus model & simulation engine
    └── process_data.py              # Data preprocessing and synthetic calibration pipeline
```

---

## 7. How to Reproduce Results

All scripts run on standard Python 3 without mandatory external dependencies:

```bash
# 1. Generate data files
python3 src/process_data.py

# 2. Run baseline 100-replicate Monte Carlo simulation
python3 src/model.py

# 3. Generate publication-quality multi-panel figure
python3 generate_figures.py
```

---

## 8. References

1. Carpenter, S. R., Ludwig, D., & Brock, W. A. (1999). Management of eutrophication for lakes subject to potentially irreversible change. *Ecological Applications*, 9(3), 751–771.
2. Singh, R., Reed, P. M., & Keller, K. (2015). Many-objective robust decision making for managing an ecosystem with a deeply uncertain threshold response. *Ecology and Society*, 20(3), 12.
3. Quinn, J. D., Reed, P. M., & Keller, K. (2017). Direct policy search for robust multi-objective management of deeply uncertain socio-ecological tipping points. *Environmental Modelling & Software*, 92, 125–141.
4. Mishra, S., & Mishra, D. R. (2012). Normalized difference chlorophyll index: a novel model for remote estimation of chlorophyll-a concentration in turbid productive waters. *Remote Sensing of Environment*, 117, 394–406.
5. Ratheesh Kumar, R., et al. (2015). State of water quality of two tropical urban lakes located at Mumbai megacity. *International Journal of Science and Research*, 4(5).
6. Surya, S., et al. (2018). Fish community structure and trophic status – a measure of ecological degradation: a case study from Powai Lake, Mumbai. *Int. J. Ecol. Environ. Sci.*, 44(4), 373–382.
