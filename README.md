# patrickcannon.cc

Personal research website. Jekyll, published by GitHub Pages from `master`.

## Build

Use `bundle exec jekyll build` with the repository Gemfile, or `jekyll build` with the installed GitHub Pages-compatible Jekyll environment.

## Release and rollback

The September 2026 redesign is a single commit based on `5f9af4b` (the previous website). Revert the redesign commit on master and push to restore the prior tracked website while preserving history. Do not reset or force-push master.

The original local checkout contained uncommitted design experiments and was left untouched. Release preparation used a separate checkout.

## Content

The first essay is `_posts/2026-08-24-training-for-reasoning.html`, exported from the training-for-reasoning research source. Shared article rendering lives in `_layouts/post.html`. Research and contact URLs are retained. Design comparison pages and painting experiments are not published.
