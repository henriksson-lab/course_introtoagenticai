"""Result plots for the Simulation track deck (fig*-*.svg made with matplotlib).
The concept figures in this folder are hand-written SVG; these are the
figures that show real model output. Needs numpy, scipy and matplotlib.
The beam numbers come from examples/fem_plate_and_beam.py (scikit-fem 12.0.2).

Run from anywhere:  python make-figs.py
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
TEAL, PURPLE, CRIMSON, OCHRE, GREY = "#2a7f8f", "#6b4fa0", "#a8324a", "#8a6a12", "#999999"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 15,
                     "axes.titlesize": 16, "axes.spines.top": False,
                     "axes.spines.right": False, "svg.fonttype": "path",
                     "svg.hashsalt": "track-simulation"})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(HERE / name, format="svg", metadata={"Date": None})
    plt.close(fig)


# ---- units trap: half-life 6 h, but the agent assumed minutes ---------------
t = np.linspace(0, 24, 600)
C0 = 10.0
fig, ax = plt.subplots(figsize=(10, 4.2))
ax.plot(t, C0 * np.exp(-np.log(2) / 6 * t), color=TEAL, lw=3,
        label="half-life 6 hours (intended)")
ax.plot(t, C0 * np.exp(-np.log(2) / (6 / 60) * t), color=CRIMSON, lw=3,
        label="half-life read as 6 minutes")
ax.axhline(2.0, color=OCHRE, ls="--", lw=1.5)
ax.text(23.8, 2.15, "effective level 2 mg/L", color=OCHRE, ha="right")
ax.set_xlabel("time after dose (hours)")
ax.set_ylabel("concentration (mg/L)")
ax.legend(frameon=False, loc="upper right")
save(fig, "fig11-units-trap.svg")

# ---- PK check -----------------------------------------------------------------
k = np.log(2) / 6
sol = solve_ivp(lambda t, c: -k * c, (0, 24), [C0], t_eval=np.linspace(0, 24, 25),
                rtol=1e-8, atol=1e-10)
fig, ax = plt.subplots(figsize=(10, 4.2))
ax.plot(t, C0 * np.exp(-k * t), color="#cccccc", lw=8, label="known answer: halves every 6 h")
ax.plot(sol.t, sol.y[0], "o", color=TEAL, ms=7, label="the agent's simulation")
for n, tt in enumerate([6, 12, 18, 24], start=1):
    ax.annotate(f"{C0 / 2**n:g}", (tt, C0 / 2**n), xytext=(tt + 0.4, C0 / 2**n + 0.9),
                color=PURPLE, fontsize=15)
ax.set_xticks([0, 6, 12, 18, 24])
ax.set_xlabel("time after dose (hours)")
ax.set_ylabel("concentration (mg/L)")
ax.legend(frameon=False, loc="upper right")
save(fig, "fig13-pk-check.svg")

# ---- SIR check ------------------------------------------------------------------
N, I0, beta, gamma = 10_000, 10, 0.3, 0.1


def sir(t, y, b):
    S, I, R = y
    f = b * S * I / N
    return [-f, f - gamma * I, gamma * I]


tt = np.linspace(0, 160, 1601)
S, I, R = solve_ivp(sir, (0, 160), [N - I0, I0, 0], t_eval=tt, args=(beta,),
                    rtol=1e-9, atol=1e-9).y
low = solve_ivp(sir, (0, 160), [N - I0, I0, 0], t_eval=tt, args=(0.08,),
                rtol=1e-9, atol=1e-9).y[1]
fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), gridspec_kw={"width_ratios": [2, 1]})
ax = axes[0]
ax.plot(tt, S, color=TEAL, lw=3, label="Susceptible")
ax.plot(tt, I, color=CRIMSON, lw=3, label="Infected")
ax.plot(tt, R, color=PURPLE, lw=3, label="Recovered")
ax.plot(tt, S + I + R, color=GREY, lw=2, ls="--", label="total (must stay 10 000)")
ip = np.argmax(I)
ax.axvline(tt[ip], color=OCHRE, lw=1.5, ls=":")
ax.text(tt[ip] + 2, 5200, f"peak: S = {S[ip]:.0f}\n(N/R0 = 3333)", color=OCHRE, fontsize=14)
ax.set_xlabel("time (days)")
ax.set_ylabel("people")
ax.set_ylim(0, 11500)
ax.set_title("R0 = 3")
ax.legend(frameon=False, loc="center right", fontsize=13)
ax = axes[1]
ax.plot(tt, low, color=CRIMSON, lw=3)
ax.set_xlabel("time (days)")
ax.set_ylabel("infected")
ax.set_title("R0 = 0.8: no outbreak")
save(fig, "fig14-sir-check.svg")

# ---- unstable time step (1D rod, explicit finite differences) ---------------------
L, alpha = 1.0, 1.0e-4


def rod(r, t_end, n=40):
    x = np.linspace(0, L, n + 1)
    dx = x[1] - x[0]
    dt = r * dx**2 / alpha
    T = np.full(n + 1, 20.0)
    T[0] = 100.0
    for _ in range(int(round(t_end / dt))):
        T[1:-1] = T[1:-1] + r * (T[2:] - 2 * T[1:-1] + T[:-2])
    return x, T


fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)
for ax, (r, label, col) in zip(axes, [(0.4, "time step below the limit", TEAL),
                                       (0.6, "time step 1.5 x larger", CRIMSON)]):
    for t_end, ls in [(75, ":"), (150, "--"), (300, "-")]:
        x, T = rod(r, t_end)
        ax.plot(x, np.clip(T, -60, 220), color=col, lw=2.5, ls=ls,
                label=f"t = {t_end} s")
    ax.set_title(label, color=col)
    ax.set_xlabel("position along the rod (m)")
    ax.set_ylim(-60, 220)
axes[0].set_ylabel("temperature (C)")
axes[0].legend(frameon=False, loc="upper right")
axes[1].text(0.98, 200, "values clipped:\nthe real ones reach millions",
             ha="right", va="top", fontsize=13, color=CRIMSON,
             bbox=dict(facecolor="white", edgecolor=CRIMSON, boxstyle="round"))
save(fig, "fig15-unstable.svg")

# ---- beam: refinement with two element types -------------------------------------------
tri = np.array([80, 320, 1280, 5120])
p2 = np.array([1.5223, 1.5245, 1.5251, 1.5254])
p1 = np.array([0.5597, 1.0640, 1.3756, 1.4848])
formula = 1.5238
fig, ax = plt.subplots(figsize=(10, 4.4))
ax.axhline(formula, color=OCHRE, lw=2, ls="--")
ax.text(5600, formula + 0.04, "textbook formula 1.52 mm", color=OCHRE, ha="right")
ax.plot(tri, p2, "o-", color=PURPLE, lw=3, ms=9, label="quadratic triangles: settles at once")
ax.plot(tri, p1, "s-", color=CRIMSON, lw=3, ms=9, label="linear triangles: far too stiff when coarse")
for x_, y_ in zip(tri, p1):
    ax.annotate(f"{y_:.2f}", (x_, y_), xytext=(8, -18), textcoords="offset points",
                color=CRIMSON, fontsize=14)
ax.set_xscale("log")
ax.set_xticks(tri)
ax.set_xticklabels([str(v) for v in tri])
ax.minorticks_off()
ax.set_ylim(0.3, 1.8)
ax.set_xlabel("number of triangles in the mesh")
ax.set_ylabel("tip deflection (mm)")
ax.legend(frameon=False, loc="lower right")
save(fig, "fig16-beam-refinement.svg")

# ---- random walkers: many vs few --------------------------------------------------------
rng = np.random.default_rng(42)
dx, dt, n_steps = 1.0, 0.01, 1000
D = dx**2 / (2 * dt)
big = np.cumsum(rng.choice([-dx, dx], size=(n_steps, 20000)), axis=0)
sigma = np.sqrt(2 * D * n_steps * dt)
fig, axes = plt.subplots(1, 2, figsize=(12, 4.3))
ax = axes[0]
ax.hist(big[-1], bins=np.arange(-120, 122, 4), density=True, color=TEAL, alpha=0.55,
        label="20 000 walkers")
xs = np.linspace(-120, 120, 400)
ax.plot(xs, np.exp(-xs**2 / (2 * sigma**2)) / (sigma * np.sqrt(2 * np.pi)),
        color=CRIMSON, lw=3, label="diffusion prediction")
ax.set_xlabel("distance from start (µm), after 10 s")
ax.set_yticks([])
ax.set_title("Many walkers match the prediction")
ax.legend(frameon=False, loc="upper left", fontsize=13)
ax = axes[1]
ts = np.arange(1, n_steps + 1) * dt
for s in range(5):
    small = np.cumsum(rng.choice([-dx, dx], size=(n_steps, 50)), axis=0)
    ax.plot(ts, np.mean(small**2, axis=1), color=PURPLE, lw=1.5, alpha=0.8,
            label="50 walkers, 5 runs" if s == 0 else None)
ax.plot(ts, 2 * D * ts, color=CRIMSON, lw=3, label="prediction 2Dt")
ax.set_xlabel("time (s)")
ax.set_ylabel("mean squared distance (µm²)")
ax.set_title("Few walkers: every run differs")
ax.legend(frameon=False, loc="upper left", fontsize=13)
save(fig, "fig17-walkers-noise.svg")
print("done")
