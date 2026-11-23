"""Finite elements with scikit-fem: a heated plate and a bent beam.
Reference solution for the track "Simulation" (FEM option).

Needs scikit-fem (tested with 12.0.2), numpy, scipy and matplotlib.
Install in a project environment, not system-wide, for example:
    python -m venv .venv
    .venv/bin/pip install scikit-fem matplotlib        (Windows: .venv\\Scripts\\pip)

Part 1, heat. A square plate, 1 m x 1 m. Left edge held at 100 C, right
edge at 20 C, top and bottom edges insulated (no heat flows through them).
Steady state. Known answer: temperature falls in a straight line from left
to right, T = 100 - 80 x. Linear elements reproduce this exactly, so the
error should be at the level of rounding (about 1e-12).

Part 2, beam. A steel cantilever, 1 m long, 0.05 m high (thin, so plane
stress, unit thickness 0.01 m), clamped at the left end, with a downward
force P = 100 N spread over the right end. Known formula (textbook, slender
beam): tip deflection = P L^3 / (3 E I), with I = t h^3 / 12.
With quadratic triangles (P2) the answer settles within about 0.1 % of the
formula (slightly above it: the formula ignores shear, a small effect for a
beam 20 times longer than high). With linear triangles (P1) the coarse mesh
is far too stiff (63 % too little deflection with 80 triangles): "shear
locking". The picture looks like a bent beam either way. Only the
refinement table and the known formula reveal the problem.

Units: SI throughout (m, N, Pa, C).

Run:  python fem_plate_and_beam.py [output-folder]
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import skfem as fem
from skfem.helpers import dot, grad
from skfem.models.elasticity import linear_elasticity, lame_parameters

out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
out.mkdir(parents=True, exist_ok=True)

# ---- Part 1: heat in a plate ------------------------------------------------
@fem.BilinearForm
def conduction(u, v, w):
    k = 200.0                                  # W/(m K), aluminium-like
    return k * dot(grad(u), grad(v))


mesh = fem.MeshTri.init_tensor(np.linspace(0, 1, 21), np.linspace(0, 1, 21))
mesh = mesh.with_boundaries({
    "left": lambda x: np.isclose(x[0], 0.0),
    "right": lambda x: np.isclose(x[0], 1.0),
})
basis = fem.Basis(mesh, fem.ElementTriP1())
A = conduction.assemble(basis)
T = basis.zeros()
left = basis.get_dofs("left")
right = basis.get_dofs("right")
T[left] = 100.0
T[right] = 20.0
fixed = np.concatenate([left.all(), right.all()])
T = fem.solve(*fem.condense(A, x=T, D=fixed))
T_exact = 100.0 - 80.0 * mesh.p[0]
err_plate = np.max(np.abs(T - T_exact))
print("Part 1: plate, left 100 C, right 20 C, top and bottom insulated")
print(f"  {mesh.nelements} triangles; max |FEM - straight line| = {err_plate:.1e} C")
print(f"  temperature in the centre: {basis.interpolator(T)(np.array([[0.5], [0.5]]))[0]:.3f} C"
      " (expected 60.000)")

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
ax = axes[0]
tc = ax.tripcolor(mesh.p[0], mesh.p[1], mesh.t.T, T, shading="gouraud",
                  cmap="coolwarm")
ax.triplot(mesh.p[0], mesh.p[1], mesh.t.T, color="k", lw=0.2)
fig.colorbar(tc, ax=ax, label="temperature (C)")
ax.set_aspect("equal")
ax.set_title("Plate: steady temperature")
ax.set_xlabel("x (m)")
ax.set_ylabel("y (m)")

# ---- Part 2: cantilever beam -----------------------------------------------
L, h, t_m = 1.0, 0.05, 0.01        # m
E, nu = 210e9, 0.3                 # Pa, steel
P = 100.0                          # N, total downward force at the tip
I = t_m * h**3 / 12
tip_formula = P * L**3 / (3 * E * I)

# plane stress: use modified Lame parameters
lam, mu = lame_parameters(E, nu)
lam_ps = 2 * lam * mu / (lam + 2 * mu)


@fem.LinearForm
def tip_load(v, w):
    traction = -P / (h * t_m)                  # N/m^2 over the end face
    return traction * v[1] * t_m


def beam(element, nx, ny):
    m = fem.MeshTri.init_tensor(np.linspace(0, L, nx + 1),
                                np.linspace(0, h, ny + 1))
    m = m.with_boundaries({"clamped": lambda x: np.isclose(x[0], 0.0),
                           "tip": lambda x: np.isclose(x[0], L)})
    eb = fem.Basis(m, fem.ElementVector(element))
    K = linear_elasticity(lam_ps, mu).assemble(eb) * t_m
    fb = fem.FacetBasis(m, eb.elem, facets=m.boundaries["tip"])
    f = tip_load.assemble(fb)
    u = fem.solve(*fem.condense(K, f, D=eb.get_dofs("clamped")))
    return -eb.interpolator(u)(np.array([[L], [h / 2]]))[1][0]


meshes = [(20, 2), (40, 4), (80, 8), (160, 16)]
rows = [(nx * ny * 2, beam(fem.ElementTriP2(), nx, ny)) for nx, ny in meshes]
rows_p1 = [(nx * ny * 2, beam(fem.ElementTriP1(), nx, ny)) for nx, ny in meshes]

print("\nPart 2: steel cantilever, L = 1 m, h = 0.05 m, P = 100 N")
print(f"  formula P L^3 / (3 E I) = {tip_formula*1000:.4f} mm")
print("     triangles   P2 tip (mm)  vs formula   P1 tip (mm)  vs formula")
for (n, d), (_, d1) in zip(rows, rows_p1):
    print(f"     {n:9d}   {d*1000:9.4f}    {100*(d/tip_formula-1):+6.2f} %"
          f"    {d1*1000:9.4f}    {100*(d1/tip_formula-1):+6.2f} %")

ok = (err_plate < 1e-8
      and abs(rows[-1][1] - rows[-2][1]) / rows[-1][1] < 1e-3
      and 0.0 < rows[-1][1] / tip_formula - 1 < 0.02)
print("ALL CHECKS PASSED" if ok else "CHECK FAILED")

ax = axes[1]
ax.plot([r[0] for r in rows], [1000 * r[1] for r in rows], "o-",
        color="#6b4fa0", lw=2, label="FEM, quadratic (P2)")
ax.plot([r[0] for r in rows_p1], [1000 * r[1] for r in rows_p1], "s-",
        color="#a8324a", lw=2, label="FEM, linear (P1)")
ax.axhline(1000 * tip_formula, color="#8a6a12", ls="--", label="P L^3/(3EI)")
ax.set_xscale("log")
ax.set_xlabel("number of triangles")
ax.set_ylabel("tip deflection (mm)")
ax.set_title("Beam: refine until it stops changing")
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(out / "fem_plate_and_beam.png", dpi=120)
