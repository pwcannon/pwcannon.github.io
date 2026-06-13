"""
Canonical generator for the live contour orb (11 June 2026).

The orb is a POSTERIOR-DRAWS INK WASH of a 3-component gaussian mixture:
each of the 14 bands is the level set of a *different* resample of the
mixture (means/covariances/weights jittered per band), so the wandering
band edges depict estimation uncertainty rather than decorative noise —
"one distribution, known only through inference."

The mixture itself (MIXTURE below) was selected from a generated batch of
non-collinear triangular candidates ("tri_09_subtle": two soft cores,
saddle ratio 0.78, contiguous skirt). Orientation/position on the page are
CSS (.contour-orb: rotate(15deg), top/right offsets) — not baked in here.

Deterministic: seed 29 reproduces _includes/contour_orb.html exactly.
Rendering constants/helpers are imported from generate_contours.py
(unmodified) via orb_numpy_compat (pure-numpy scipy/skimage stand-ins).

Usage:  python3 make_orb_inkwash.py          # writes orb_inkwash.svg here
        python3 make_orb_inkwash.py --include # ALSO rewrites _includes/contour_orb.html
"""

import copy
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from orb_numpy_compat import find_contours, load_orb_module

gc = load_orb_module()

MIXTURE = [
    {'mean': [272.0, 288.0], 'cov': [[7697.0, 700.0], [700.0, 6283.0]], 'weight': 0.512},
    {'mean': [443.0, 205.0], 'cov': [[5672.0, -930.0], [-930.0, 5705.0]], 'weight': 0.284},
    {'mean': [461.0, 486.0], 'cov': [[6165.0, -961.0], [-961.0, 7475.0]], 'weight': 0.204},
]

SEED = 29
N_BANDS = 14

# Band ablation (12 Jun 2026, Patrick, leave-one-out eye test): bands 11, 12,
# 14 (1-indexed) are not emitted. Their perturbation draws STILL RUN so the
# rng sequence — and therefore every surviving band — is identical to the
# original 14-band orb. Card generator mirrors this (make_brand_assets.py).
SKIP_BANDS = {10, 11, 13}  # 0-indexed

rng = np.random.default_rng(SEED)  # module default; seeded locally in svg_body


def perturbed(comps, rng=None):
    """One posterior-style resample of the mixture parameters."""
    if rng is None:
        rng = globals()['rng']
    c2 = copy.deepcopy(comps)
    w = []
    for comp in c2:
        comp['mean'] = [m + rng.normal(0, 10) for m in comp['mean']]
        cv = np.array(comp['cov'], float) * float(np.exp(rng.normal(0, 0.08)))
        cv[0, 1] = cv[1, 0] = cv[0, 1] * float(np.exp(rng.normal(0, 0.10)))
        if np.linalg.eigvalsh(cv).min() <= 200:
            cv = np.array(comp['cov'], float)
        comp['cov'] = cv.tolist()
        w.append(comp['weight'] * float(np.exp(rng.normal(0, 0.08))))
    w = np.array(w)
    w /= w.sum()
    for comp, wi in zip(c2, w):
        comp['weight'] = float(wi)
    return c2


def bezier_d(P, step=4):
    """Closed Catmull-Rom spline through every `step`-th point, as cubic Beziers."""
    if np.allclose(P[0], P[-1]):
        P = P[:-1]
    if len(P) > 3 * step:
        P = P[::step]
    n = len(P)
    if n < 4:
        return None
    parts = [f'M {P[0][0]:.1f} {P[0][1]:.1f}']
    for i in range(n):
        p0, p1, p2, p3 = P[(i - 1) % n], P[i], P[(i + 1) % n], P[(i + 2) % n]
        c1 = p1 + (p2 - p0) / 6.0
        c2 = p2 - (p3 - p1) / 6.0
        parts.append(f'C {c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}')
    parts.append('Z')
    return ' '.join(parts)


def mixture_mode():
    """Argmax of the UNPERTURBED mixture density (the central estimate)."""
    px, py, PZ = gc.evaluate_mixture(MIXTURE, 800, gc.VIEWBOX_W, gc.VIEWBOX_H)
    iy, ix = np.unravel_index(PZ.argmax(), PZ.shape)
    return px[ix], py[iy]


def ensemble_avg_density(seed=SEED, res=600):
    """Ensemble-average density over the SHOWN resamples (separate rng
    pass with the same sequence; does not disturb band generation)."""
    rng2 = np.random.default_rng(seed)
    avg = None
    for bi in range(N_BANDS):
        cset = perturbed(MIXTURE, rng2)
        if bi in SKIP_BANDS:
            continue
        px, py, PZ = gc.evaluate_mixture(cset, res, gc.VIEWBOX_W, gc.VIEWBOX_H)
        avg = PZ if avg is None else avg + PZ
    return px, py, avg / (N_BANDS - len(SKIP_BANDS))


def ensemble_mode(seed=SEED):
    """Argmax of the ensemble-average density (the global, upper mode)."""
    px, py, avg = ensemble_avg_density(seed)
    iy, ix = np.unravel_index(avg.argmax(), avg.shape)
    return px[ix], py[iy]


def ensemble_mode_lower(seed=SEED):
    """LOCAL mode of the ensemble average in the lower lobe (y > 410)."""
    px, py, avg = ensemble_avg_density(seed)
    mask = np.zeros_like(avg, bool)
    mask[py > 410, :] = True
    masked = np.where(mask, avg, -np.inf)
    iy, ix = np.unravel_index(masked.argmax(), masked.shape)
    return px[ix], py[iy]


def sampler_path(seed=SEED, n=46):
    """Smooth, gently wandering trajectory between the two modes.

    Elastic-band relaxation: start from the straight chord, iteratively
    nudge interior points uphill along the density gradient (perpendicular
    component only, endpoints pinned, neighbour-smoothing each step) so the
    path bows through the saddle — the mountain-pass route a Langevin-ish
    sampler would drift along — then add a small seeded tapered wander."""
    px, py, avg = ensemble_avg_density(seed)
    logp = np.log(avg + avg.max() * 1e-6)
    gy, gx = np.gradient(logp)         # row-grad (y), col-grad (x)
    dx, dy = px[1] - px[0], py[1] - py[0]

    def grad_at(p):
        ix = np.clip(np.searchsorted(px, p[0]), 1, len(px) - 2)
        iy = np.clip(np.searchsorted(py, p[1]), 1, len(py) - 2)
        return np.array([gx[iy, ix] / dx, gy[iy, ix] / dy])

    p1, p2 = np.array(ensemble_mode(seed)), np.array(ensemble_mode_lower(seed))
    pts = np.linspace(p1, p2, n)
    for _ in range(60):
        tang = np.gradient(pts, axis=0)
        tang /= np.linalg.norm(tang, axis=1, keepdims=True) + 1e-9
        g = np.array([grad_at(p) for p in pts])
        g_perp = g - (g * tang).sum(1, keepdims=True) * tang
        norm = np.linalg.norm(g_perp, axis=1, keepdims=True) + 1e-9
        step = g_perp / norm * np.clip(norm * 300, 0, 1.2)   # capped uphill step
        step[0] = step[-1] = 0
        pts = pts + step
        pts[1:-1] = 0.25 * pts[:-2] + 0.5 * pts[1:-1] + 0.25 * pts[2:]  # smooth
    # rounder bow (Patrick, 12 Jun 2026, after the real-dynamics detour was
    # judged too complicated for a simple graphic): amplify the path's
    # deviation from the straight chord — endpoints pinned, arc fuller.
    BOW = 1.35
    t = np.linspace(0, 1, n)
    chord_t = p1 + t[:, None] * (p2 - p1)
    pts = chord_t + BOW * (pts - chord_t)
    # gentle seeded wander, zero at both ends
    wrng = np.random.default_rng(seed + 1)
    phase = wrng.uniform(0, 2 * np.pi)
    tang = np.gradient(pts, axis=0)
    tang /= np.linalg.norm(tang, axis=1, keepdims=True) + 1e-9
    normal = np.column_stack([-tang[:, 1], tang[:, 0]])
    wander = 4.0 * np.sin(t * np.pi * 2.5 + phase) * np.sin(t * np.pi)
    return pts + normal * wander[:, None]


def trim_to_halo(pts, centre, R, from_start):
    """Cut the polyline where it enters a radius-R halo around centre,
    landing the new endpoint exactly on the halo boundary."""
    pts = np.asarray(pts, float)
    c = np.asarray(centre, float)
    d = np.linalg.norm(pts - c, axis=1)
    idx = range(len(pts)) if from_start else range(len(pts) - 1, -1, -1)
    prev = None
    for i in idx:
        if d[i] > R:
            if prev is None:
                return pts if from_start else pts
            a, b = pts[prev], pts[i]          # a inside halo, b outside
            da, db = d[prev], d[i]
            t = (R - da) / (db - da)
            edge = a + t * (b - a)
            if from_start:
                return np.vstack([edge, pts[i:]])
            return np.vstack([pts[:prev], edge])
        prev = i
    return pts


def open_bezier_d(P):
    """Open Catmull-Rom spline through P, as cubic Beziers."""
    P = np.asarray(P, float)
    n = len(P)
    parts = [f'M {P[0][0]:.1f} {P[0][1]:.1f}']
    for i in range(n - 1):
        p0 = P[max(i - 1, 0)]
        p1, p2 = P[i], P[i + 1]
        p3 = P[min(i + 2, n - 1)]
        c1 = p1 + (p2 - p0) / 6.0
        c2 = p2 - (p3 - p1) / 6.0
        parts.append(f'C {c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}')
    return ' '.join(parts)


# Site rotation applied by CSS (.contour-orb transform) — the label group
# counter-rotates by this so the mathematics reads level on the page.
# KEEP IN SYNC with style.css.
CSS_ROT_DEG = 7.5

LABEL_TEX = r'$\hat{\theta} = \arg\max_{\theta}\ \bar{p}(\theta \mid x)$'
LABEL_HEIGHT = 26   # orb units, bbox height of the rendered expression


def label_paths(ax, ay):
    """LABEL_TEX as SVG path data (Computer Modern outlines via matplotlib
    TextPath — vectors, no font dependency in the page). Anchored with left
    edge at (ax, ay), vertically centred, counter-rotated to page-level."""
    import matplotlib
    matplotlib.rcParams['mathtext.fontset'] = 'cm'   # Computer Modern, as comped
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    from matplotlib.path import Path as MplPath
    tp = TextPath((0, 0), LABEL_TEX, size=100, prop=FontProperties())
    v = tp.vertices
    x0, y0, x1, y1 = v[:, 0].min(), v[:, 1].min(), v[:, 0].max(), v[:, 1].max()
    s = LABEL_HEIGHT / (y1 - y0)

    def tx(p):
        # scale, y-flip (TextPath is y-up, SVG y-down), centre vertically
        return ((p[0] - x0) * s, -(p[1] - (y0 + y1) / 2) * s)

    parts = []
    i = 0
    verts, codes = tp.vertices, tp.codes
    while i < len(codes):
        c = codes[i]
        if c == MplPath.MOVETO:
            p = tx(verts[i]); parts.append(f'M{p[0]:.2f} {p[1]:.2f}'); i += 1
        elif c == MplPath.LINETO:
            p = tx(verts[i]); parts.append(f'L{p[0]:.2f} {p[1]:.2f}'); i += 1
        elif c == MplPath.CURVE3:
            q1, q2 = tx(verts[i]), tx(verts[i + 1])
            parts.append(f'Q{q1[0]:.2f} {q1[1]:.2f} {q2[0]:.2f} {q2[1]:.2f}'); i += 2
        elif c == MplPath.CURVE4:
            c1, c2, p2 = tx(verts[i]), tx(verts[i + 1]), tx(verts[i + 2])
            parts.append(f'C{c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} '
                         f'{p2[0]:.2f} {p2[1]:.2f}'); i += 3
        elif c == MplPath.CLOSEPOLY:
            parts.append('Z'); i += 1
        else:
            i += 1
    d = ' '.join(parts)
    return (f'  <g class="mode-label" transform="translate({ax:.1f} {ay:.1f}) '
            f'rotate({-CSS_ROT_DEG})">\n    <path d="{d}"/>\n  </g>')


def svg_body(seed=SEED):
    """Full orb SVG for a given resample seed (band config/colours fixed).

    Annotation layer (12 Jun 2026, evolved through the day): white crosses
    at BOTH modes of the ensemble-average density (global upper + local
    lower lobe, the lower cross smaller in proportion to its mode height),
    joined by a thin densely-dashed sampler trajectory along the
    conditional ridge (sampler_path). The earlier equation label was
    retired in favour of this. Everything sits inside the single blur
    group, beneath the page grain; colours/styling come from CSS
    (.mode-marker / .mode-path)."""
    rng = np.random.default_rng(seed)
    # THE one blur dial (12 Jun 2026): everything — bands, cross, label —
    # sits in this single filter (the old element-level CSS blur is gone).
    # SETTLED at 1 by live eye test (Patrick, 12 Jun 2026). History:
    # 2.75-equivalent (launch look), 2.3, 1.8 intermediate steps. Live-tune:
    # document.querySelector('#iw feGaussianBlur').setAttribute('stdDeviation', N)
    L = ['<svg viewBox="-100 -100 1000 900" xmlns="http://www.w3.org/2000/svg" style="overflow:visible;">',
         '  <defs><filter id="iw"><feGaussianBlur stdDeviation="1"/></filter></defs>',
         '  <g filter="url(#iw)">']
    fracs = np.linspace(0.04, 0.92, N_BANDS)
    alphas = np.linspace(0.03, 0.58, N_BANDS)
    for bi, (fr, a_) in enumerate(zip(fracs, alphas)):
        cset = perturbed(MIXTURE, rng)  # must run even for skipped bands (rng sequence)
        if bi in SKIP_BANDS:
            continue
        px, py, PZ = gc.evaluate_mixture(cset, gc.GRID_SIZE, gc.VIEWBOX_W, gc.VIEWBOX_H)
        lv = fr * PZ.max()
        r, g, b, _ = gc.interpolate_color(bi / (N_BANDS - 1), gc.FILL_COLOR_OUTER, gc.FILL_COLOR_INNER)
        for cc in find_contours(PZ, lv):
            P = np.column_stack([np.interp(cc[:, 1], np.arange(len(px)), px),
                                 np.interp(cc[:, 0], np.arange(len(py)), py)])
            d = bezier_d(P)
            if d:
                L.append(f'    <path d="{d}" fill="rgba({int(r)},{int(g)},{int(b)},{a_:.3f})" stroke="none" />')
    px_, py_, avg = ensemble_avg_density(seed)
    (mx, my), (lx, ly) = ensemble_mode(seed), ensemble_mode_lower(seed)
    h1 = avg[np.argmin(np.abs(py_ - my)), np.argmin(np.abs(px_ - mx))]
    h2 = avg[np.argmin(np.abs(py_ - ly)), np.argmin(np.abs(px_ - lx))]
    arm1, arm2 = 10.0, max(6.0, 10 * (h2 / h1) ** 0.5)  # smaller mode, smaller cross

    # trajectory gradient: white at the upper mode -> darkest theme ink at
    # the lower (the lower cross's colour). userSpaceOnUse along the chord.
    L.insert(1, f'  <defs><linearGradient id="trajgrad" gradientUnits="userSpaceOnUse" '
                f'x1="{mx:.1f}" y1="{my:.1f}" x2="{lx:.1f}" y2="{ly:.1f}">'
                f'<stop offset="0" stop-color="rgba(255,255,255,0.92)"/>'
                f'<stop offset="1" stop-color="rgba(10,30,46,0.92)"/>'
                f'</linearGradient></defs>')

    # sampler trajectory FIRST (under the crosses), trimmed so it never
    # touches the crosses: a clearance halo ("force field") around each.
    traj = sampler_path(seed)
    traj = trim_to_halo(traj, (mx, my), arm1 + 7, from_start=True)
    traj = trim_to_halo(traj, (lx, ly), arm2 + 7, from_start=False)
    L.append(f'    <path class="mode-path" stroke="url(#trajgrad)" d="{open_bezier_d(traj)}" />')

    def cross(cx, cy, arm, variant):
        return (f'    <g transform="rotate({-CSS_ROT_DEG} {cx:.1f} {cy:.1f})">\n'
                f'      <path class="mode-marker mode-marker--{variant}" '
                f'd="M{cx-arm:.1f} {cy:.1f}L{cx+arm:.1f} {cy:.1f}'
                f'M{cx:.1f} {cy-arm:.1f}L{cx:.1f} {cy+arm:.1f}" fill="none" stroke-linecap="round" />\n'
                f'    </g>')

    L.append(cross(mx, my, arm1, 'upper'))
    L.append(cross(lx, ly, arm2, 'lower'))
    L.append('  </g>')
    L.append('</svg>')
    return '\n'.join(L)


def main():
    # --seed N: build an alternate resample; --asset: write to
    # assets/img/orb/orb_seedN.svg (used by the A/B switcher, orb_ab.html)
    seed = SEED
    if '--seed' in sys.argv:
        seed = int(sys.argv[sys.argv.index('--seed') + 1])
    svg = svg_body(seed)

    if '--asset' in sys.argv:
        dest_dir = HERE.parent / 'assets' / 'img' / 'orb'
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f'orb_seed{seed}.svg'
        dest.write_text(svg + '\n')
        print(f'{dest} written ({len(svg) // 1024} KB)')
        return

    (HERE / 'orb_inkwash.svg').write_text(svg)
    print(f'orb_inkwash.svg written ({len(svg) // 1024} KB)')

    if '--include' in sys.argv:
        header = '''<!--
  Contour orb: POSTERIOR-DRAWS INK WASH (11 bands; 11/12/14 ablated 12 Jun 2026).
  Each band is the level set of a different resample of a 3-component
  gaussian mixture — the edge wander depicts estimation uncertainty.
  Generated by _design/make_orb_inkwash.py (seed 29, deterministic).
  Orientation/position are CSS (.contour-orb). Dark field: pairs with
  the bright-on-dark nav.
-->
<div class="contour-orb">
'''
        (HERE.parent / '_includes' / 'contour_orb.html').write_text(header + svg + '\n</div>')
        print('_includes/contour_orb.html rewritten')


if __name__ == '__main__':
    main()
