# Website Context

This is Patrick Cannon's personal academic website. Jekyll + GitHub Pages.

## Design Language (June 2026)
Soft, near-monochrome cool-blue palette on pale paper (#EDF2F7), airbrushed
background blobs + film grain, hairline structural rules, DM Sans.
Single accent: rose (button hover, sparingly). Nav is bright-on-dark,
backed by the contour orb's dark field.

The top-right "contour orb" is the signature motif: a posterior-draws ink
wash of a 3-component gaussian mixture — each band is the level set of a
different resample, so the wandering edges depict estimation uncertainty.
11 bands since 12 Jun 2026 (bands 11/12/14 ablated by eye test; SKIP_BANDS
in the generator, mirrored in make_brand_assets.py). Regenerate with
`_design/make_orb_inkwash.py --include` (deterministic, seed 29).
Orientation/position live in CSS (`.contour-orb`). Keep the orb dark
behind the nav; no separate islands; nothing crossing body text.

Content-first. Must render LaTeX beautifully (MathJax in post layout).

## Structure Notes
- `_includes/contour_orb.html` — generated, don't hand-edit
- `_design/` — generators and prototype, excluded from the build
- `_design/make_brand_assets.py` — generates og_card.png + favicon set from
  the orb mixture (seed 29). Card text needs DM Sans TTFs in `_design/fonts/`
  (not vendored; download from Google Fonts)
- Blobs + grain are shared includes (`background_blobs.html`, `noise_grain.html`);
  grain include must stay AFTER `.page-wrapper` in the DOM (paints over
  blobs/orb, beneath z-indexed content)
- Publications are single-sourced in `_data/publications.yml`, rendered by
  `_includes/publications.html` (homepage: `selected=true` subset; research
  page: full list). Update the YAML, never the pages
- Post body font: flip `--post-font` in style.css between sans/serif stacks
  (Source Serif 4 loaded in post layout only; A/B pending decision)

## Broader Context
This website supports a job search targeting frontier AI labs (OpenAI,
Anthropic, GDM, Meta FAIR, xAI). The site needs to read as "serious
researcher with personality," not "hobbyist" or "novelty."

## Commands
- Deploy: push to the branch GitHub Pages is configured to serve
  (currently `update-homepage-copy`)
- Local preview: bundle exec jekyll serve
  (restart required after `_config.yml` changes)
