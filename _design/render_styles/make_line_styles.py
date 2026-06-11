"""
Refined contour-line orb + independent nav treatments (11 June 2026).

v2: smooth curves. v1 reused generate_contours.py's extract_contours, which
decimates to every 3rd point and rounds coordinates to integers — invisible
under the fill's blur, visibly jagged on crisp 0.9px hairlines. v2 extracts
contours at full grid resolution, resamples lightly, and emits Catmull-Rom
cubic Beziers with 0.1px precision.

Outputs: line_styles.html (contact sheet) and refreshes
../../_includes/orb_lines.html when run with --include.
"""

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from orb_numpy_compat import find_contours, load_orb_module

gc = load_orb_module()

man = json.loads((HERE.parent / 'variations_tri' / 'tri_manifest.json').read_text())
COMPS = next(m for m in man if m['file'] == 'tri_09_subtle.svg')['components']

x, y, Z = gc.evaluate_mixture(COMPS, gc.GRID_SIZE, gc.VIEWBOX_W, gc.VIEWBOX_H)
ZMAX = Z.max()

N_LINES = 9
levels = np.linspace(ZMAX * 0.06, ZMAX * 0.90, N_LINES)


def full_res_contours(level):
    """Contours in SVG coords, full resolution, no decimation."""
    out = []
    for cc in find_contours(Z, level):
        coords = np.column_stack([
            np.interp(cc[:, 1], np.arange(len(x)), x),
            np.interp(cc[:, 0], np.arange(len(y)), y),
        ])
        out.append(coords)
    return out


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


CONTOURS = [full_res_contours(lv) for lv in levels]


def line_svg(wash=False):
    lines = ['<svg viewBox="-100 -100 1000 900" xmlns="http://www.w3.org/2000/svg" style="overflow:visible;">']
    if wash:
        for lc in CONTOURS:
            for cc in lc:
                d = bezier_d(cc)
                if d:
                    lines.append(f'  <path d="{d}" fill="rgba(70,100,140,0.012)" stroke="none" />')
    for i, lc in enumerate(CONTOURS):
        a = 0.10 + 0.025 * i
        w = 0.9 if i < N_LINES - 2 else 1.1
        for cc in lc:
            d = bezier_d(cc)
            if d:
                lines.append(f'  <path d="{d}" fill="none" stroke="rgba(60,90,130,{a:.3f})" '
                             f'stroke-width="{w}" stroke-linejoin="round" />')
    lines.append('</svg>')
    return '\n'.join(lines)


SVG_PLAIN = line_svg(False)
SVG_WASH = line_svg(True)

TILES = [
    ('1 — fine lines, ink nav',
     'Nine isolines, 0.9px, opacity .10–.30. Nav in page ink with rose underline — no backing needed.',
     SVG_PLAIN, 'nav-ink', False),
    ('2 — fine lines + whisper wash, ink nav',
     'Same lines over a ~10% cumulative fill so the region has a faint body.',
     SVG_WASH, 'nav-ink', False),
    ('3 — fine lines, frosted-pill nav',
     'Nav sits on a translucent blurred chip; lines pass behind it.',
     SVG_PLAIN, 'nav-frost', False),
    ('4 — fine lines, clearing behind nav',
     'CSS radial mask dissolves the lines around the nav — the field quietly gives way.',
     SVG_PLAIN, 'nav-ink', True),
    ('5 — clearing + rose active',
     'As 4, with the active item in the site accent instead of an underline.',
     SVG_PLAIN, 'nav-rose', True),
]

tiles_html = []
for name, blurb, svg, navcls, clearing in TILES:
    orbcls = 'orb orb-clear' if clearing else 'orb'
    tiles_html.append(f'''<div class="tile">
<div class="corner">
  <div class="{orbcls}">{svg}</div>
  <div class="pnav {navcls}"><span class="on">home</span><span>blog</span><span>research</span></div>
</div>
<p class="cap"><strong>{name}</strong><br>{blurb}</p>
</div>''')

html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Refined contour lines + independent nav (v2 smooth)</title>
<style>
body {{ font-family: 'DM Sans', -apple-system, sans-serif; background: #fff; margin: 24px; color: #0A1E2E; }}
h1 {{ font-size: 20px; }} p.note {{ font-size: 13px; color: #3A6080; max-width: 72ch; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(460px, 1fr)); gap: 20px; margin-top: 18px; }}
.corner {{ position: relative; height: 400px; overflow: hidden; border-radius: 6px;
          border: 1px solid rgba(160,185,210,.45);
          background: linear-gradient(175deg, #EDF2F7 0%, #E4EDF5 40%, #EEF0F4 100%); }}
.orb {{ position: absolute; top: -130px; right: -140px; width: 520px; height: 460px;
       transform: rotate(15deg); pointer-events: none; }}
.orb svg {{ width: 100%; height: 100%; }}
.orb-clear {{ -webkit-mask-image: radial-gradient(ellipse 240px 110px at 72% 32%, transparent 0 40%, black 78%);
             mask-image: radial-gradient(ellipse 240px 110px at 72% 32%, transparent 0 40%, black 78%); }}
.pnav {{ position: absolute; top: 20px; right: 22px; display: flex; gap: 16px; font-size: 12px; font-weight: 500; }}
.nav-ink span {{ color: #3A6080; }}
.nav-ink span.on {{ color: #0A1E2E; font-weight: 600; border-bottom: 2px solid rgba(200,140,170,0.85); padding-bottom: 3px; }}
.nav-frost {{ background: rgba(240,245,250,0.55); border: 1px solid rgba(255,255,255,0.6);
             border-radius: 8px; padding: 8px 14px;
             backdrop-filter: blur(8px) saturate(1.1); -webkit-backdrop-filter: blur(8px) saturate(1.1); }}
.nav-frost span {{ color: #3A6080; }}
.nav-frost span.on {{ color: #0A1E2E; font-weight: 600; border-bottom: 2px solid rgba(200,140,170,0.85); padding-bottom: 3px; }}
.nav-rose span {{ color: #3A6080; }}
.nav-rose span.on {{ color: #A05C7E; font-weight: 600; }}
.cap {{ font-size: 12.5px; color: #3A6080; margin: 8px 4px 2px; line-height: 1.5; }}
.cap strong {{ color: #0A1E2E; }}
</style></head><body>
<h1>Refined contour lines (smooth Beziers) + nav that stands on its own</h1>
<p class="note">v2: full-resolution contours as Catmull-Rom cubic Beziers, 0.1px
precision — no decimation, no integer rounding, no facets.</p>
<div class="grid">
{''.join(tiles_html)}
</div>
</body></html>'''

(HERE / 'line_styles.html').write_text(html)
print(f'line_styles.html written ({len(html) / 1024:.0f} KB)')

if '--include' in sys.argv:
    header = '''<!--
  Orb treatment: FINE LINES (v2 smooth) — nine isolines of the tri_09_subtle
  mixture as Catmull-Rom cubic Beziers, 0.9px strokes at 10-30% opacity.
  Pairs with the ink-nav CSS block and the .contour-orb--lines modifier.
  Generated by _design/render_styles/make_line_styles.py --include
-->
<div class="contour-orb contour-orb--lines">
'''
    (HERE.parent.parent / '_includes' / 'orb_lines.html').write_text(header + SVG_PLAIN + '\n</div>')
    print('orb_lines.html refreshed')
