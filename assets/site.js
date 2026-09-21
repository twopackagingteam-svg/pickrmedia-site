// Pickr Media — site behavior. Everything here is progressive: the page works without it.
(function () {
  var root = document.documentElement;
  root.classList.add('js');

  var yr = document.getElementById('yr');
  if (yr) yr.textContent = new Date().getFullYear();

  // Reveal on scroll.
  var items = [].slice.call(document.querySelectorAll('.reveal'));
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var siblings = [].slice.call(e.target.parentNode.children).filter(function (n) { return n.classList.contains('reveal'); });
        e.target.style.transitionDelay = Math.min(siblings.indexOf(e.target), 5) * 70 + 'ms';
        e.target.classList.add('in');
        io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    items.forEach(function (n) { io.observe(n); });
  } else {
    items.forEach(function (n) { n.classList.add('in'); });
  }

  // Preview request form.
  var form = document.getElementById('preview-form');
  if (!form) return;
  var status = document.getElementById('form-status');
  var button = form.querySelector('button[type="submit"]');

  function say(kind, html) { status.className = 'form__status ' + kind; status.innerHTML = html; }

  function mailtoFallback(data) {
    var body = 'Business: ' + data.business + '\nLink: ' + data.link + '\nName: ' + data.name + '\nEmail: ' + data.email + (data.notes ? '\nNotes: ' + data.notes : '');
    return 'mailto:hello@pickrmedia.com?subject=' + encodeURIComponent('Free website preview — ' + data.business) + '&body=' + encodeURIComponent(body);
  }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var firstBad = null;
    [].forEach.call(form.querySelectorAll('[required]'), function (el) {
      var bad = !el.value.trim() || (el.type === 'email' && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(el.value.trim()));
      if (el.type === 'url' && !bad) {
        var v = el.value.trim();
        if (!/^https?:\/\//i.test(v)) { v = 'https://' + v; el.value = v; }
        try { new URL(v); } catch (e) { bad = true; }
      }
      el.setAttribute('aria-invalid', bad ? 'true' : 'false');
      if (bad && !firstBad) firstBad = el;
    });
    if (firstBad) { say('err', 'Please check the highlighted field.'); firstBad.focus(); return; }

    var data = {};
    new FormData(form).forEach(function (v, k) { data[k] = String(v).trim(); });
    button.disabled = true;
    say('', 'Sending…');

    fetch(form.action, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
      .then(function (r) { if (!r.ok) throw new Error('bad status'); return r.json(); })
      .then(function () {
        form.reset();
        say('ok', 'Got it. Your preview will arrive by email, usually the same day.');
      })
      .catch(function () {
        say('err', 'That didn’t send. <a href="' + mailtoFallback(data) + '">Email it to us instead</a> and we’ll start right away.');
      })
      .then(function () { button.disabled = false; });
  });
})();


