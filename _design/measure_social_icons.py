"""Measure + render the social icon SVG paths from _layouts/default.html.

Justifies the per-icon sizes in style.css (.social-icons nth-child rules):
glyphs fill different fractions of their 24-unit viewBoxes, so equal CSS
sizes render unequal optical sizes. Measured 12 Jun 2026:
  scholar 23.8x24.0 of 24 | github 24.0x23.4 | linkedin 17.1x17.2 | twitter 18.8x15.6
-> normalized sizes 20/20/26/24 px (blend of bbox- and ink-weight-equalization).

Implementation (no SVG renderer needed):
mini path parser (M/L/H/V/C/S/A/Z + relatives), arcs via endpoint
parametrization, even-odd fill through matplotlib Agg."""
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch

NUM = re.compile(r'[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?')


def parse(d):
    tokens = re.findall(r'[MmLlHhVvCcSsQqAaZz]|' + NUM.pattern, d)
    i, cmd, cur, start = 0, None, np.zeros(2), np.zeros(2)
    prev_c2 = None
    subpaths, pts = [], []

    def num():
        nonlocal i
        v = float(tokens[i]); i += 1
        return v

    def flush():
        nonlocal pts
        if len(pts) > 2:
            subpaths.append(np.array(pts))
        pts = []

    while i < len(tokens):
        t = tokens[i]
        if re.match(r'[A-Za-z]', t):
            cmd = t; i += 1
        elif cmd is None:
            raise ValueError('number before command')
        c = cmd
        if c in 'Mm':
            xy = np.array([num(), num()])
            cur = xy if c == 'M' else cur + xy
            flush(); start = cur.copy(); pts = [cur.copy()]
            cmd = 'L' if c == 'M' else 'l'
            prev_c2 = None
        elif c in 'Ll':
            xy = np.array([num(), num()])
            cur = xy if c == 'L' else cur + xy
            pts.append(cur.copy()); prev_c2 = None
        elif c in 'Hh':
            x = num()
            cur = np.array([x, cur[1]]) if c == 'H' else cur + [x, 0]
            pts.append(cur.copy()); prev_c2 = None
        elif c in 'Vv':
            y = num()
            cur = np.array([cur[0], y]) if c == 'V' else cur + [0, y]
            pts.append(cur.copy()); prev_c2 = None
        elif c in 'CcSs':
            if c in 'Cc':
                c1 = np.array([num(), num()]); c2 = np.array([num(), num()])
                p2 = np.array([num(), num()])
                if c == 'c': c1, c2, p2 = cur + c1, cur + c2, cur + p2
            else:
                c1 = 2 * cur - prev_c2 if prev_c2 is not None else cur.copy()
                c2 = np.array([num(), num()]); p2 = np.array([num(), num()])
                if c == 's': c2, p2 = cur + c2, cur + p2
            ts = np.linspace(0, 1, 24)[1:, None]
            seg = ((1-ts)**3*cur + 3*(1-ts)**2*ts*c1 + 3*(1-ts)*ts**2*c2 + ts**3*p2)
            pts.extend(seg); prev_c2 = c2; cur = p2
        elif c in 'Aa':
            rx, ry, rot, laf, sf = num(), num(), num(), num(), num()
            p2 = np.array([num(), num()])
            if c == 'a': p2 = cur + p2
            seg = arc_points(cur, p2, rx, ry, rot, laf, sf)
            pts.extend(seg); cur = p2; prev_c2 = None
        elif c in 'Zz':
            pts.append(start.copy()); cur = start.copy()
            flush(); i += 0; prev_c2 = None
        else:
            raise ValueError(c)
    flush()
    return subpaths


def arc_points(p1, p2, rx, ry, rot_deg, laf, sf, n=32):
    """W3C endpoint -> center parametrization, sampled."""
    if rx == 0 or ry == 0 or np.allclose(p1, p2):
        return [p2]
    phi = np.deg2rad(rot_deg)
    R = np.array([[np.cos(phi), np.sin(phi)], [-np.sin(phi), np.cos(phi)]])
    p1p = R @ (p1 - p2) / 2
    lam = (p1p[0]/rx)**2 + (p1p[1]/ry)**2
    if lam > 1:
        s = np.sqrt(lam); rx, ry = s*rx, s*ry
    num_ = rx**2*ry**2 - rx**2*p1p[1]**2 - ry**2*p1p[0]**2
    den = rx**2*p1p[1]**2 + ry**2*p1p[0]**2
    co = np.sqrt(max(0, num_/den)) * (1 if laf != sf else -1)
    cp = co * np.array([rx*p1p[1]/ry, -ry*p1p[0]/rx])
    ctr = R.T @ cp + (p1 + p2)/2
    def ang(v):
        return np.arctan2(v[1], v[0])
    v1 = (p1p - cp) / [rx, ry]
    v2 = (-p1p - cp) / [rx, ry]
    th1 = ang(v1)
    dth = ang(v2) - th1
    if sf == 0 and dth > 0: dth -= 2*np.pi
    if sf == 1 and dth < 0: dth += 2*np.pi
    ts = th1 + dth*np.linspace(0, 1, n)[1:]
    pts = np.stack([rx*np.cos(ts), ry*np.sin(ts)], 1)
    return list(pts @ np.array([[np.cos(phi), np.sin(phi)],
                                [-np.sin(phi), np.cos(phi)]]) + ctr)


def render(subpaths, size=240, box=24):
    verts, codes = [], []
    for sp in subpaths:
        verts.extend(sp); codes.extend([MplPath.MOVETO] + [MplPath.LINETO]*(len(sp)-1))
    fig = plt.figure(figsize=(1, 1), dpi=size)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis('off')
    ax.set_xlim(0, box); ax.set_ylim(box, 0)
    ax.add_patch(PathPatch(MplPath(verts, codes), facecolor='black',
                           edgecolor='none', fill=True))
    fig.canvas.draw()
    a = np.asarray(fig.canvas.buffer_rgba())[..., :3].mean(-1)
    plt.close(fig)
    return (a < 128)  # ink mask


def measure(name, d):
    mask = render(parse(d))
    ys, xs = np.nonzero(mask)
    S = mask.shape[0]
    w, h = (xs.max()-xs.min()+1)/S*24, (ys.max()-ys.min()+1)/S*24
    area = mask.sum()/S/S * 24*24
    return dict(name=name, w=w, h=h, maxdim=max(w, h), area=area, mask=mask)
