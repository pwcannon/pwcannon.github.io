"""Social icon roundel set (decided 12 Jun 2026): every mark is its glyph
knocked out of a solid 24-unit disc — the GitHub mark's grammar extended
to the rest. Scholar uses the mortarboard alone (the layered cap+lens
mark dissolves under knockout; accepted trade-off). X glyph: Simple
Icons path, visually verified. Emits the path data used in
_layouts/default.html (fill-rule="evenodd" on constructed paths;
the github mark ships verbatim as the dialect anchor).

Command-level SVG path transform: parse to absolute commands, uniform
scale + translate, serialize. Usage: python3 make_social_roundels.py"""
import re
import numpy as np

NUM = re.compile(r'[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?')


def parse_abs(d):
    """Parse path data to a list of absolute commands [(cmd, [args...])]."""
    tokens = re.findall(r'[MmLlHhVvCcSsQqAaZz]|' + NUM.pattern, d)
    i, cmd = 0, None
    cur = np.zeros(2); start = np.zeros(2)
    out = []

    def num():
        nonlocal i
        v = float(tokens[i]); i += 1
        return v

    while i < len(tokens):
        if re.match(r'[A-Za-z]', tokens[i]):
            cmd = tokens[i]; i += 1
        c = cmd
        if c in 'Mm':
            xy = np.array([num(), num()])
            cur = xy if c == 'M' else cur + xy
            start = cur.copy()
            out.append(('M', list(cur)))
            cmd = 'L' if c == 'M' else 'l'
        elif c in 'Ll':
            xy = np.array([num(), num()])
            cur = xy if c == 'L' else cur + xy
            out.append(('L', list(cur)))
        elif c in 'Hh':
            x = num()
            cur = np.array([x, cur[1]]) if c == 'H' else cur + [x, 0]
            out.append(('L', list(cur)))
        elif c in 'Vv':
            y = num()
            cur = np.array([cur[0], y]) if c == 'V' else cur + [0, y]
            out.append(('L', list(cur)))
        elif c in 'CcSs':
            if c in 'Cc':
                c1 = np.array([num(), num()]); c2 = np.array([num(), num()])
                p2 = np.array([num(), num()])
                if c == 'c': c1, c2, p2 = cur + c1, cur + c2, cur + p2
            else:
                prev = out[-1]
                if prev[0] == 'C':
                    pc2 = np.array(prev[1][2:4])
                    c1 = 2 * cur - pc2
                else:
                    c1 = cur.copy()
                c2 = np.array([num(), num()]); p2 = np.array([num(), num()])
                if c == 's': c2, p2 = cur + c2, cur + p2
            out.append(('C', list(c1) + list(c2) + list(p2)))
            cur = p2
        elif c in 'Aa':
            rx, ry, rot, laf, sf = num(), num(), num(), num(), num()
            p2 = np.array([num(), num()])
            if c == 'a': p2 = cur + p2
            out.append(('A', [rx, ry, rot, laf, sf] + list(p2)))
            cur = p2
        elif c in 'Zz':
            out.append(('Z', []))
            cur = start.copy()
    return out


def transform(cmds, s, tx, ty):
    """Uniform scale then translate, on absolute commands."""
    res = []
    for c, a in cmds:
        if c in 'ML':
            res.append((c, [a[0]*s+tx, a[1]*s+ty]))
        elif c == 'C':
            res.append((c, [a[i]*s + (tx if i % 2 == 0 else ty) for i in range(6)]))
        elif c == 'A':
            rx, ry, rot, laf, sf, x, y = a
            res.append((c, [rx*s, ry*s, rot, laf, sf, x*s+tx, y*s+ty]))
        else:
            res.append((c, a))
    return res


def serialize(cmds):
    parts = []
    for c, a in cmds:
        if c == 'Z':
            parts.append('Z')
        elif c == 'A':
            rx, ry, rot, laf, sf, x, y = a
            parts.append(f'A{rx:.2f} {ry:.2f} {rot:g} {int(laf)} {int(sf)} {x:.2f} {y:.2f}')
        else:
            parts.append(c + ' '.join(f'{v:.2f}' for v in a))
    return ' '.join(parts)


def glyph_bbox(cmds):
    """Crude bbox over command coordinates (endpoints + control points)."""
    xs, ys = [], []
    for c, a in cmds:
        if c in 'ML':
            xs.append(a[0]); ys.append(a[1])
        elif c == 'C':
            xs += a[0::2]; ys += a[1::2]
        elif c == 'A':
            xs.append(a[5]); ys.append(a[6])
    return min(xs), min(ys), max(xs), max(ys)


DISC = 'M12 0A12 12 0 1 0 12 24A12 12 0 1 0 12 0Z'


def roundel(glyph_d, target_maxdim, dy=0.0):
    """Glyph scaled to target_maxdim (24-unit space), centred in the disc,
    knocked out via fill-rule evenodd. dy: optical vertical nudge."""
    cmds = parse_abs(glyph_d)
    x0, y0, x1, y1 = glyph_bbox(cmds)
    s = target_maxdim / max(x1-x0, y1-y0)
    tx = 12 - s*(x0+x1)/2
    ty = 12 - s*(y0+y1)/2 + dy
    return DISC + ' ' + serialize(transform(cmds, s, tx, ty))


# --- source glyphs (pre-roundel site icons + Simple Icons X) ---
SCHOLAR = 'M5.242 13.769L0 9.5 12 0l12 9.5-5.242 4.269C17.548 11.249 14.978 9.5 12 9.5c-2.977 0-5.548 1.748-6.758 4.269zM12 10a7 7 0 1 0 0 14 7 7 0 0 0 0-14zm0 2a5 5 0 1 1 0 10 5 5 0 0 1 0-10z'
GITHUB = 'M12 0C5.37 0 0 5.37 0 12c0 5.3 3.44 9.8 8.2 11.39.6.11.82-.26.82-.58v-2.03c-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.75.08-.73.08-.73 1.2.08 1.84 1.24 1.84 1.24 1.07 1.84 2.81 1.31 3.5 1 .1-.78.42-1.31.76-1.61-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.13-.3-.54-1.52.12-3.18 0 0 1-.32 3.3 1.23a11.5 11.5 0 0 1 6.02 0c2.28-1.55 3.29-1.23 3.29-1.23.66 1.66.25 2.88.12 3.18.77.84 1.24 1.91 1.24 3.22 0 4.61-2.81 5.63-5.48 5.92.43.37.81 1.1.81 2.22v3.29c0 .32.22.7.82.58A12 12 0 0 0 24 12c0-6.63-5.37-12-12-12z'   # ships verbatim
LINKEDIN = 'M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.34V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45z'
X = 'M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z'

if __name__ == '__main__':
    cap_only = SCHOLAR[:SCHOLAR.index('zM12 10a7')] + 'z'
    print('scholar :', roundel(cap_only, 13.5, dy=-0.4))
    print('github  :', GITHUB)
    print('linkedin:', roundel(LINKEDIN, 11.5))
    print('x       :', roundel(X, 11.0))
