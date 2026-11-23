"""One-compartment pharmacokinetics: a drug given as an IV bolus, then
repeated every 8 hours. Reference solution for the track "Simulation".

This is the kind of script an agent might write for the worked example.
It is here so that teachers and participants can compare their own result
with a known answer. Needs numpy, scipy and matplotlib.

Model (in words): the drug sits in one well-mixed compartment (the blood
plasma, volume V). It is removed at a rate proportional to how much is
there, so the concentration falls by half every half-life.

    dC/dt = -k * C,   k = ln(2) / t_half

Units: time in hours (h), concentration in mg/L, dose in mg, volume in L.

Checks printed at the end:
  1. single dose: the numerical solution matches C0 * exp(-k t)
  2. after one half-life the concentration is half of C0
  3. repeated dosing: the steady-state peak matches C0 / (1 - exp(-k tau))

Run:  python pk_one_compartment.py [output-folder]
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
out.mkdir(parents=True, exist_ok=True)

# ---- parameters, with units -------------------------------------------
dose_mg = 500.0      # mg, given as an IV bolus
V_L = 50.0           # L, volume of distribution
t_half_h = 6.0       # h, elimination half-life
tau_h = 8.0          # h, dosing interval for the repeated-dose case
n_doses = 10

k = np.log(2) / t_half_h          # 1/h
C0 = dose_mg / V_L                # mg/L just after one dose


def rhs(t, C):
    return -k * C


# ---- 1. single dose ------------------------------------------------------
t_eval = np.linspace(0, 48, 481)
sol = solve_ivp(rhs, (0, 48), [C0], t_eval=t_eval, rtol=1e-8, atol=1e-10)
C_num = sol.y[0]
C_exact = C0 * np.exp(-k * t_eval)
max_err = np.max(np.abs(C_num - C_exact))

C_at_half_life = np.interp(t_half_h, t_eval, C_num)
C_at_24 = np.interp(24.0, t_eval, C_num)

# ---- 2. repeated dosing: integrate between doses, add a dose each time ----
t_all, C_all = [], []
C_start = 0.0
peaks = []
for i in range(n_doses):
    C_start += C0                          # bolus: concentration jumps by C0
    peaks.append(C_start)
    t0 = i * tau_h
    ts = np.linspace(t0, t0 + tau_h, 81)
    s = solve_ivp(rhs, (t0, t0 + tau_h), [C_start], t_eval=ts,
                  rtol=1e-8, atol=1e-10)
    t_all.append(s.t)
    C_all.append(s.y[0])
    C_start = s.y[0][-1]
t_all = np.concatenate(t_all)
C_all = np.concatenate(C_all)

accumulation = 1.0 / (1.0 - np.exp(-k * tau_h))
peak_ss_exact = C0 * accumulation

# ---- report ---------------------------------------------------------------
print("One-compartment model, IV bolus")
print(f"  k = ln2/t_half = {k:.4f} 1/h, C0 = {C0:.2f} mg/L")
print(f"  max |numerical - exact| over 0-48 h: {max_err:.2e} mg/L")
print(f"  C at one half-life ({t_half_h:g} h): {C_at_half_life:.3f} mg/L "
      f"(expected {C0/2:.3f})")
print(f"  C at 24 h: {C_at_24:.4f} mg/L (expected C0/16 = {C0/16:.4f})")
print(f"  repeated dosing every {tau_h:g} h: peak after dose {n_doses} = "
      f"{peaks[-1]:.3f} mg/L; steady-state formula gives {peak_ss_exact:.3f}")

ok = (max_err < 1e-4 and abs(C_at_half_life - C0 / 2) < 1e-3
      and abs(peaks[-1] - peak_ss_exact) / peak_ss_exact < 0.01)
print("ALL CHECKS PASSED" if ok else "CHECK FAILED")

# ---- plots ----------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
ax = axes[0]
ax.plot(t_eval, C_exact, color="#bbbbbb", lw=6, label="exact: C0·exp(-kt)")
ax.plot(t_eval, C_num, color="#2a7f8f", lw=2, label="solve_ivp")
ax.axhline(C0 / 2, color="#a8324a", ls=":", lw=1)
ax.axvline(t_half_h, color="#a8324a", ls=":", lw=1)
ax.set_xlabel("time (h)")
ax.set_ylabel("plasma concentration (mg/L)")
ax.set_title("Single dose")
ax.legend(frameon=False)
ax = axes[1]
ax.plot(t_all, C_all, color="#6b4fa0", lw=2)
ax.axhline(peak_ss_exact, color="#8a6a12", ls="--", lw=1,
           label="steady-state peak (formula)")
ax.set_xlabel("time (h)")
ax.set_ylabel("plasma concentration (mg/L)")
ax.set_title(f"Dose every {tau_h:g} h")
ax.legend(frameon=False)
for a in axes:
    a.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(out / "pk_one_compartment.png", dpi=120)
