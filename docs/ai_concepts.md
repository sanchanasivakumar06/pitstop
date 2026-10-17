# Artificial Intelligence Concepts & Formulation

The **Race Strategist** system integrates four foundational AI decision paradigms:

---

## 1. Intelligent Agent & PEAS Framework

| Dimension | Specification |
| :--- | :--- |
| **Performance Measure** | Primary: Minimize total race completion time ($\sum T_{\text{lap}} + T_{\text{pits}}$). Secondary: Avoid DNF, minimize tyre cliff exposure, maximize finishing position. |
| **Environment** | Stochastic, dynamic, partially observable, sequential, continuous-state / discrete-time. Features dynamic weather transitions, changing track temperatures, and unexpected incidents (Safety Car, punctures). |
| **Actuators** | **Pit Strategy Actions**: `STAY_OUT`, `PIT_SOFT`, `PIT_MEDIUM`, `PIT_HARD`, `PIT_INTER`, `PIT_WET`.<br>**Tactical Controls**: Refuel Mass (kg), Pace Mode (`PUSH`, `NORMAL`, `CONSERVE`). |
| **Sensors** | Onboard telemetry (lap, fuel remaining, tyre compound, wear %, temperature), competitor timing gaps ahead/behind, noisy rain and grip sensors, and race control flag indicators. |

---

## 2. Utility Theory & Maximum Expected Utility (MEU)

Rather than using opaque heuristics, the agent quantifies candidate actions by decomposing expected outcomes into 6 explicit utility terms:

$$U(a) = - \Big[ T_{\text{pit\_loss}}(a) - \Delta_{\text{pace\_gain}}(a) + \Delta_{\text{fuel\_weight}}(a) + P_{\text{wear\_risk}}(a) + P_{\text{traffic}}(a) + P_{\text{weather\_mismatch}}(a) \Big]$$

Where:
1. $T_{\text{pit\_loss}}(a)$: 0 if staying out; transit time + tyre service + refuelling - Safety Car discount if pitting.
2. $\Delta_{\text{pace\_gain}}(a)$: Cumulative pace advantage gained across the remainder of the stint by installing fresh rubber.
3. $\Delta_{\text{fuel\_weight}}(a)$: Mass penalty differences from adding fuel vs running lean.
4. $P_{\text{wear\_risk}}(a)$: Severe risk penalty applied if running past the cliff threshold or nursing an active puncture.
5. $P_{\text{traffic}}(a)$: Estimated time lost or undercut clean-air benefit relative to traffic windows.
6. $P_{\text{weather\_mismatch}}(a)$: Expected penalty under the Bayesian belief distribution:
   $$\mathbb{E}[\text{Mismatch}] = \sum_{w \in W} P(w \mid \text{Evidence}) \cdot \text{Cost}(c, w)$$

The agent selects the action with **Maximum Expected Utility**:
$$a^* = \arg\max_{a \in A} U(a)$$

---

## 3. Probabilistic Reasoning & Bayesian HMM Filtering

The agent cannot observe true weather states directly. Instead, track weather follows a 3-state Markov chain:

$$\mathcal{S}_W = \{\text{DRY}, \text{LIGHT\_RAIN}, \text{HEAVY\_RAIN}\}$$

Transition probability matrix $T_{i, j} = P(W_{t+1} = j \mid W_t = i)$.

At each lap $t$, noisy sensors return:
- Track grip measurement $G_t \in [0.2, 1.0]$
- Rain sensor level $R_t \in [0.0, 1.0]$

The agent computes the **Forward Bayesian Belief Update**:
1. **Prediction Step (Prior)**:
   $$P(W_t = s_j) = \sum_{s_i} T_{i, j} \cdot \text{Belief}_{t-1}(s_i)$$
2. **Observation Likelihood**:
   $$P(\text{Obs}_t \mid W_t = s_j) = \mathcal{N}(G_t; \mu_{G, j}, \sigma_{G, j}^2) \times \mathcal{N}(R_t; \mu_{R, j}, \sigma_{R, j}^2)$$
3. **Posterior Normalization**:
   $$\text{Belief}_t(s_j) = \frac{P(\text{Obs}_t \mid W_t = s_j) \cdot P(W_t = s_j)}{\sum_{k} P(\text{Obs}_t \mid W_t = s_k) \cdot P(W_t = s_k)}$$

---

## 4. Markov Decision Process (MDP) with Dynamic Programming

To balance immediate pit costs against long-term benefits across the entire race horizon, the flagship strategist formulates the decision as a finite-horizon MDP:

- **State Space**:
  $$s = (\text{lap}, \text{compound}, \text{tyre\_age}, \text{fuel\_level}, \text{weather\_state})$$
- **Action Space**:
  $$a \in \{\text{STAY\_OUT}, \text{PIT\_SOFT}, \text{PIT\_MEDIUM}, \text{PIT\_HARD}, \text{PIT\_INTER}, \text{PIT\_WET}\}$$
- **Reward**:
  $$R(s, a) = - \text{LapTime}(s, a)$$
- **Terminal Condition**:
  At lap $N = \text{total\_laps}$, remaining cost-to-go $V(s, N) = 0$.

### Backward Induction Algorithm
For $t = N - 1$ down to current lap:
$$Q(s, a, t) = \text{Cost}(s, a) + \sum_{w'} P(w' \mid w) V(s', t + 1)$$
$$V(s, t) = \min_{a} Q(s, a, t)$$
$$\pi^*(s, t) = \arg\min_{a} Q(s, a, t)$$

### Event-Driven Replanning
Because the state space is discretized into a vectorized NumPy tensor, backward induction solves in **under 15 ms**. The agent continuously monitors environmental shifts and re-solves whenever:
1. The Bayesian belief distribution shifts significantly (TVD $> 0.35$).
2. A Safety Car or Virtual Safety Car is deployed or withdrawn.
3. A puncture or mechanical event occurs.
