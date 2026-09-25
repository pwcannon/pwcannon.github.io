(function () {
  var desktopNotes = window.matchMedia('(min-width: 1269px)');
  var page = document.querySelector('.prototype-page, .article-shell');
  if (!page) return;

  // Keep axis-label and caption gaps in body-line units, outside the SVG.
  var gaoFigure = page.querySelector('#fig-gao-proxy-gold-overoptimization figure');
  if (gaoFigure) {
    var axisLabel = document.createElement('div');
    axisLabel.className = 'figure-x-axis-label';
    axisLabel.textContent = 'More optimization against the proxy →';
    gaoFigure.insertBefore(axisLabel, gaoFigure.querySelector('figcaption'));
  }

  // Quarto emits the figure prefix as text; wrap only that prefix for colour.
  page.querySelectorAll('figcaption').forEach(function (caption) {
    var first = caption.firstChild;
    while (first && first.nodeType === 3 && !first.textContent.trim()) {
      first = first.nextSibling;
    }
    if (!first || first.nodeType !== 3) return;
    var match = first.textContent.match(/^(\s*)(Figure[\s\u00a0]+\d+:)/);
    if (!match) return;
    var prefix = document.createElement('span');
    prefix.className = 'figure-number';
    prefix.textContent = match[2];
    first.textContent = first.textContent.slice(match[0].length);
    caption.insertBefore(prefix, first);
  });

  var toc = page.querySelector('.article-toc');
  if (toc) {
    var tocToggle = toc.querySelector('.article-toc-toggle');
    var tocToggleLabel = toc.querySelector('.article-toc-toggle-label');
    var tocToggleIcon = toc.querySelector('.article-toc-toggle-icon');
    var nestedTocLists = Array.prototype.slice.call(
      toc.querySelectorAll('.article-toc-level-2')
    );

    function setFullTocVisible(expanded) {
      toc.classList.toggle('is-expanded', expanded);
      tocToggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');

      nestedTocLists.forEach(function (list) {
        list.hidden = !expanded;
      });

      tocToggleLabel.textContent = expanded
        ? 'Show sections only'
        : 'Show full contents';
      tocToggleIcon.textContent = expanded ? '−' : '+';
    }

    if (tocToggle && tocToggleLabel && tocToggleIcon && nestedTocLists.length) {
      setFullTocVisible(false);
      tocToggle.addEventListener('click', function () {
        setFullTocVisible(tocToggle.getAttribute('aria-expanded') !== 'true');
        scheduleNotePositioning();
      });
    } else if (tocToggle) {
      tocToggle.hidden = true;
    }
  }

  var notes = Array.prototype.slice.call(
    page.querySelectorAll('.margin-note[data-ref]')
  );
  var homes = new Map();


  notes.forEach(function (note) {
    var marker = document.createComment('margin-note-home');
    note.parentNode.insertBefore(marker, note);
    homes.set(note, marker);
  });

  function restoreNotes() {
    notes.forEach(function (note) {
      var marker = homes.get(note);
      if (marker && marker.parentNode && marker.nextSibling !== note) {
        marker.parentNode.insertBefore(note, marker.nextSibling);
      }
    });
  }

  function updateReferenceTargets() {
    notes.forEach(function (note) {
      var reference = document.getElementById(note.getAttribute('data-ref'));
      if (!reference) return;

      var link = reference.querySelector('a');
      var target = desktopNotes.matches
        ? note.id
        : note.getAttribute('data-endnote');

      if (link && target) {
        link.setAttribute('href', '#' + target);
        link.setAttribute('aria-describedby', target);
      }
    });
  }

  function prepareCollapsibleNotes() {
    notes.forEach(function (note) {
      var body = note.querySelector('.margin-note-body');
      note.classList.remove('is-collapsible', 'is-expanded');
      if (!desktopNotes.matches || !body) return;

      var collapsedNoteHeight = parseFloat(getComputedStyle(body).lineHeight) * 10;
      note.style.setProperty("--note-fold-height", collapsedNoteHeight + "px");
      note.style.setProperty("--note-full-height", body.scrollHeight + "px");
      if (body.scrollHeight > collapsedNoteHeight + 1) {
        note.classList.add('is-collapsible');
      }
    });
  }

  function positionMarginNotes() {
    restoreNotes();

    if (!desktopNotes.matches) {
      notes.forEach(function (note) {
        note.style.removeProperty('top');
      });
      return;
    }

    var noteContainer = page.querySelector(".article-document");
    var pageRect = noteContainer.getBoundingClientRect();
    var pageTop = pageRect.top + window.scrollY;
    var scale = pageRect.width / noteContainer.offsetWidth;
    var noteGap = parseFloat(getComputedStyle(noteContainer).getPropertyValue('--space-md'));
    var previousBottom = -Infinity;

    notes.forEach(function (note) {
      var reference = document.getElementById(note.getAttribute('data-ref'));
      if (!reference) return;

      var referenceTop = reference.getBoundingClientRect().top + window.scrollY;
      var desiredTop = (referenceTop - pageTop) / scale;
      var top = Math.ceil(Math.max(desiredTop, previousBottom + noteGap) * 4) / 4;
      note.style.top = top + 'px';
      previousBottom = top + note.getBoundingClientRect().height / scale;
    });
  }

  var positioningFrame = null;
  var positioningUntil = 0;
  function scheduleNotePositioning() {
    positioningUntil = performance.now() + 360;
    if (positioningFrame !== null) return;
    function tick(now) {
      positionMarginNotes();
      positioningFrame = now < positioningUntil
        ? window.requestAnimationFrame(tick) : null;
    }
    positioningFrame = window.requestAnimationFrame(tick);
  }

  var closeTimers = new Map();
  function cancelNoteClose(note) {
    window.clearTimeout(closeTimers.get(note));
    closeTimers.delete(note);
  }
  function scheduleNoteClose(reference, note) {
    cancelNoteClose(note);
    closeTimers.set(note, window.setTimeout(function () {
      closeTimers.delete(note);
      syncLinkedState(reference, note, false);
    }, 200));
  }

  function syncLinkedState(reference, note, ignoreFocus) {
    var active = reference.matches(':hover') || note.matches(':hover');
    if (!ignoreFocus) {
      active = active || reference.matches(':focus-within') ||
        note.matches(':focus-within');
    }
    reference.classList.toggle('is-linked-highlight', active);
    note.classList.toggle('is-linked-highlight', active);
    note.classList.toggle(
      'is-expanded',
      active && note.classList.contains('is-collapsible')
    );
    scheduleNotePositioning();
  }

  function activateLinkedState(reference, note) {
    cancelNoteClose(note);
    reference.classList.add('is-linked-highlight');
    note.classList.add('is-linked-highlight');
    if (note.classList.contains('is-collapsible')) {
      note.classList.add('is-expanded');
    }
    scheduleNotePositioning();
  }

  notes.forEach(function (note) {
    var reference = document.getElementById(note.getAttribute('data-ref'));
    if (!reference) return;

    [reference, note].forEach(function (element) {
      element.addEventListener('pointerenter', function () {
        activateLinkedState(reference, note);
      });
      element.addEventListener('pointerleave', function () {
        scheduleNoteClose(reference, note);
      });
      element.addEventListener('focusin', function () {
        activateLinkedState(reference, note);
      });
      element.addEventListener('focusout', function () {
        window.requestAnimationFrame(function () {
          syncLinkedState(reference, note);
        });
      });
    });

  });

  function refreshNotes() {
    updateReferenceTargets();
    prepareCollapsibleNotes();
    positionMarginNotes();
  }

  function resetCollapsedState() {
    page.querySelectorAll('details').forEach(function (box) {
      box.open = false;
    });
    if (tocToggle && nestedTocLists.length) setFullTocVisible(false);
    notes.forEach(function (note) {
      cancelNoteClose(note);
      note.classList.remove('is-expanded', 'is-linked-highlight');
    });
    page.querySelectorAll('.margin-note-ref').forEach(function (reference) {
      reference.classList.remove('is-linked-highlight');
    });
    refreshNotes();
  }
  resetCollapsedState();
  // Also reset state restored by back/forward navigation or the browser cache.
  window.addEventListener('pageshow', resetCollapsedState);
  window.addEventListener('load', refreshNotes);
  window.addEventListener('resize', refreshNotes);
  page.addEventListener('toggle', scheduleNotePositioning, true);
  page.querySelectorAll('img').forEach(function (image) {
    image.addEventListener('load', scheduleNotePositioning);
  });

  if (desktopNotes.addEventListener) {
    desktopNotes.addEventListener('change', refreshNotes);
  }

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(refreshNotes);
  }

  if (window.MathJax && window.MathJax.startup) {
    window.MathJax.startup.promise.then(refreshNotes);
  }
})();
