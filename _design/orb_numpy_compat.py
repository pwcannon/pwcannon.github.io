"""
Pure-numpy stand-ins for scipy.stats.multivariate_normal and
skimage.measure.find_contours, plus a loader that imports
generate_contours.py unmodified with those stubs in place.

Exists because the sandbox that generates orb variations has no
scipy/skimage. Results are numerically equivalent (verified 11 June 2026:
regenerated baseline matches the committed orb's geometry exactly).
Used by variations/make_variations.py-style drivers.
"""

import sys
import types
from collections import defaultdict
from pathlib import Path

import numpy as np


class MVN:
    def __init__(self, mean, cov):
        self.mean = np.asarray(mean, float)
        cov = np.asarray(cov, float)
        self._inv = np.linalg.inv(cov)
        self._norm = 1.0 / (2.0 * np.pi * np.sqrt(np.linalg.det(cov)))

    def pdf(self, pos):
        d = np.asarray(pos, float) - self.mean
        e = np.einsum('...i,ij,...j->...', d, self._inv, d)
        return self._norm * np.exp(-0.5 * e)


def multivariate_normal(mean=None, cov=None):
    return MVN(mean, cov)


def find_contours(Z, level):
    """Marching squares returning (row, col) polylines, skimage-style."""
    Z = np.asarray(Z, float)
    R, C = Z.shape
    B = Z > level

    with np.errstate(divide='ignore', invalid='ignore'):
        tH = np.clip((level - Z[:, :-1]) / (Z[:, 1:] - Z[:, :-1]), 0.0, 1.0)
        tV = np.clip((level - Z[:-1, :]) / (Z[1:, :] - Z[:-1, :]), 0.0, 1.0)

    Hr = np.broadcast_to(np.arange(R, dtype=float)[:, None], (R, C - 1))
    Hc = np.arange(C - 1, dtype=float)[None, :] + tH
    Vr = np.arange(R - 1, dtype=float)[:, None] + tV
    Vc = np.broadcast_to(np.arange(C, dtype=float)[None, :], (R - 1, C))

    b00 = B[:-1, :-1].astype(np.int8)
    b01 = B[:-1, 1:].astype(np.int8)
    b11 = B[1:, 1:].astype(np.int8)
    b10 = B[1:, :-1].astype(np.int8)
    case = b00 | (b01 << 1) | (b11 << 2) | (b10 << 3)

    def pt(kind, r, c):
        if kind == 'T':
            return (Hr[r, c], Hc[r, c])
        if kind == 'B':
            return (Hr[r + 1, c], Hc[r + 1, c])
        if kind == 'L':
            return (Vr[r, c], Vc[r, c])
        return (Vr[r, c + 1], Vc[r, c + 1])

    CASES = {
        1: [('L', 'T')], 2: [('T', 'R')], 3: [('L', 'R')], 4: [('R', 'B')],
        6: [('T', 'B')], 7: [('L', 'B')], 8: [('B', 'L')], 9: [('T', 'B')],
        11: [('R', 'B')], 12: [('R', 'L')], 13: [('T', 'R')], 14: [('L', 'T')],
    }

    segs = []
    for k, pairs in CASES.items():
        for r, c in np.argwhere(case == k):
            for a, b in pairs:
                segs.append((pt(a, r, c), pt(b, r, c)))
    for k in (5, 10):
        for r, c in np.argwhere(case == k):
            avg = (Z[r, c] + Z[r, c + 1] + Z[r + 1, c] + Z[r + 1, c + 1]) / 4.0
            if k == 5:
                pairs = [('T', 'R'), ('B', 'L')] if avg > level else [('L', 'T'), ('R', 'B')]
            else:
                pairs = [('L', 'T'), ('R', 'B')] if avg > level else [('T', 'R'), ('B', 'L')]
            for a, b in pairs:
                segs.append((pt(a, r, c), pt(b, r, c)))

    adj = defaultdict(list)
    for i, (p, q) in enumerate(segs):
        adj[p].append((i, q))
        adj[q].append((i, p))

    used = [False] * len(segs)
    contours = []
    for i, (p, q) in enumerate(segs):
        if used[i]:
            continue
        used[i] = True
        path = [p, q]
        closed = False
        for grow_tail in (True, False):
            while not closed:
                end = path[-1] if grow_tail else path[0]
                nxt = None
                for j, other in adj[end]:
                    if not used[j]:
                        nxt = (j, other)
                        break
                if nxt is None:
                    break
                used[nxt[0]] = True
                if grow_tail:
                    path.append(nxt[1])
                else:
                    path.insert(0, nxt[1])
                if path[0] == path[-1]:
                    closed = True
        contours.append(np.asarray(path, float))
    return contours


def load_orb_module():
    """Import generate_contours.py unmodified, with numpy stubs installed."""
    _scipy = types.ModuleType('scipy')
    _scipy_stats = types.ModuleType('scipy.stats')
    _scipy_stats.multivariate_normal = multivariate_normal
    _scipy.stats = _scipy_stats
    _skimage = types.ModuleType('skimage')
    _skimage_measure = types.ModuleType('skimage.measure')
    _skimage_measure.find_contours = find_contours
    _skimage.measure = _skimage_measure
    sys.modules.setdefault('scipy', _scipy)
    sys.modules.setdefault('scipy.stats', _scipy_stats)
    sys.modules.setdefault('skimage', _skimage)
    sys.modules.setdefault('skimage.measure', _skimage_measure)

    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'gc_orb', Path(__file__).resolve().parent / 'generate_contours.py')
    gc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gc)
    return gc
