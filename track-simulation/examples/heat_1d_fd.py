"""Heat conduction in a 1D rod with finite differences.
Reference solution for the track "Simulation".

Model (in words): a metal rod of length L. Heat flows from warm to cold
parts, faster when the temperature changes steeply along the rod. The
thermal diffusivity alpha says how fast. The ends are held at fixed
temperatures (boundary conditions).

    dT/dt = alpha * d2T/dx2

The rod is cut into small pieces of length dx; each time step dt, every
piece moves towards the average of its neighbours (explicit scheme).

Units: x in m, t in s, T in degrees C, alpha in m^2/s.

Checks printed at the end:
  1. steady state with ends at 100 and 20 C is a straight line
  2. a sine-shaped start with both ends at 0 C decays as
     exp(-alpha * pi^2 * t / L^2); the error shrinks about 4x when dx halves
  3. with a time step above the stability limit dt <= dx^2 / (2 alpha)
     (rod at 20 C, left end suddenly at 100 C) the solution blows up: a plot can look like physics and be nonsense

Run:  python heat_1d_fd.py [output-folder]
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
out.mkdir(parents=True, exist_ok=True)

L = 1.0              # m
alpha = 1.0e-4       # m^2/s (order of magnitude of a metal such as aluminium)


def run(n_cells, t_end, T_init, T_left, T_right, safety=0.4):
    """Explicit finite differences. safety = alpha*dt/dx^2 (stable if <= 0.5)."""
    x = np.linspace(0, L, n_cells + 1)
    dx = x[1] - x[0]
    dt = safety * dx**2 / alpha
    n_steps = int(np.ceil(t_end / dt))
    dt = t_end / n_steps
    r = alpha * dt / dx**2
    T = T_init(x).astype(float)
    T[0], T[-1] = T_left, T_right
    for _ in range(n_steps):
        T[1:-1] = T[1:-1] + r * (T[2:] - 2 * T[1:-1] + T[:-2])
    return x, T, r


# ---- 1. steady state: a straight line --------------------------------------
t_long = 5 * L**2 / alpha          # long enough to settle (5 diffusion times)
x, T_ss, _ = run(50, t_long, lambda x: 20 + 0 * x, 100.0, 20.0)
T_line = 100 + (20 - 100) * x / L
err_ss = np.max(np.abs(T_ss - T_line))

# ---- 2. sine mode decay and mesh refinement --------------------------------
t_check = 0.1 * L**2 / alpha       # 1000 s
rows = []
for n in (10, 20, 40, 80):
    x, T, r = run(n, t_check, lambda x: 100 * np.sin(np.pi * x / L), 0.0, 0.0,
                  safety=0.25)
    exact = 100 * np.sin(np.pi * x / L) * np.exp(-alpha * np.pi**2 * t_check / L**2)
    rows.append((n, L / n, np.max(np.abs(T - exact))))

# ---- 3. unstable time step --------------------------------------------------
# rod at 20 C, left end suddenly heated to 100 C, right end kept at 20 C
x_u, T_u, r_u = run(40, 200.0, lambda x: 20 + 0 * x, 100.0, 20.0, safety=0.6)
x_s, T_s, r_s = run(40, 200.0, lambda x: 20 + 0 * x, 100.0, 20.0, safety=0.4)

print("1D heat equation, explicit finite differences")
print(f"  1. steady state, ends 100 C and 20 C: max distance from straight "
      f"line = {err_ss:.2e} C")
print(f"  2. sine decay at t = {t_check:.0f} s (exact centre value "
      f"{100*np.exp(-alpha*np.pi**2*t_check/L**2):.3f} C):")
print("     cells   dx (m)   max error (C)   error ratio")
prev = None
for n, dx, e in rows:
    ratio = "" if prev is None else f"{prev / e:.2f}"
    print(f"     {n:5d}   {dx:.4f}   {e:.2e}        {ratio}")
    prev = e
print(f"  3. time step factor r = alpha*dt/dx^2 = {r_u:.2f} (> 0.5): "
      f"max |T| after 200 s = {np.max(np.abs(T_u)):.3g} C "
      f"(stable run with r = {r_s:.2f}: {np.max(np.abs(T_s)):.1f} C, "
      "never above the hottest end)")

ratios = [rows[i][2] / rows[i + 1][2] for i in range(len(rows) - 1)]
ok = (err_ss < 1e-3 and all(3.5 < q < 4.5 for q in ratios)
      and np.max(np.abs(T_u)) > 1000 and np.max(T_s) <= 100.0 + 1e-9)
print("ALL CHECKS PASSED" if ok else "CHECK FAILED")

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
ax = axes[0]
ax.plot(x_s, T_s, color="#2a7f8f", lw=2, label=f"stable (r = {r_s:.2f})")
ax.plot(x_u, np.clip(T_u, -50, 200), color="#a8324a", lw=1.5,
        label=f"unstable (r = {r_u:.2f}), clipped")
ax.set_xlabel("position along rod (m)")
ax.set_ylabel("temperature (C)")
ax.set_title("Same model, two time steps, t = 200 s")
ax.legend(frameon=False, loc="upper right")
ax = axes[1]
ns = [r[1] for r in rows]
es = [r[2] for r in rows]
ax.loglog(ns, es, "o-", color="#6b4fa0", lw=2)
ax.set_xlabel("cell size dx (m)")
ax.set_ylabel("max error (C)")
ax.set_title("Halving dx cuts the error ~4x")
for a in axes:
    a.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(out / "heat_1d_fd.png", dpi=120)
