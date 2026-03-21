---
layout: blog
---

## You've reached The Blog.

A (very) relaxed collection of technical and non-technical notes.

---

{% assign posts_by_year = site.posts | group_by_exp: "post", "post.date | date: '%Y'" %}
{% for year in posts_by_year %}
## {{ year.name }}

{% for post in year.items %}
[{{ post.title }}]({{ post.url | relative_url }})   ({{ post.date | date: "%-d %B %Y" }})

{% endfor %}
---
{% endfor %}