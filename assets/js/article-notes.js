(function () {
  var desktopNotes = window.matchMedia("(min-width: 1269px)");
  var page = document.querySelector(".article-shell");
  if (!page) return;

  var toc = page.querySelector(".article-toc");
  if (toc) {
    var tocToggle = toc.querySelector(".article-toc-toggle");
    var tocToggleLabel = toc.querySelector(".article-toc-toggle-label");
    var tocToggleIcon = toc.querySelector(".article-toc-toggle-icon");
    var nestedTocLists = Array.prototype.slice.call(
      toc.querySelectorAll(".article-toc-level-2")
    );

    function setFullTocVisible(expanded) {
      toc.classList.toggle("is-expanded", expanded);
      tocToggle.setAttribute("aria-expanded", expanded ? "true" : "false");

      nestedTocLists.forEach(function (list) {
        list.hidden = !expanded;
      });

      tocToggleLabel.textContent = expanded
        ? "Show sections only"
        : "Show full contents";
      tocToggleIcon.textContent = expanded ? "−" : "+";
    }

    if (tocToggle && tocToggleLabel && tocToggleIcon && nestedTocLists.length) {
      setFullTocVisible(false);
      tocToggle.addEventListener("click", function () {
        setFullTocVisible(tocToggle.getAttribute("aria-expanded") !== "true");
      });
    } else if (tocToggle) {
      tocToggle.hidden = true;
    }
  }

  var notes = Array.prototype.slice.call(
    page.querySelectorAll(".margin-note[data-ref]")
  );
  if (!notes.length) return;

  // The source notes remain permanent endnotes. Only copies enter the margin.
  var endnotes = notes;
  var section = document.createElement("section");
  section.className = "article-endnotes";
  section.setAttribute("aria-label", "Footnotes");
  page.querySelector(".article-content").appendChild(section);
  notes = endnotes.map(function (note) {
    section.appendChild(note);
    var copy = note.cloneNode(true);
    copy.id = note.id + "-margin";
    copy.classList.add("desktop-margin-note");
    copy.setAttribute("aria-hidden", "true");
    copy.removeAttribute("tabindex");
    copy.querySelectorAll("[id]").forEach(function (el) { el.removeAttribute("id"); });
    copy.querySelectorAll("a").forEach(function (el) { el.tabIndex = -1; });
    page.querySelector(".article-content").appendChild(copy);
    return copy;
  });

  function positionMarginNotes() {
    if (!desktopNotes.matches) {
      notes.forEach(function (note) { note.style.removeProperty("top"); });
      return;
    }

    var pageTop = page.getBoundingClientRect().top + window.scrollY;
    var previousBottom = -Infinity;

    notes.forEach(function (note) {
      var reference = document.getElementById(note.getAttribute("data-ref"));
      if (!reference) return;

      var referenceTop =
        reference.getBoundingClientRect().top + window.scrollY;
      var desiredTop = referenceTop - pageTop - 8;
      var top = Math.max(desiredTop, previousBottom + 18);
      note.style.top = top + "px";
      previousBottom = top + note.offsetHeight;
    });
  }

  function syncHighlight(reference, note) {
    var active =
      reference.matches(":hover, :focus-within") ||
      note.matches(":hover, :focus-within");
    reference.classList.toggle("is-linked-highlight", active);
    note.classList.toggle("is-linked-highlight", active);
  }

  notes.forEach(function (note) {
    var reference = document.getElementById(note.getAttribute("data-ref"));
    if (!reference) return;

    [reference, note].forEach(function (element) {
      element.addEventListener("pointerenter", function () {
        reference.classList.add("is-linked-highlight");
        note.classList.add("is-linked-highlight");
      });
      element.addEventListener("pointerleave", function () {
        window.requestAnimationFrame(function () {
          syncHighlight(reference, note);
        });
      });
      element.addEventListener("focusin", function () {
        reference.classList.add("is-linked-highlight");
        note.classList.add("is-linked-highlight");
      });
      element.addEventListener("focusout", function () {
        window.requestAnimationFrame(function () {
          syncHighlight(reference, note);
        });
      });
    });

    var referenceLink = reference.querySelector("a");
    if (referenceLink) {
      referenceLink.addEventListener("click", function () {
        window.setTimeout(function () {
          var target = document.getElementById(referenceLink.hash.slice(1));
          if (target) target.focus({ preventScroll: true });
        }, 0);
      });
    }
  });

  positionMarginNotes();
  window.addEventListener("load", positionMarginNotes);
  window.addEventListener("resize", positionMarginNotes);

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(positionMarginNotes);
  }

  if (window.MathJax && window.MathJax.startup) {
    window.MathJax.startup.promise.then(positionMarginNotes);
  }
})();
