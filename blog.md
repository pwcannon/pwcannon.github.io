---
layout: blog
permalink: /blog/
---

{% if site.posts.size == 0 %}
<p class="body">Writing coming soon.</p>
{% else %}
{% assign posts_by_year = site.posts | group_by_exp: "post", "post.date | date: '%Y'" %}
{% for year in posts_by_year %}
<p class="blog-year">{{ year.name }}</p>
<ul class="blog-post-list">
  {% for post in year.items %}
  <li>
    <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    <span class="post-list-date">{{ post.date | date: "%-d %b" }}</span>
  </li>
  {% endfor %}
</ul>
{% endfor %}
{% endif %}
