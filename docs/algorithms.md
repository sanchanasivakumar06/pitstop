# Mathematical Algorithms & Formulas

This document details the exact physics and calculation equations implemented across the engine modules.

---

## 1. Lap Time Simulation Model (`engine/lap_time.py`)

$$\text{LapTime} = T_{\text{base}} + \Delta_{\text{compound}} + \Delta_{\text{wear}} + \Delta_{\text{fuel}} + \Delta_{\text{weather}} + \Delta_{\text{traffic}} + \Delta_{\text{pace}} + \Delta_{\text{event}} + \epsilon$$

| Term | Unit | Description |
| :--- | :--- | :--- |
| $T_{\text{base}}$ | seconds | Nominal benchmark track lap time (e.g. $88.5\text{s}$ at Silverstone Classic). |
| $\Delta_{\text{compound}}$ | seconds | Base pace delta relative to Medium tyre on dry track (Soft: $-1.20\text{s}$, Hard: $+0.85\text{s}$). |
| $\Delta_{\text{wear}}$ | seconds | Degradation penalty calculated from current tyre wear and cliff distance. |
| $\Delta_{\text{fuel}}$ | seconds | Fuel mass weight penalty: $\text{fuel\_kg} \times 0.033\text{ s/kg}$. |
| $\Delta_{\text{weather}}$ | seconds | Penalty for compound mismatch with track wetness: $(1 - \text{Suitability})^2 \times 22.0\text{s}$. |
| $\Delta_{\text{traffic}}$ | seconds | Time lost following within dirty air wake ($< 1.4\text{s}$ gap). |
| $\Delta_{\text{pace}}$ | seconds | Driver push/conserve pace mode offset (PUSH: $-0.65\text{s}$, CONSERVE: $+0.80\text{s}$). |
| $\Delta_{\text{event}}$ | seconds | Track neutralization pace (Safety Car: $+32.0\text{s}$, VSC: $+18.0\text{s}$). |
| $\epsilon$ | seconds | Seeded Gaussian execution noise $\sim \mathcal{N}(0, 0.12^2)$. |

---

## 2. Tyre Wear & Degradation Cliff Model (`engine/tyres.py`)

Accumulated wear per lap:
$$\Delta\text{Wear} = W_{\text{base}} \times M_{\text{pace}} \times \big[1.0 + |\text{Temp} - T_{\text{opt}}| \cdot S_{\text{temp}}\big] \times M_{\text{mismatch}}$$

Lap time wear penalty ($\Delta_{\text{wear}}$):
$$\Delta_{\text{wear}} = \begin{cases}
\left(\frac{\text{wear}}{10}\right) \cdot K_{\text{linear}}, & \text{if wear} < \text{CliffThreshold} \\
\left(\frac{\text{CliffThreshold}}{10}\right) \cdot K_{\text{linear}} + (\text{wear} - \text{CliffThreshold})^2 \cdot K_{\text{cliff}}, & \text{if wear} \ge \text{CliffThreshold}
\end{cases}$$

---

## 3. Fuel Consumption & Mass Weight Model (`engine/fuel.py`)

Burn per lap:
$$\text{Burn} = B_{\text{base}} \times M_{\text{pace}} \times M_{\text{weather}}$$

- PUSH: $1.22 \times$
- NORMAL: $1.00 \times$
- CONSERVE: $0.82 \times$

Remaining range in laps:
$$\text{LapsRemaining} = \frac{\text{Fuel}_{\text{kg}}}{\text{BurnRate}}$$

---

## 4. Pit Stop Transit & Servicing Duration (`engine/pit_stop.py`)

$$T_{\text{pit}} = \max\big(6.0, T_{\text{pit\_lane\_loss}} - \Delta_{\text{SC\_discount}}\big) + \max(T_{\text{tyre\_change}}, T_{\text{refuel}}) + \text{CrewVariance}$$

Where:
- $T_{\text{pit\_lane\_loss}}$: Speed limit transit time through pit lane ($20.0\text{s}$ to $25.0\text{s}$).
- $\Delta_{\text{SC\_discount}}$: Time discount when pitting under Safety Car ($10.5\text{s}$) or VSC ($6.0\text{s}$).
- $T_{\text{tyre\_change}}$: Stationary wheel swap time ($2.45\text{s}$).
- $T_{\text{refuel}}$: Refuel mass / Flow rate ($\text{kg} / 2.80\text{ kg/s}$).
