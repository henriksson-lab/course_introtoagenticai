"""Agent-based model: many random walkers compared with the diffusion
equation. Reference solution for the track "Simulation".

Model (in words): 20,000 particles (molecules, cells, animals) start at the
same spot. Each time step, each one takes a step of length dx left or right
at random. Nobody coordinates; the spreading cloud is what we compare with
the smooth diffusion prediction.

Diffusion predicts, with D = dx^2 / (2 dt):
  - mean squared distance from the start = 2 * D * t
  - the positions follow a bell curve (normal distribution) with
    standard deviation sqrt(2 * D * t)

Units: position in micrometres (um), time in seconds (s).

Checks printed at the end:
  1. mean squared displacement against 2 D t at several times
  2. the share of walkers within one standard deviation is about 68 %
  3. the same with 50 walkers: the agent model is noisy when small

Run:  python random_walk_diffusion.py [output-folder]
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
out.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(42)    # fixed seed: the same numbers every run

n_walkers = 20_000
dx_um = 1.0          # um per step
dt_s = 0.01          # s per step
n_steps = 1000       # 10 s in total
D = dx_um**2 / (2 * dt_s)          # um^2/s  (= 50)


def simulate(n):
    steps = rng.choice([-dx_um, dx_um], size=(n_steps, n))
    return np.cumsum(steps, axis=0)  # position after each step


pos = simulate(n_walkers)
check_steps = [100, 250, 500, 1000]

print(f"Random walk, {n_walkers} walkers, D = dx^2/(2 dt) = {D:g} um^2/s")
print("     t (s)   mean sq. distance   2 D t   ratio")
ratios = []
for k in check_steps:
    t = k * dt_s
    msd = np.mean(pos[k - 1] ** 2)
    ratios.append(msd / (2 * D * t))
    print(f"     {t:5.1f}   {msd:12.1f}      {2*D*t:6.0f}   {ratios[-1]:.3f}")

sigma = np.sqrt(2 * D * n_steps * dt_s)
within = np.mean(np.abs(pos[-1]) <= sigma)
print(f"  share within one standard deviation ({sigma:.1f} um) at 10 s: "
      f"{within:.3f} (bell curve: 0.683)")

small = simulate(50)
r_small = np.mean(small[-1] ** 2) / (2 * D * n_steps * dt_s)
print(f"  with only 50 walkers the ratio at 10 s is {r_small:.2f}: "
      "small agent models are noisy; run several seeds")

ok = all(abs(r - 1) < 0.05 for r in ratios) and abs(within - 0.683) < 0.02
print("ALL CHECKS PASSED" if ok else "CHECK FAILED")

fig, ax = plt.subplots(figsize=(7, 4))
bins = np.arange(-120, 122, 4)
ax.hist(pos[-1], bins=bins, density=True, color="#2a7f8f", alpha=0.6,
        label="walkers at 10 s")
xs = np.linspace(-120, 120, 400)
ax.plot(xs, np.exp(-xs**2 / (2 * sigma**2)) / (sigma * np.sqrt(2 * np.pi)),
        color="#a8324a", lw=2, label="diffusion prediction")
ax.set_xlabel("distance from start (um)")
ax.set_ylabel("share of walkers per um")
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(out / "random_walk_diffusion.png", dpi=120)
