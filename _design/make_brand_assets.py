"""
Brand assets generator: OG link-preview card + favicon set (12 June 2026).

Reuses the canonical contour-orb machinery (same MIXTURE, same seed-29
posterior-draws band logic, same navy ink ramp) so the link card and the
tab icon are literally the same object as the site motif.

Outputs:
  assets/img/og_card.png   1200x630 link-preview card (og:image / twitter card)
  favicon.svg              flat blob mark, auto dark-mode via media query
  favicon.ico              16+32+48 multi-size, repo root (fallback)
  apple-touch-icon.png     180x180 blob on paper tile, repo root
  assets/img/favicon-16.png, favicon-32.png

Card design (decided 12 Jun 2026, workshopped at length): dark ink field
(more figure-ground in feeds; quotes the site's bright-on-dark nav moment),
orb as bright wash with bands 11/12/14 ablated (leave-one-out eye test),
source-over band stacking (SVG painter's model — cumulative coverage, not
single-layer alpha), spline-smoothed edges, grain split into quiet
luminance + site-strength chroma dust (the dusty-rose hue). Copy locked:
name / "machine learning researcher" / "reasoning · uncertainty ·
alignment" / domain, type scale 68/30/20.

Favicon design (decided 12 Jun 2026): the soft posterior-draws wash works
at page scale but dies at 16px, so the favicon is the FLAT silhouette of
the unperturbed mixture's 0.30 level set ("the heart blob" — Patrick),
solid navy, with a chunkier lower-level cut for the 16px render and a
bright variant on dark tab bars (SVG prefers-color-scheme).

Text on the card requires DM Sans, which is not vendored: download the
family from fonts.google.com and unzip into _design/fonts/ (any layout —
the script globs for static SemiBold/Regular TTFs and falls back to the
variable font via fvar axes). Without fonts the card is written WITHOUT
text and a warning is printed.

Deterministic: seed 29.

Usage:  python3 make_brand_assets.py
"""

import copy
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from orb_numpy_compat import find_contours, load_orb_module
from make_orb_inkwash import MIXTURE, N_BANDS, bezier_d

gc = load_orb_module()

# Card filename is VERSIONED because scrapers (LinkedIn/Slack/X) cache
# og-images by URL for days: bump the version on any visible card change,
# and update the matching `image:` default in _config.yml IN LOCKSTEP.
CARD_ASSET = 'og_card_v3.png'

SEED = 29       # site orb / grain determinism
CARD_SEED = 69  # card orb resample — deliberately a different posterior draw
                # from the site's (decided 12 Jun 2026: the motif's identity
                # is the mixture + band grammar, not a particular draw; each
                # surface carrying its own resample IS the concept)

# Card geometry (rendered at 2x, downsampled for crispness)
CARD_W, CARD_H, SS = 1200, 630, 2

# Site palette
PAPER_TOP = (237, 242, 247)      # #EDF2F7
PAPER_MID = (228, 237, 245)      # #E4EDF5
PAPER_BOT = (238, 240, 244)      # #EEF0F4
INK_NAME = (10, 30, 46)          # --name / --lead
INK_BODY = (46, 74, 102)         # --body-text
INK_META = (122, 154, 184)       # --meta
HAIRLINE = (160, 185, 210, 115)  # --border

# Card copy — locked 12 Jun 2026 (Patrick). The _config.yml meta description
# is intentionally different (informative sentence for Google).
ROLE = "machine learning researcher"
ROW = "reasoning · uncertainty · alignment"
DOMAIN = "patrickcannon.cc"

# Card design — dark field, decided 12 Jun 2026 (Patrick):
DARK_TOP = (10, 25, 40)
DARK_BOT = (16, 36, 58)
TXT_BRIGHT = (232, 244, 255)     # --nav-active (name)
TXT_MID = (168, 200, 224)        # --nav-inactive (keyword row)
TXT_MUTED = (122, 154, 184)      # --meta (role, domain)
HAIR_DARK = (168, 200, 224, 60)
ORB_RAMP_DARK = ((90, 130, 175), (190, 222, 248))  # bright wash on ink field

# Orb band ablation — Patrick, 12 Jun 2026, by leave-one-out eye test:
# bands 11, 12, 14 (1-indexed) removed. ADOPTED SITE-WIDE same day — must
# stay in sync with SKIP_BANDS in make_orb_inkwash.py.
SKIP_BANDS = {10, 11, 13}  # 0-indexed
BAND_ALPHAS = np.linspace(0.03, 0.58, 14)


def band_polys(seed=SEED):
    """Posterior-draws bands, exactly as make_orb_inkwash computes them.

    Returns a list of (polygon_points, rgba) in orb space (800x700, y down).
    """
    rng = np.random.default_rng(seed)

    def perturbed(comps):
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

    out = []
    fracs = np.linspace(0.04, 0.92, N_BANDS)
    alphas = np.linspace(0.03, 0.58, N_BANDS)
    for bi, (fr, a_) in enumerate(zip(fracs, alphas)):
        cset = perturbed(MIXTURE)
        px, py, PZ = gc.evaluate_mixture(cset, gc.GRID_SIZE, gc.VIEWBOX_W, gc.VIEWBOX_H)
        lv = fr * PZ.max()
        r, g, b, _ = gc.interpolate_color(bi / (N_BANDS - 1),
                                          gc.FILL_COLOR_OUTER, gc.FILL_COLOR_INNER)
        for cc in find_contours(PZ, lv):
            P = np.column_stack([np.interp(cc[:, 1], np.arange(len(px)), px),
                                 np.interp(cc[:, 0], np.arange(len(py)), py)])
            out.append((P, (int(r), int(g), int(b), a_)))
    return out


def paper_background(w, h):
    """Vertical-ish gradient matching the body::after 175deg ramp."""
    t = np.linspace(0, 1, h)[:, None, None]
    top = np.array(PAPER_TOP, float)
    mid = np.array(PAPER_MID, float)
    bot = np.array(PAPER_BOT, float)
    ramp = np.where(t < 0.4, top + (mid - top) * (t / 0.4),
                    mid + (bot - mid) * ((t - 0.4) / 0.6))
    img = np.broadcast_to(ramp, (h, w, 3)).astype(np.uint8)
    return Image.fromarray(img, 'RGB').convert('RGBA')


def dark_background(w, h):
    """Deep ink gradient for the card field."""
    t = np.linspace(0, 1, h)[:, None, None]
    ramp = np.array(DARK_TOP, float) + (np.array(DARK_BOT, float)
                                        - np.array(DARK_TOP, float)) * t
    return Image.fromarray(np.broadcast_to(ramp, (h, w, 3)).astype(np.uint8),
                           'RGB').convert('RGBA')


def band_index(a):
    return int(np.argmin(np.abs(BAND_ALPHAS - a)))


def bez_points(P, step=4, samples=12):
    """Catmull-Rom spline through every step-th point (matches the site's
    bezier_d smoothing, sampled back to a polygon)."""
    if np.allclose(P[0], P[-1]):
        P = P[:-1]
    if len(P) > 3 * step:
        P = P[::step]
    n = len(P)
    if n < 4:
        return P
    out = []
    for i in range(n):
        p0, p1, p2, p3 = P[(i - 1) % n], P[i], P[(i + 1) % n], P[(i + 2) % n]
        c1 = p1 + (p2 - p0) / 6.0
        c2 = p2 - (p3 - p1) / 6.0
        for t in np.linspace(0, 1, samples, endpoint=False):
            mt = 1 - t
            out.append(mt ** 3 * p1 + 3 * mt * mt * t * c1
                       + 3 * mt * t * t * c2 + t ** 3 * p2)
    return np.array(out)


def draw_orb_stacked(layer_size, polys, center, scale, angle_deg,
                     skip=frozenset(), ramp=None, global_a=0.85, blur=6):
    """Source-over band stacking — matches the SVG painter's model.

    Each band composites onto the running stack (cumulative coverage
    1-prod(1-a_i), ~99% at the core), then the group opacity and blur are
    applied to the stacked result, exactly like the site's CSS/SVG filters.
    Bands listed in `skip` (0-indexed) are omitted; `ramp` recolours
    outer->inner (used by the dark card's bright wash).
    """
    th = np.deg2rad(angle_deg)
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    c0 = np.array([380.0, 330.0])  # approximate mass centroid in orb space
    L = Image.new('RGBA', layer_size, (0, 0, 0, 0))
    for P, (r, g, b, a) in polys:
        if band_index(a) in skip:
            continue
        if ramp:
            t = band_index(a) / (len(BAND_ALPHAS) - 1)
            r, g, b = [int(ramp[0][k] + t * (ramp[1][k] - ramp[0][k]))
                       for k in range(3)]
        Q = (bez_points(P) - c0) @ R.T * scale + np.array(center)
        if len(Q) < 3:
            continue
        tmp = Image.new('RGBA', layer_size, (0, 0, 0, 0))
        ImageDraw.Draw(tmp).polygon([tuple(p) for p in Q],
                                    fill=(r, g, b, int(round(255 * a))))
        L = Image.alpha_composite(L, tmp)
    arr = np.asarray(L).astype(np.float32)
    arr[..., 3] *= global_a
    return Image.fromarray(arr.astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(blur))


def _fractal_noise(h, w, rng):
    """feTurbulence-style noise: base ~1.5 css px features, finer octaves."""
    noise = np.zeros((h, w, 3), np.float32)
    amp_sum = 0
    for o in range(3):
        amp = 0.5 ** o
        cell = max(1, round(3 / 2 ** o))
        n = rng.random((max(2, h // cell), max(2, w // cell), 3),
                       dtype=np.float32)
        noise += amp * np.asarray(
            Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR),
            np.float32) / 255
        amp_sum += amp
    return noise / amp_sum


def _overlay(base, field):
    return np.where(base < 0.5, 2 * base * field, 1 - 2 * (1 - base) * (1 - field))


def add_grain(img, rng, op_luma=0.05, op_chroma=0.30):
    """Site-matched grain, perceptually decomposed (12 Jun 2026):
    luminance speckle at 0.05 (quiet), chroma 'dust' at the site's 0.30,
    blurred so it reads as hue weather — this is the dusty-rose component
    of the website's feTurbulence overlay grain."""
    base = np.asarray(img.convert('RGB')).astype(np.float32) / 255
    h, w = base.shape[:2]
    n = _fractal_noise(h, w, rng)
    luma = n.mean(-1, keepdims=True)
    chroma = 0.5 + (n - luma)
    chroma = np.asarray(
        Image.fromarray((np.clip(chroma, 0, 1) * 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(1.2 * SS)), np.float32) / 255
    out = base * (1 - op_luma) + _overlay(base, np.repeat(luma, 3, axis=2)) * op_luma
    out = out * (1 - op_chroma) + _overlay(out, chroma) * op_chroma
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8),
                           'RGB').convert('RGBA')


def find_fonts():
    """Locate DM Sans in _design/fonts/. Returns (semibold, regular) loaders or None."""
    fdir = HERE / 'fonts'
    if not fdir.exists():
        return None
    ttfs = sorted(fdir.rglob('*.ttf'))
    if not ttfs:
        return None

    def static(tag):
        cands = [p for p in ttfs if tag.lower() in p.stem.lower()
                 and 'italic' not in p.stem.lower()]
        # Prefer larger optical sizes for display use (e.g. DMSans_36pt-…)
        return sorted(cands, key=lambda p: p.stem, reverse=True)[0] if cands else None

    sb, rg = static('SemiBold'), static('Regular')
    if sb and rg:
        return (lambda s: ImageFont.truetype(str(sb), s),
                lambda s: ImageFont.truetype(str(rg), s))

    var = [p for p in ttfs if 'variablefont' in p.stem.lower().replace('_', '')]
    if var:
        def loader(weight):
            def f(s):
                font = ImageFont.truetype(str(var[0]), s)
                try:
                    font.set_variation_by_axes([weight])
                except Exception:
                    pass
                return font
            return f
        return loader(600), loader(400)
    return None


def make_card(polys, root):
    """Final card (12 Jun 2026): dark ink field, bright 11-band orb wash,
    type scale 68/30/20 (name / role+row / domain), locked copy."""
    w, h = CARD_W * SS, CARD_H * SS
    img = dark_background(w, h)

    # Orb: right side at 1.05x, nearly full contour visible so the heart
    # silhouette reads and rhymes with the favicon (V1 framing, 12 Jun 2026;
    # 1.25x bleed framing rejected — favicon match beats site-crop match
    # on first-contact surfaces). NATIVE orientation (0°): the site's 15° CSS
    # rotation exists to seat the orb behind the nav; brand marks keep the
    # original, more charming tilt (Patrick, 12 Jun 2026).
    orb = draw_orb_stacked((w, h), polys, center=(w * 0.76, h * 0.40),
                           scale=1.05 * SS, angle_deg=0, skip=SKIP_BANDS,
                           ramp=ORB_RAMP_DARK, global_a=0.77)
    img = Image.alpha_composite(img, orb)
    img = add_grain(img, np.random.default_rng(SEED))

    # Hairline rule above the footer line, echoing the site's structural rules
    draw = ImageDraw.Draw(img, 'RGBA')
    draw.line([(70 * SS, h - 92 * SS), (w - 70 * SS, h - 92 * SS)],
              fill=HAIR_DARK, width=SS)

    fonts = find_fonts()
    if fonts:
        f_sb, f_rg = fonts
        x = 70 * SS
        draw.text((x, 182 * SS), "Patrick Cannon", font=f_sb(68 * SS),
                  fill=TXT_BRIGHT)
        draw.text((x, 304 * SS), ROLE, font=f_rg(30 * SS), fill=TXT_MUTED)
        draw.text((x, 354 * SS), ROW, font=f_rg(30 * SS), fill=TXT_MID)
        draw.text((x, h - 72 * SS), DOMAIN, font=f_rg(20 * SS), fill=TXT_MUTED)
    else:
        print('WARNING: DM Sans not found in _design/fonts/ — card written '
              'WITHOUT text. Download DM Sans from fonts.google.com, unzip '
              'into _design/fonts/, re-run.')

    out = img.resize((CARD_W, CARD_H), Image.LANCZOS).convert('RGB')
    dest = root / 'assets' / 'img' / CARD_ASSET
    out.save(dest, optimize=True)
    print(f'{dest.relative_to(root)} written ({dest.stat().st_size // 1024} KB)')


BLOB_NAVY = (12, 36, 78)      # light-mode mark (orb inner ramp colour)
BLOB_BRIGHT = '#A8C8E0'       # dark-mode mark (--nav-inactive)


def blob_polys(frac):
    """Flat silhouette: level set of the UNPERTURBED mixture, NATIVE
    orientation (0° — matches the card; the site's 15° tilt is CSS-only)."""
    px, py, PZ = gc.evaluate_mixture(MIXTURE, gc.GRID_SIZE, gc.VIEWBOX_W, gc.VIEWBOX_H)
    out = []
    for cc in find_contours(PZ, frac * PZ.max()):
        P = np.column_stack([np.interp(cc[:, 1], np.arange(len(px)), px),
                             np.interp(cc[:, 0], np.arange(len(py)), py)])
        out.append(P)
    return out


def render_blob(size, frac, pad, color):
    """Flat hard-edged blob, fit to a size x size transparent canvas."""
    polys = blob_polys(frac)
    allp = np.vstack(polys)
    c = (allp.min(0) + allp.max(0)) / 2
    half = (allp.max(0) - allp.min(0)).max() / 2 * pad
    S = 1024
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for P in polys:
        Q = (P - c) * (S / (2 * half)) + S / 2
        d.polygon([tuple(p) for p in Q], fill=color + (255,))
    return img.resize((size, size), Image.LANCZOS)


def make_favicons(root):
    """'Heart blob' mark: flat 0.30 level set. Chunkier 0.26 cut at 16px."""
    img_dir = root / 'assets' / 'img'

    # PNG/ICO fallbacks (Safari has no SVG-favicon support, so these must be
    # legible on BOTH light and dark tab bars without scheme awareness):
    # blob on a small paper tile, matching the apple-touch-icon treatment.
    def tile_blob(size):
        S = 512
        img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(img).rounded_rectangle(
            [0, 0, S - 1, S - 1], radius=int(S * 0.22),
            fill=PAPER_TOP + (255,))
        blob = render_blob(int(S * 0.78), 0.26, 1.02, BLOB_NAVY)
        img.alpha_composite(blob, (int(S * 0.11), int(S * 0.11)))
        return img.resize((size, size), Image.LANCZOS)

    tile_blob(32).save(img_dir / 'favicon-32.png')
    tile_blob(16).save(img_dir / 'favicon-16.png')
    print('assets/img/favicon-32.png, favicon-16.png written (paper tile)')

    tile_blob(256).save(root / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
    print('favicon.ico written (paper tile)')

    # Apple touch icon: blob on paper tile (iOS composites transparency onto black)
    apple = paper_background(180, 180)
    apple.alpha_composite(render_blob(132, 0.30, 1.06, BLOB_NAVY), (24, 24))
    apple.convert('RGB').save(root / 'apple-touch-icon.png')
    print('apple-touch-icon.png written')

    # SVG favicon: smoothed path, auto colour-scheme swap (Chrome/Firefox)
    polys = blob_polys(0.30)
    allp = np.vstack(polys)
    lo, hi = allp.min(0), allp.max(0)
    c = (lo + hi) / 2
    half = (hi - lo).max() / 2 * 1.06
    paths = []
    for P in polys:
        Q = (P - c) + half  # coordinate frame [0, 2*half]
        d = bezier_d(Q, step=6)
        if d:
            paths.append(f'  <path d="{d}"/>')
    rgb = 'rgb({},{},{})'.format(*BLOB_NAVY)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
           f'viewBox="0 0 {2 * half:.0f} {2 * half:.0f}">\n'
           f'  <style>path{{fill:{rgb}}}'
           f'@media(prefers-color-scheme:dark){{path{{fill:{BLOB_BRIGHT}}}}}</style>\n'
           + '\n'.join(paths) + '\n</svg>\n')
    (root / 'favicon.svg').write_text(svg)
    print(f'favicon.svg written ({len(svg)} bytes)')


def main():
    root = HERE.parent
    make_card(band_polys(CARD_SEED), root)
    make_favicons(root)


if __name__ == '__main__':
    main()
