---
layout: default
permalink: /
description: "Independent AI researcher working on reliable oversight for language-model reasoning."
body_class: home-page
---

<main class="portfolio">
  <header class="identity-composition">
    <img
      class="identity-mark"
      src="{{ "/assets/img/inkblot-blue-3.webp" | relative_url }}"
      width="512"
      height="512"
      alt=""
      aria-hidden="true"
      decoding="async"
      fetchpriority="high"
    >

    <div class="identity-copy">
      <h1>Patrick Cannon</h1>

      <nav class="identity-links" aria-label="Profile links">
        <a href="mailto:hello@patrickcannon.cc">Email</a>
        <span aria-hidden="true">·</span>
        <a href="https://scholar.google.com/citations?user=drP5-oIAAAAJ">Scholar</a>
        <span aria-hidden="true">·</span>
        <a href="https://www.linkedin.com/in/patrick-cannon/">LinkedIn</a>
        <span aria-hidden="true">·</span>
        <a href="https://x.com/pw_cannon" aria-label="X">&#x1D54F;</a>
      </nav>
    </div>
  </header>

  <section class="introduction" aria-label="About">
    <p>I’m an independent AI researcher funded by <a href="https://bluedot.org/">BlueDot Impact</a>. My current work addresses robust oversight for language-model reasoning. I study when learned verifiers become unreliable under inference-time search, how high-confidence false approvals occur, and when systems should defer rather than trust a verifier’s judgement.</p>

    <p>I have a PhD in statistics from the University of Bristol, where I worked on particle MCMC for population genetics with <a href="https://scholar.google.co.uk/citations?hl=en&amp;user=kcsbLrAAAAAJ&amp;view_op=list_works">Christophe Andrieu</a> and <a href="https://scholar.google.co.uk/citations?hl=en&amp;user=2K3F0MMAAAAJ">Mark Beaumont</a>.</p>

    <p>At <a href="https://www.improbable.io/">Improbable</a>, I developed methods for calibrating large multi-agent simulations against real-world data. I later co-founded a computer-vision startup building large-scale 3D representations with neural radiance fields and Gaussian splats, before joining <a href="https://amazon.jobs/content/en-gb/teams/agi">Amazon AGI</a> to work on multimodal foundation models for speech and audio.</p>
  </section>

  <section class="work" aria-labelledby="work-heading">
    <h2 id="work-heading">Selected work</h2>
    {% include selected-work.html %}
  </section>

  <hr class="work-end" aria-hidden="true">

  {% if site.posts.size > 0 %}
  <footer class="home-footer">
    <a href="{{ "/blog/" | relative_url }}">All writing <span class="writing-link-arrow" aria-hidden="true">→</span></a>
  </footer>
  {% endif %}

</main>
