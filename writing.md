---
layout: blog
title: Writing
description: "Technical writing, essays and art by Patrick Cannon."
permalink: /writing/
---

<div class="writing-filters" role="group" aria-label="Filter writing by type" hidden>
  <button type="button" data-writing-filter="all" aria-pressed="true"><span class="writing-filter-label">All</span></button>
  {% for category in site.data.writing_labels %}
  <button type="button" data-writing-filter="{{ category[0] }}" aria-pressed="false"><span class="writing-filter-label">{{ category[1] }}</span></button>
  {% endfor %}
</div>
<p class="writing-filter-status" role="status" aria-live="polite" aria-atomic="true"></p>
<p class="writing-empty writing-filter-empty" hidden>No posts in this selection yet. Choose another type or All.</p>
<noscript><p class="writing-empty">Showing all writing. Enable JavaScript to filter by type.</p></noscript>

{% if site.posts.size == 0 %}
<p class="writing-empty">Writing coming soon.</p>
{% else %}
{% assign posts_by_year = site.posts | group_by_exp: "post", "post.date | date: '%Y'" %}
{% for year in posts_by_year %}
<section class="writing-year" aria-labelledby="year-{{ year.name }}">
  <h2 id="year-{{ year.name }}">{{ year.name }}</h2>
  <div class="writing-list">
    {% for post in year.items %}
    {% capture writing_category %}{% include writing-category.html post=post %}{% endcapture %}
    {% assign writing_category = writing_category | strip %}
    <a class="writing-item" data-writing-category="{{ writing_category }}" href="{{ post.url | relative_url }}">
      <span class="writing-copy"><span class="writing-title">{{ post.title }}</span><span class="work-meta"><span class="work-format">{{ site.data.writing_labels[writing_category] | escape }}</span></span></span>
      <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%-d %b" }}</time>
    </a>
    {% endfor %}
  </div>
</section>
{% endfor %}
{% endif %}

<script defer src="{% include asset-url.html path="/assets/js/writing.js" %}"></script>
