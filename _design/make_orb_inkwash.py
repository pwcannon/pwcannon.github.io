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


def ensemble_mode(seed=SEED):
    """Argmax of the ensemble-average density over the SHOWN resamples.

    The marker notation reads argmax of p-bar, so the cross sits at the
    mode of the average of the 11 displayed densities — not the central
    mixture's mode. Separate rng pass; does not disturb band generation."""
    rng2 = np.random.default_rng(seed)
    avg = None
    for bi in range(N_BANDS):
        cset = perturbed(MIXTURE, rng2)   # same sequence as the bands
        if bi in SKIP_BANDS:
            continue
        px, py, PZ = gc.evaluate_mixture(cset, 600, gc.VIEWBOX_W, gc.VIEWBOX_H)
        avg = PZ if avg is None else avg + PZ
    iy, ix = np.unravel_index(avg.argmax(), avg.shape)
    return px[ix], py[iy]


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

    Includes the posterior-mode marker (12 Jun 2026): a small rose plus at
    the central mixture's mode — point estimate against the uncertainty
    wash. Lives INSIDE the blur group so it reads as part of the wash;
    the page grain overlay paints over it (grain include is after
    .page-wrapper). Colour comes from CSS (.contour-orb .mode-marker,
    rgba(var(--accent-rose),...)), keeping the accent single-sourced."""
    rng = np.random.default_rng(seed)
    # stdDeviation 2.75 = the old 2.0 with the former CSS blur(1.5px)
    # folded in (removed from .contour-orb 12 Jun 2026 so the mode-label
    # outside this group renders truly crisp; band softness unchanged).
    L = ['<svg viewBox="-100 -100 1000 900" xmlns="http://www.w3.org/2000/svg" style="overflow:visible;">',
         '  <defs><filter id="iw"><feGaussianBlur stdDeviation="2.75"/></filter></defs>',
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
    mx, my = ensemble_mode(seed)
    arm = 10
    # cross counter-rotates about its centre (stays in the blur group for
    # the soft wash look, but reads level on the page like the label)
    L.append(f'    <g transform="rotate({-CSS_ROT_DEG} {mx:.1f} {my:.1f})">')
    L.append(f'      <path class="mode-marker" d="M{mx-arm:.1f} {my:.1f}L{mx+arm:.1f} {my:.1f}'
             f'M{mx:.1f} {my-arm:.1f}L{mx:.1f} {my+arm:.1f}" fill="none" stroke-linecap="round" />')
    L.append('    </g>')
    L.append('  </g>')
    # label OUTSIDE the blur group: crisp annotation against the soft wash,
    # still beneath the page grain overlay. Anchored at the cross's
    # bottom-right corner IN PAGE SPACE (both elements are counter-rotated,
    # so the desired page offset maps through the inverse CSS rotation).
    page_dx, page_dy = arm + 3, arm + LABEL_HEIGHT / 2 + 2
    th = np.deg2rad(-CSS_ROT_DEG)
    ax = mx + page_dx * np.cos(th) - page_dy * np.sin(th)
    ay = my + page_dx * np.sin(th) + page_dy * np.cos(th)
    L.append(label_paths(ax, ay))
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
