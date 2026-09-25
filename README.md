# patrickcannon.cc

Personal research website. Jekyll, published by GitHub Pages from `master`.

Last updated: 2026-09-25

## Build and release

Use `bundle exec jekyll build` with the repository Gemfile, or the installed
GitHub Pages-compatible Jekyll environment. Build and review the maintained
checkout locally before committing a release. Publication requires Patrick's
explicit instruction; pushing `master` triggers GitHub Pages. Verify the live
page after deployment. Roll back with a reviewed revert, never a reset or force
push. Historical design experiments remain on an archive branch and must not be
merged wholesale.

## Article sources and styling

Article prose and maths are edited in the separate private Quarto blog repository,
not in `_posts`. Its `PUBLICATION-WORKFLOW.md` documents rendering and export.
The shared exporter generates each post's body and metadata; reading time is
computed during the Quarto render. A full `title` remains available for listings
and search metadata; `display-title` and `subtitle` control the visible heading.

All posts use `_layouts/post.html`, `assets/css/spacing.css`,
`assets/css/article.css` and `assets/js/article.js`. The CSS and JavaScript are generated from the private
shared presentation; change those sources and regenerate both assets rather than
editing website copies. Margin notes, responsive footnotes, technical notes,
figures and references share those components. Footnotes precede references;
method summaries begin with an italic “Method summary:” label followed by normal text. Do not introduce per-post layout switches.

`assets/css/style.css` owns the site shell, navigation, footer and non-article
pages. The article exporter deliberately excludes those rules. Keep the existing
website navigation when changing article presentation. Check both published
articles at desktop and phone widths after changing shared components, and check
the homepage and Writing page after changing site-wide CSS.

Publications are single-sourced in `_data/publications.yml`. Private drafts,
review artefacts and design comparison pages must not be included in releases.

## Asset caching

Route local stylesheet and script URLs through `_includes/asset-url.html`. It
appends Jekyll's build timestamp, shared by all pages in that build. Every build
therefore requests a fresh, matching set of CSS and JavaScript instead of mixing
new page markup with a returning visitor's cached assets. No manual version bump
is required. Keep the version when adding new local CSS or script references.

## Spacing

The generated `assets/css/spacing.css` provides one scale: 4, 8, 16, 24, 40 and
56 px. Its source is the private blog's `shared/css/spacing.css`. Paragraphs,
equations and abstract gaps use 16 px; main sections use 56 px before their
heading, subsections 40 px, and figure padding and technical-note outer gaps
use 24 px. Contents uses subsection spacing: 40 px above and below the whole block,
and 16 px between the heading and list. These rules apply on phones too. There is no special abstract or
first-section spacing. Typography, outer page padding and diagram geometry
remain separate. Regenerate the spacing stylesheet along with article CSS/JS.

## Selected work

Selected work uses `_data/selected_work.yml`. A purple “new” label uses regular weight in
the award label’s metadata row for the first 30 days after
publication. Internal blog links inherit the post date; other entries can set
`date: YYYY-MM-DD`. The homepage script checks recency on page load, so labels
expire without rebuilding. Undated and future-dated entries receive no label.
