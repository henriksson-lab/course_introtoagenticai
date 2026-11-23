"""SIR epidemic model. Reference solution for the track "Simulation".

Model (in words): a closed population of N people is split into
Susceptible, Infected and Recovered. Each day, infected people meet others
and pass the infection on to susceptible ones (rate beta), and a fraction
of infected people recover (rate gamma). Nobody is born, dies or moves.

    dS/dt = -beta * S * I / N
    dI/dt =  beta * S * I / N - gamma * I
    dR/dt =  gamma * I

Units: time in days, beta and gamma per day, S, I, R in people.
R0 = beta / gamma is the number of people one infected person infects in
a fully susceptible population.

Checks printed at the end (all known results for this model):
  1. S + I + R stays equal to N (nobody appears or disappears)
  2. the number infected peaks when S = N / R0
  3. the peak size matches  N - N/R0 * (1 + ln(R0 * S0 / N))  (with I0 + S0 = N)
  4. the final fraction ever infected z solves  z = 1 - exp(-R0 * z)
     (approximately, because a few people are infected at the start)
  5. with R0 < 1 there is no epidemic: I only falls

Run:  python sir_model.py [output-folder]
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
out.mkdir(parents=True, exist_ok=True)

# ---- parameters, with units -------------------------------------------
N = 10_000          # people
I0 = 10             # people infected on day 0
beta = 0.3          # per day: infectious contacts per infected person
gamma = 0.1         # per day: 1 / (average infectious period of 10 days)
days = 200
R0 = beta / gamma
S0 = N - I0


def sir(t, y, beta, gamma):
    S, I, R = y
    new_inf = beta * S * I / N
    return [-new_inf, new_inf - gamma * I, gamma * I]


t = np.linspace(0, days, 2001)
sol = solve_ivp(sir, (0, days), [S0, I0, 0], t_eval=t, args=(beta, gamma),
                rtol=1e-9, atol=1e-9)
S, I, R = sol.y

# 1. conservation
cons_err = np.max(np.abs(S + I + R - N))

# 2 + 3. peak
ip = np.argmax(I)
S_at_peak = S[ip]
I_peak_formula = S0 + I0 - N / R0 * (1 + np.log(R0 * S0 / N))

# 4. final size
z_formula = brentq(lambda z: z - (1 - np.exp(-R0 * z)), 1e-6, 1)
z_sim = R[-1] / N

# 5. R0 < 1
sol_low = solve_ivp(sir, (0, days), [S0, I0, 0], t_eval=t,
                    args=(0.08, gamma), rtol=1e-9, atol=1e-9)
I_low = sol_low.y[1]
falls = np.all(np.diff(I_low) <= 1e-9)

print(f"SIR model, N = {N}, beta = {beta}/day, gamma = {gamma}/day, R0 = {R0:g}")
print(f"  1. max |S+I+R-N| = {cons_err:.2e} people")
print(f"  2. S at the peak = {S_at_peak:.0f}; N/R0 = {N/R0:.0f}")
print(f"  3. peak infected = {I[ip]:.0f} on day {t[ip]:.0f}; "
      f"formula gives {I_peak_formula:.0f}")
print(f"  4. fraction ever infected = {z_sim:.4f}; "
      f"final-size equation gives {z_formula:.4f}")
print(f"  5. with R0 = 0.8 the number infected only falls: {falls}")

ok = (cons_err < 1e-3 and abs(S_at_peak - N / R0) / N < 0.005
      and abs(I[ip] - I_peak_formula) / I_peak_formula < 0.005
      and abs(z_sim - z_formula) < 0.005 and falls)
print("ALL CHECKS PASSED" if ok else "CHECK FAILED")

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(t, S, color="#2a7f8f", lw=2, label="Susceptible")
ax.plot(t, I, color="#a8324a", lw=2, label="Infected")
ax.plot(t, R, color="#6b4fa0", lw=2, label="Recovered")
ax.axhline(N / R0, color="#8a6a12", ls=":", lw=1)
ax.text(days, N / R0, "N/R0", color="#8a6a12", ha="right", va="bottom")
ax.set_xlabel("time (days)")
ax.set_ylabel("people")
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(out / "sir_model.png", dpi=120)
