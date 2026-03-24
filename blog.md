---
layout: blog
permalink: /blog/
---

<p class="blog-intro">A (very) relaxed collection of technical and non-technical notes.</p>

<hr class="section-break">

{% assign posts_by_year = site.posts | group_by_exp: "post", "post.date | date: '%Y'" %}
{% for year in posts_by_year %}
<p class="blog-year">{{ year.name }}</p>
<ul class="blog-post-list">
{% for post in year.items %}
  <li>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    <span class="post-list-date">{{ post.date | date: "%-d %B %Y" }}</span>
  </li>
{% endfor %}
</ul>
{% endfor %}
