---
layout: default
---

<p class="lead">I'm a machine learning researcher with a background in Monte Carlo methods. One idea runs through my work: AI we can trust will know when it doesn't know, when to stop searching, and when its model is wrong. To me these are all problems of sampling and inference.</p>

<p class="body">I have a PhD in statistics from the University of Bristol, where I worked on particle MCMC for population genetics with <a href="https://scholar.google.co.uk/citations?hl=en&user=kcsbLrAAAAAJ&view_op=list_works">Christophe Andrieu</a> and <a href="https://scholar.google.co.uk/citations?hl=en&user=2K3F0MMAAAAJ">Mark Beaumont</a>. This largely revolved around finding tricks to sample from distributions that strongly preferred to be left undisturbed.</p>

<p class="body">I then spent three years at <a href="https://www.improbable.io/">Improbable</a> building methods to calibrate complex simulators against real-world data. It worked beautifully until we asked what happens when the simulator is <em>wrong</em>, which it invariably is. That question turned into a line of papers at NeurIPS, UAI, AISTATS, and others. After, I co-founded a computer vision startup pushing NeRFs and Gaussian splats to their limits, then moved to <a href="https://amazon.jobs/content/en-gb/teams/agi">Amazon AGI</a> to work on large multimodal models for speech and audio.</p>

<p class="body">I now work on AI safety full-time as an independent researcher, funded by <a href="https://bluedot.org">BlueDot Impact</a>.</p>

<a class="cta-link cta-link-1" href="/contact">get in touch →</a>

<hr class="section-break">
<p class="section-label">Direction</p>

<p class="body">In domains with verifiable rewards like mathematics, code, games, and formal reasoning, we're seeing clear progress. Here, sampling and inference have an obvious target. We generate candidates, search over them, spend more compute at test time, and let verification decide what survives. I expect this recipe to matter deeply for scientific discovery, but only if the verification itself is reliable.</p>

<p class="body">I'm most interested in where this recipe breaks. Most of the questions we ask intelligent systems have no straightforward verifier. They involve judgment, context, preference, uncertainty, and disagreement. Current methods average these away. That can be useful, but it leaves us with systems that stay confident even when the target is underspecified – a central difficulty for alignment.</p>

<p class="body">I want to build systems that track that underspecification explicitly, ones that know when to search further, when to ask, when to defer, and when to preserve disagreement rather than resolve it prematurely. My current work is on the mathematical foundations of systems that can act under uncertainty without collapsing it.</p>



<a class="cta-link cta-link-2" href="/blog">read the blog →</a>

<hr class="section-break">
<p class="section-label">Selected publications</p>

{% include publications.html selected=true %}
