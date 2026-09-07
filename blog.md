---
layout: blog
title: Writing
description: "Essays and research notes by Patrick Cannon."
permalink: /blog/
---

{% if site.posts.size == 0 %}
<p class="writing-empty">Writing coming soon.</p>
{% else %}
{% assign posts_by_year = site.posts | group_by_exp: "post", "post.date | date: '%Y'" %}
{% for year in posts_by_year %}
<section class="writing-year" aria-labelledby="year-{{ year.name }}">
  <h2 id="year-{{ year.name }}">{{ year.name }}</h2>
  <div class="writing-list">
    {% for post in year.items %}
    <a class="writing-item" href="{{ post.url | relative_url }}">
      <span>{{ post.title }}</span>
      <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: "%-d %b" }}</time>
    </a>
    {% endfor %}
  </div>
</section>
{% endfor %}
{% endif %}
