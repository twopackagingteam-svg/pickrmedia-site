/* WAHL AIR — interactions */
(function () {
  'use strict';
  const fine = matchMedia('(pointer:fine)').matches;
  const motionOK = matchMedia('(prefers-reduced-motion: no-preference)').matches;

  /* ---------- nav ---------- */
  const nav = document.querySelector('.nav');
  const onScroll = () => nav && nav.classList.toggle('scrolled', window.scrollY > 12);
  onScroll();
  addEventListener('scroll', onScroll, { passive: true });

  const burger = document.querySelector('.nav-burger');
  const links = document.querySelector('.nav-links');
  if (burger && links) {
    burger.addEventListener('click', () => {
      const open = burger.classList.toggle('open');
      links.classList.toggle('open', open);
    });
    links.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      burger.classList.remove('open'); links.classList.remove('open');
    }));
  }

  /* dropdowns — hover on desktop, tap on mobile */
  document.querySelectorAll('.nav-item').forEach(item => {
    const btn = item.querySelector('button');
    if (!btn) return;
    if (fine && innerWidth > 1120) {
      let t;
      item.addEventListener('mouseenter', () => { clearTimeout(t); item.classList.add('open'); });
      item.addEventListener('mouseleave', () => { t = setTimeout(() => item.classList.remove('open'), 120); });
    }
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const wasOpen = item.classList.contains('open');
      document.querySelectorAll('.nav-item.open').forEach(o => o !== item && o.classList.remove('open'));
      item.classList.toggle('open', !wasOpen);
    });
  });
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-item')) document.querySelectorAll('.nav-item.open').forEach(o => o.classList.remove('open'));
  });
  addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    document.querySelectorAll('.nav-item.open').forEach(o => o.classList.remove('open'));
    if (links && links.classList.contains('open')) burger.click();
  });

  /* ---------- scroll reveals ---------- */
  const io = new IntersectionObserver((es) => {
    es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { threshold: 0.1, rootMargin: '0px 0px -5% 0px' });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));

  /* ---------- counters ---------- */
  const fmt = new Intl.NumberFormat('en-US');
  const cio = new IntersectionObserver((es) => {
    es.forEach(e => {
      if (!e.isIntersecting) return;
      cio.unobserve(e.target);
      const el = e.target;
      const target = parseFloat(el.dataset.count);
      const dec = parseInt(el.dataset.dec || '0', 10);
      const pre = el.dataset.prefix || '', suf = el.dataset.suffix || '';
      const dur = 1700, t0 = performance.now();
      const tick = (t) => {
        const p = Math.min((t - t0) / dur, 1);
        const v = target * (1 - Math.pow(1 - p, 4));
        el.textContent = pre + (dec ? v.toFixed(dec) : fmt.format(Math.round(v))) + suf;
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }, { threshold: 0.45 });
  document.querySelectorAll('[data-count]').forEach(el => cio.observe(el));

  /* ---------- scroll progress ---------- */
  const bar = document.querySelector('.progress');
  if (bar) {
    const prog = () => {
      const max = document.documentElement.scrollHeight - innerHeight;
      bar.style.width = (max > 0 ? (scrollY / max) * 100 : 0) + '%';
    };
    prog(); addEventListener('scroll', prog, { passive: true });
  }

  /* ---------- hero cursor glow ---------- */
  const hero = document.querySelector('.hero'), glow = document.querySelector('.hero-glow');
  if (hero && glow && fine) {
    hero.addEventListener('pointermove', (e) => {
      const r = hero.getBoundingClientRect();
      glow.style.left = (e.clientX - r.left) + 'px';
      glow.style.top = (e.clientY - r.top) + 'px';
      glow.style.opacity = '1';
    });
    hero.addEventListener('pointerleave', () => { glow.style.opacity = '0'; });
  }

  /* ---------- hero video parallax ---------- */
  const heroMedia = document.querySelector('.hero-media');
  if (heroMedia && motionOK) {
    addEventListener('scroll', () => {
      if (scrollY < innerHeight * 1.2) heroMedia.style.transform = 'translateY(' + scrollY * 0.22 + 'px) scale(1.04)';
    }, { passive: true });
  }

  /* ---------- magnetic buttons ---------- */
  if (fine && motionOK) {
    document.querySelectorAll('.btn').forEach(btn => {
      const mag = btn.querySelector('.mag');
      btn.addEventListener('pointermove', (e) => {
        const r = btn.getBoundingClientRect();
        const x = (e.clientX - r.left - r.width / 2) / r.width;
        const y = (e.clientY - r.top - r.height / 2) / r.height;
        btn.style.setProperty('transform', 'translate(' + x * 6 + 'px,' + (y * 5 - 2) + 'px)');
        if (mag) mag.style.transform = 'translate(' + x * 5 + 'px,' + y * 4 + 'px)';
      });
      btn.addEventListener('pointerleave', () => {
        btn.style.removeProperty('transform');
        if (mag) mag.style.transform = '';
      });
    });
  }

  /* ---------- card tilt (services, gallery, reviews) ---------- */
  const tilt = (el, max) => {
    el.addEventListener('pointermove', (e) => {
      const r = el.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - .5;
      const y = (e.clientY - r.top) / r.height - .5;
      el.style.transform = 'perspective(1000px) rotateY(' + (x * max) + 'deg) rotateX(' + (-y * max) + 'deg) translateY(-6px)';
    });
    el.addEventListener('pointerleave', () => { el.style.transform = ''; });
  };
  if (fine && motionOK) document.querySelectorAll('[data-tilt]').forEach(el => tilt(el, parseFloat(el.dataset.tilt) || 6));

  /* ============================================================
     REVIEW TICKER — built from reviews.json
     ============================================================ */
  const ticker = document.querySelector('.ticker');
  if (ticker) {
    const AV = ['#F10310', '#0B0E13', '#68727F', '#C4020D', '#12161E'];
    const star = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2l2.9 6.3 6.9.8-5.1 4.7 1.4 6.8L12 17.3 5.9 20.6l1.4-6.8L2.2 9.1l6.9-.8z"/></svg>';
    const gmark = '<svg class="gmark" viewBox="0 0 48 48" aria-hidden="true"><path fill="#4285F4" d="M45 24.5c0-1.6-.1-2.7-.4-4H24v7.6h12c-.2 2-1.5 5-4.4 7l6.7 5.2C42.2 36.6 45 31 45 24.5z"/><path fill="#34A853" d="M24 46c5.9 0 10.9-2 14.5-5.3l-6.9-5.4c-1.9 1.3-4.4 2.2-7.6 2.2-5.8 0-10.7-3.8-12.5-9.1l-7.1 5.5C8 41.3 15.4 46 24 46z"/><path fill="#FBBC05" d="M11.5 28.4c-.5-1.4-.7-2.9-.7-4.4s.3-3 .7-4.4l-7.1-5.5C2.9 17 2 20.4 2 24s.9 7 2.4 9.9z"/><path fill="#EA4335" d="M24 10.6c3.3 0 5.5 1.4 6.8 2.6l5.9-5.8C33 4 29 2 24 2 15.4 2 8 6.7 4.4 14.1l7.1 5.5C13.3 14.4 18.2 10.6 24 10.6z"/></svg>';
    const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

    const card = (r, i) => {
      const initials = r.name.trim().split(/\s+/).slice(0, 2).map(w => w[0]).join('').toUpperCase();
      return '<article class="rcard" data-tilt="5">' +
        '<div class="rcard-top"><div class="stars" aria-label="' + r.stars + ' out of 5 stars">' + star.repeat(r.stars) + '</div>' + gmark + '</div>' +
        '<blockquote>&ldquo;' + esc(r.pull) + '&rdquo;</blockquote>' +
        '<p>' + esc(r.text) + '</p>' +
        '<footer><span class="rav" style="background:' + AV[i % AV.length] + '">' + esc(initials) + '</span>' +
        '<span><b>' + esc(r.name) + '</b><small>' + esc(r.when) + (r.service ? ' &middot; ' + esc(r.service) : '') + '</small></span>' +
        '<span class="verified"><svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/></svg>Google</span>' +
        '</footer></article>';
    };

    fetch('reviews.json?v=1').then(r => r.json()).then(data => {
      const list = data.reviews || [];
      const mid = Math.ceil(list.length / 2);
      const rows = [list.slice(0, mid), list.slice(mid)];
      ticker.innerHTML = rows.map((row, ri) => {
        const html = row.map((r, i) => card(r, i + ri * mid)).join('');
        return '<div class="tick-row ' + (ri ? 'b' : 'a') + '">' + html + html + '</div>';
      }).join('');

      ticker.classList.remove('paused');
      if (fine && motionOK) ticker.querySelectorAll('.rcard').forEach(c => tilt(c, 5));

      /* fill the aggregate header */
      const agg = data.aggregate || {};
      const num = document.querySelector('[data-agg-rating]');
      if (num) { num.dataset.count = agg.rating; num.dataset.dec = '1'; cio.observe(num); }
      const cnt = document.querySelector('[data-agg-count]');
      if (cnt) cnt.textContent = agg.count + '+ Google reviews';
      document.querySelectorAll('[data-agg-count-inline]').forEach(e => { e.textContent = agg.count; });

      const topics = document.querySelector('.revs-topics');
      if (topics && data.topics) {
        topics.innerHTML = data.topics.map(t =>
          '<span class="topic"><b>' + t.count + '</b> ' + esc(t.label) + '</span>').join('');
      }
    }).catch(() => {
      ticker.innerHTML = '<p style="color:rgba(255,255,255,.6);text-align:center;width:100%">' +
        'Read our reviews on Google &mdash; 4.9 stars across 218 reviews.</p>';
    });
  }

  /* ---------- image slots: hide broken so the brand block shows ---------- */
  document.querySelectorAll('img[data-slot]').forEach(img => {
    const fail = () => { img.style.display = 'none'; img.closest('[data-slot-wrap]')?.classList.add('empty'); };
    img.addEventListener('error', fail);
    if (img.complete && img.naturalWidth === 0) fail();
  });

  /* ---------- hero video: fall back to the poster if it will not play ---------- */
  document.querySelectorAll('.hero-media video').forEach(v => {
    const src = v.querySelector('source');
    if (src) src.addEventListener('error', () => { v.style.display = 'none'; });
    const p = v.play();
    if (p && p.catch) p.catch(() => { v.style.display = 'none'; });
  });

  /* ---------- contact form ---------- */
  const form = document.getElementById('contact-form');
  if (form) {
    const status = document.getElementById('form-status');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type=submit]');
      const label = btn.innerHTML;
      btn.disabled = true; btn.innerHTML = 'Sending&hellip;';
      status.className = 'form-status';
      try {
        const res = await fetch(form.getAttribute('action'), { method: 'POST', body: new FormData(form) });
        const data = await res.json().catch(() => ({}));
        if (!res.ok || !data.ok) throw new Error(data.error || 'send failed');
        status.textContent = 'Thank you — your request is in. Someone from Wahl Air will call you back shortly.';
        status.classList.add('ok'); form.reset();
      } catch (err) {
        status.textContent = 'That did not go through. Please call us at (602) 242-2353 and we will take care of you right away.';
        status.classList.add('err');
      } finally {
        btn.disabled = false; btn.innerHTML = label;
        status.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    });
  }
})();
