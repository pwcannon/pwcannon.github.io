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

All posts use `_layouts/post.html`, `assets/css/article.css` and
`assets/js/article.js`. The CSS and JavaScript are generated from the private
shared presentation; change those sources and regenerate both assets rather than
editing website copies. Margin notes, responsive footnotes, technical notes,
figures and references share those components. Footnotes precede references;
method summaries use ordinary prose. Do not introduce per-post layout switches.

`assets/css/style.css` owns the site shell, navigation, footer and non-article
pages. The article exporter deliberately excludes those rules. Keep the existing
website navigation when changing article presentation. Check both published
articles at desktop and phone widths after changing shared components, and check
the homepage and Writing page after changing site-wide CSS.

Publications are single-sourced in `_data/publications.yml`. Private drafts,
review artefacts and design comparison pages must not be included in releases.
