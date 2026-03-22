# Website Redesign — Working Document

**Created:** 2026-03-21
**Status:** In progress (Evening 1 complete)

---

## Design Direction

**Aesthetic:** Tasteful retro — a "nod" to Win95/retro computing, not a recreation. Personality through palette and typography, not pixel art or UI chrome. Content-first. Mathematical material should present beautifully and clearly.

**Colour palette (cool grey):**
- Teal accent: `#007a7a`
- Navy headings: `#1a1a4e`
- Body text: `#2d2d2d`
- Cool grey background (blog/posts): `#f4f5f6`
- Home page background: `#ffffff`
- Borders: `#cdd0d4`
- Secondary text: `#646972`

**Typography:**
- Headings: IBM Plex Mono (monospace = the main retro signal)
- Body: IBM Plex Sans
- Code: IBM Plex Mono

**Layout:**
- Home page: sidebar (photo + links) + content (bio + publications). Uses `layout: default`.
- Blog index: full-width centered column. Uses `layout: blog`.
- Blog posts: full-width centered column, 700px max-width. Uses `layout: post`.

---

## Completed — Evening 1 (March 21)

### Files changed
- `_layouts/default.html` — updated with new fonts, clean sidebar links, blog CTA
- `_layouts/post.html` — **new**. Full-width post layout with MathJax (incl. ams packages)
- `_layouts/blog.html` — **new**. Full-width blog index layout with dynamic post listing
- `_layouts/default_2.html` — **deleted**. Replaced by `post.html`
- `assets/css/style.scss` — full design system: palette, typography, post styles, responsive
- `blog.md` — updated to `layout: blog`, dynamic post listing via Liquid
- `_config.yml` — added `kramdown: math_engine: null`, fixed YAML syntax
- `_posts/2023-11-13-test-blog.md` — updated to `layout: post`, removed LaTeX from title

### Bugs fixed
- MathJax double-load in old `default_2.html`
- Base theme CSS (`float`, `position`) bleeding into post layout — reset with targeted overrides
- Title + body text overlap on post pages
- Footer floating mid-page — fixed with flexbox `min-height: 100vh`
- Blog index centering issue — `width: 100%` on flex child
- YAML syntax error in `_config.yml` (single-line kramdown config)
- Nav bar gap at top of post pages — body margin/padding reset

### Infrastructure
- SSH key added to GitHub
- `pre-redesign` branch created as safety rollback
- Working on `redesign` branch, GitHub Pages temporarily pointed at it
- Remote switched from HTTPS to SSH

---

## TODO — Evening 2: Personality and Polish (Home Page)

### Bring back lost elements
- [ ] Profile photo — check if it's rendering in sidebar (it's in `_config.yml` as `logo`). If not, debug.
- [ ] Retro computer icon — find a natural placement (sidebar? near blog link? footer?)
- [ ] Helsinki photo from old `default_2` — decide: keep somewhere or drop?

### Home page design improvements
- [ ] Replace emoji bullets (🔘) with CSS-styled alternatives (teal dashes, arrows, or similar)
- [ ] Make "Blog →" link in sidebar more visually intentional
- [ ] Consider small inline SVG icons for social links (Scholar, GitHub, LinkedIn, Twitter)
- [ ] Review sidebar spacing and visual hierarchy

### Content updates (can defer to Evening 3)
- [ ] Update interests from "robust deep learning / algorithmic trustworthiness / alignment" to inference-time compute / RL for reasoning positioning

---

## TODO — Evening 3: Content and Final Sweep

- [ ] Update landing page bio and interests for new positioning
- [ ] Test mobile responsiveness (home, blog index, post)
- [ ] Test MathJax with realistic content: inline math, display equations, align environments
- [ ] Merge `redesign` → `master`
- [ ] Switch GitHub Pages back to `master`
- [ ] Delete `redesign` branch
- [ ] Final review of all pages

---

## Decisions Made
1. **Custom domain:** Keep patrickcannon.cc — net positive signal.
2. **Theme approach:** Stay with forked `jekyll-theme-minimal`, override with custom layouts and CSS.
3. **Sidebar:** Keep on home page, full-width (no sidebar) for blog index and posts.
4. **Retro aesthetic level:** Tasteful nod — palette and monospace headings only. No pixel art, no UI chrome, no 98.css.
5. **Footer:** Keep on blog/post pages (satisfying scroll-to-end feel), pinned to viewport bottom via flexbox.
6. **Home page background:** White (`#ffffff`), distinct from blog pages (cool grey `#f4f5f6`). Intentional differentiation: professional card vs reading environment.
7. **LaTeX in titles:** Avoid. Titles should work as plain text everywhere.
8. **Dynamic blog index:** Posts auto-listed via Liquid, no manual editing needed.

---

## Reference: Key Asset Finds (from research session)
- **98.css** — pure CSS Win98 recreation. Decided NOT to use, but good reference for border treatments.
- **Pixelarticons** (pixelarticons.com) — 4000+ pixel SVGs. Decided against pixel aesthetic but could revisit for one or two small accents.
- **IBM Plex Mono / IBM Plex Sans** — chosen fonts. Google Fonts, free.
- **Themesberg Win95 UI Kit** — colour reference only (grey/teal/navy confirmed our palette choice).
