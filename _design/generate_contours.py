"""
Generate an SVG contour plot of a mixture of Gaussians for use as a 
background element in patrickcannon.cc.

The output is a self-contained SVG snippet that can be pasted directly 
into the HTML. The web page positions it in the top-right corner via CSS.

Tweak the mixture components below and re-run to regenerate.
"""

import numpy as np
from scipy.stats import multivariate_normal
from skimage.measure import find_contours

# ──────────────────────────────────────────────
# MIXTURE DEFINITION — edit these to change the shape
# ──────────────────────────────────────────────
# Coordinates are in SVG viewBox space (800 x 700).
# The web page will position this so the centre (~400, 350) 
# sits off-page in the top-right corner.

components = [
    {
        'mean': [380, 320],
        'cov': [[28000, 8000],
                [8000, 18000]],
        'weight': 0.55
    },
    {
        'mean': [480, 260],
        'cov': [[12000, -4000],
                [-4000, 8000]],
        'weight': 0.30
    },
    {
        'mean': [320, 400],
        'cov': [[6000, 2000],
                [2000, 10000]],
        'weight': 0.15
    },
]

# ──────────────────────────────────────────────
# RENDERING PARAMETERS
# ──────────────────────────────────────────────
GRID_SIZE = 400              # Resolution of evaluation grid
VIEWBOX_W, VIEWBOX_H = 800, 700
N_CONTOUR_LEVELS = 14        # Number of contour lines
CONTOUR_LEVEL_MIN = 0.04     # As fraction of max density (outermost)
CONTOUR_LEVEL_MAX = 0.92     # As fraction of max density (innermost)

# Colour ramp for filled bands (outermost to innermost)
# Format: (r, g, b, opacity)
FILL_COLOR_OUTER = (24, 60, 110, 0.03)
FILL_COLOR_INNER = (12, 36, 78, 0.58)

# Contour line style
STROKE_COLOR_OUTER = (55, 120, 190, 0.08)
STROKE_COLOR_INNER = (90, 160, 235, 0.55)
STROKE_WIDTH_OUTER = 1.0
STROKE_WIDTH_INNER = 2.2

OUTPUT_FILE = 'contour_orb.svg'
HTML_SNIPPET_FILE = 'contour_orb_snippet.html'


def evaluate_mixture(components, grid_size, viewbox_w, viewbox_h):
    """Evaluate mixture of Gaussians density on a grid."""
    x = np.linspace(0, viewbox_w, grid_size)
    y = np.linspace(0, viewbox_h, grid_size)
    X, Y = np.meshgrid(x, y)
    pos = np.dstack((X, Y))
    
    Z = np.zeros((grid_size, grid_size))
    for comp in components:
        rv = multivariate_normal(mean=comp['mean'], cov=comp['cov'])
        Z += comp['weight'] * rv.pdf(pos)
    
    return x, y, Z


def extract_contours(Z, levels, x, y):
    """Extract contour paths at specified density levels."""
    contours_by_level = []
    for level in levels:
        raw_contours = find_contours(Z, level)
        # Convert from grid indices to SVG coordinates
        svg_contours = []
        for contour in raw_contours:
            # contour is (row, col) in grid space -> (x, y) in SVG space
            coords = np.column_stack([
                np.interp(contour[:, 1], np.arange(len(x)), x),
                np.interp(contour[:, 0], np.arange(len(y)), y)
            ])
            # Simplify: keep every 3rd point (blur hides the difference)
            if len(coords) > 20:
                indices = np.arange(0, len(coords), 3)
                if indices[-1] != len(coords) - 1:
                    indices = np.append(indices, len(coords) - 1)
                coords = coords[indices]
            svg_contours.append(coords)
        contours_by_level.append(svg_contours)
    return contours_by_level


def coords_to_svg_path(coords, close=False):
    """Convert Nx2 coordinate array to SVG path d attribute."""
    if len(coords) == 0:
        return ""
    parts = [f"M {coords[0, 0]:.0f} {coords[0, 1]:.0f}"]
    for i in range(1, len(coords)):
        parts.append(f"L {coords[i, 0]:.0f} {coords[i, 1]:.0f}")
    if close:
        parts.append("Z")
    return " ".join(parts)


def interpolate_color(t, c_outer, c_inner):
    """Linearly interpolate between two RGBA tuples."""
    return tuple(c_outer[i] + t * (c_inner[i] - c_outer[i]) for i in range(4))


def generate_svg(contours_by_level, levels, z_max):
    """Generate complete SVG string with filled bands and contour lines."""
    lines = []
    lines.append(f'<svg viewBox="-100 -100 1000 900" xmlns="http://www.w3.org/2000/svg" style="overflow:visible;">')
    lines.append('  <defs>')
    lines.append('    <filter id="contour-soften">')
    lines.append('      <feGaussianBlur stdDeviation="4" />')
    lines.append('    </filter>')
    lines.append('  </defs>')
    lines.append('')
    
    n = len(levels)
    
    # Layer 1: Filled contour bands (painter's algorithm — outer to inner)
    lines.append('  <!-- Filled contour bands -->')
    lines.append('  <g filter="url(#contour-soften)">')
    for i, (level_contours, level) in enumerate(zip(contours_by_level, levels)):
        t = i / max(n - 1, 1)
        r, g, b, a = interpolate_color(t, FILL_COLOR_OUTER, FILL_COLOR_INNER)
        fill = f"rgba({int(r)},{int(g)},{int(b)},{a:.3f})"
        for contour_coords in level_contours:
            if len(contour_coords) < 3:
                continue
            d = coords_to_svg_path(contour_coords, close=True)
            lines.append(f'    <path d="{d}" fill="{fill}" stroke="none" />')
    lines.append('  </g>')
    lines.append('')
    
    # Layer 2: Contour line strokes
    lines.append('  <!-- Contour line strokes -->')
    lines.append('  <g filter="url(#contour-soften)">')
    for i, (level_contours, level) in enumerate(zip(contours_by_level, levels)):
        t = i / max(n - 1, 1)
        r, g, b, a = interpolate_color(t, STROKE_COLOR_OUTER, STROKE_COLOR_INNER)
        stroke = f"rgba({int(r)},{int(g)},{int(b)},{a:.3f})"
        sw = STROKE_WIDTH_OUTER + t * (STROKE_WIDTH_INNER - STROKE_WIDTH_OUTER)
        for contour_coords in level_contours:
            if len(contour_coords) < 3:
                continue
            d = coords_to_svg_path(contour_coords, close=False)
            lines.append(f'    <path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw:.1f}" />')
    lines.append('  </g>')
    
    lines.append('</svg>')
    return '\n'.join(lines)


def generate_html_snippet(svg_content):
    """Wrap SVG in HTML with the CSS class for positioning."""
    return f'''<!-- 
  Mixture of Gaussians contour orb
  Generated by generate_contours.py
  Paste this into the page HTML, replacing the existing contour-orb element.
  Requires CSS class .contour-orb for positioning.
-->
<div class="contour-orb">
{svg_content}
</div>'''


def main():
    print("Evaluating mixture of Gaussians on grid...")
    x, y, Z = evaluate_mixture(components, GRID_SIZE, VIEWBOX_W, VIEWBOX_H)
    z_max = Z.max()
    print(f"  Grid: {GRID_SIZE}x{GRID_SIZE}")
    print(f"  Peak density: {z_max:.6e}")
    
    # Define contour levels
    levels = np.linspace(
        z_max * CONTOUR_LEVEL_MIN,
        z_max * CONTOUR_LEVEL_MAX,
        N_CONTOUR_LEVELS
    )
    print(f"  {N_CONTOUR_LEVELS} contour levels from {levels[0]:.4e} to {levels[-1]:.4e}")
    
    print("Extracting contours...")
    contours_by_level = extract_contours(Z, levels, x, y)
    total_paths = sum(len(c) for c in contours_by_level)
    print(f"  Extracted {total_paths} paths across {N_CONTOUR_LEVELS} levels")
    
    print("Generating SVG...")
    svg_content = generate_svg(contours_by_level, levels, z_max)
    
    # Write standalone SVG
    with open(OUTPUT_FILE, 'w') as f:
        f.write(svg_content)
    print(f"  SVG written to {OUTPUT_FILE}")
    
    # Write HTML snippet
    snippet = generate_html_snippet(svg_content)
    with open(HTML_SNIPPET_FILE, 'w') as f:
        f.write(snippet)
    print(f"  HTML snippet written to {HTML_SNIPPET_FILE}")
    
    # Print SVG file size
    svg_size = len(svg_content.encode('utf-8'))
    print(f"  SVG size: {svg_size / 1024:.1f} KB")


if __name__ == '__main__':
    main()
