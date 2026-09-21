/* CSA — interactions */
(function () {
  'use strict';

  /* nav scroll state (a nav that starts .scrolled stays solid) */
  const nav = document.querySelector('.nav');
  const navSolid = nav && nav.classList.contains('scrolled');
  const onScroll = () => nav && nav.classList.toggle('scrolled', navSolid || window.scrollY > 40);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* mobile burger */
  const burger = document.querySelector('.nav-burger');
  const links = document.querySelector('.nav-links');
  if (burger && links) {
    burger.addEventListener('click', () => {
      burger.classList.toggle('open');
      links.classList.toggle('open');
    });
    links.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      burger.classList.remove('open');
      links.classList.remove('open');
    }));
  }

  /* scroll reveals */
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));

  /* animated counters — <span data-count="1820000" data-prefix="$" data-suffix=""> */
  const fmt = new Intl.NumberFormat('en-US');
  const cio = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      cio.unobserve(e.target);
      const el = e.target;
      const target = parseFloat(el.dataset.count);
      const prefix = el.dataset.prefix || '';
      const suffix = el.dataset.suffix || '';
      const dur = 1800;
      const t0 = performance.now();
      const tick = (t) => {
        const p = Math.min((t - t0) / dur, 1);
        const eased = 1 - Math.pow(1 - p, 4);
        el.textContent = prefix + fmt.format(Math.round(target * eased)) + suffix;
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }, { threshold: 0.4 });
  document.querySelectorAll('[data-count]').forEach(el => cio.observe(el));

  /* scroll progress bar */
  const bar = document.querySelector('.progress');
  if (bar) {
    const prog = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = (max > 0 ? (window.scrollY / max) * 100 : 0) + '%';
    };
    prog();
    window.addEventListener('scroll', prog, { passive: true });
  }

  /* ghost watermark parallax drift */
  const ghosts = document.querySelectorAll('.ghost[data-drift], .ghost-mark[data-drift]');
  if (ghosts.length && matchMedia('(prefers-reduced-motion: no-preference)').matches) {
    const drift = () => {
      const vh = window.innerHeight;
      ghosts.forEach(g => {
        const r = g.getBoundingClientRect();
        const offset = (r.top + r.height / 2 - vh / 2) / vh;
        const speed = parseFloat(g.dataset.drift) || 40;
        const base = g.classList.contains('ghost-mark') ? 'translateY(-50%) ' : '';
        g.style.transform = base + 'translateY(' + (-offset * speed) + 'px)';
      });
    };
    drift();
    window.addEventListener('scroll', drift, { passive: true });
  }

  /* hero cursor glow */
  const hero = document.querySelector('.hero');
  const glow = document.querySelector('.hero-glow');
  if (hero && glow && matchMedia('(pointer:fine)').matches) {
    hero.addEventListener('mousemove', (e) => {
      const r = hero.getBoundingClientRect();
      glow.style.left = (e.clientX - r.left) + 'px';
      glow.style.top = (e.clientY - r.top) + 'px';
      glow.style.opacity = '1';
    });
    hero.addEventListener('mouseleave', () => { glow.style.opacity = '0'; });
  }

  /* subtle hero parallax */
  const heroMedia = document.querySelector('.hero-media img');
  if (heroMedia) {
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      if (y < window.innerHeight) heroMedia.style.transform = 'scale(1.06) translateY(' + y * 0.18 + 'px)';
    }, { passive: true });
  }

  /* 3D tilt on project cards (pointer only) */
  if (matchMedia('(pointer:fine)').matches) {
    document.querySelectorAll('.proj').forEach(card => {
      card.addEventListener('mousemove', (e) => {
        const r = card.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - 0.5;
        const y = (e.clientY - r.top) / r.height - 0.5;
        card.style.transform = 'perspective(1100px) rotateY(' + (x * 7) + 'deg) rotateX(' + (-y * 7) + 'deg) translateY(-4px)';
      });
      card.addEventListener('mouseleave', () => { card.style.transform = ''; });
    });
  }

  /* touch devices: cards are tapped, not hovered */
  if (!matchMedia('(hover:hover)').matches) {
    document.querySelectorAll('.flip-front .hint').forEach(h => { h.textContent = 'Tap to explore'; });
  }

  /* flip cards: tap support on touch */
  document.querySelectorAll('.flip').forEach(card => {
    card.addEventListener('click', (e) => {
      if (e.target.closest('a')) return;
      if (!matchMedia('(hover:hover)').matches) card.classList.toggle('flipped');
    });
  });

  /* services page scrollspy */
  const svcLinks = document.querySelectorAll('.svc-nav a');
  if (svcLinks.length) {
    const blocks = [...document.querySelectorAll('.svc-block[id]')];
    const spy = () => {
      let current = blocks[0];
      blocks.forEach(b => { if (b.getBoundingClientRect().top < 180) current = b; });
      svcLinks.forEach(a => a.classList.toggle('active', a.getAttribute('href') === '#' + current.id));
    };
    spy();
    window.addEventListener('scroll', spy, { passive: true });
  }

  /* hero video: hide if the file isn't there yet so the image/fallback shows */
  document.querySelectorAll('.hero-media video').forEach(v => {
    const src = v.querySelector('source');
    if (src) src.addEventListener('error', () => { v.style.display = 'none'; });
  });

  /* image slots: hide broken imgs so fallbacks show */
  document.querySelectorAll('img[data-slot]').forEach(img => {
    img.addEventListener('error', () => { img.style.display = 'none'; });
    if (img.complete && img.naturalWidth === 0) img.style.display = 'none';
  });

  /* project drawings upload zone */
  const MAX_UPLOAD_BYTES = 120 * 1024 * 1024; // 120MB — server caps the whole request at 128MB
  const fmtBytes = (n) => {
    if (n < 1024) return n + ' B';
    if (n < 1024 * 1024) return (n / 1024).toFixed(0) + ' KB';
    return (n / (1024 * 1024)).toFixed(1) + ' MB';
  };
  const uploadZone = document.getElementById('upload-zone');
  const uploadInput = document.getElementById('f-plans');
  let selectedFiles = [];
  let renderUploads = () => {};
  if (uploadZone && uploadInput) {
    const list = document.getElementById('upload-list');
    const totalEl = document.getElementById('upload-total');

    const syncInput = () => {
      const dt = new DataTransfer();
      selectedFiles.forEach((f) => dt.items.add(f));
      uploadInput.files = dt.files;
    };

    const render = () => {
      list.innerHTML = '';
      selectedFiles.forEach((file, i) => {
        const chip = document.createElement('div');
        chip.className = 'upload-chip';
        chip.innerHTML = `<span class="name">${file.name}</span><span class="size">${fmtBytes(file.size)}</span>`;
        const rm = document.createElement('button');
        rm.type = 'button';
        rm.setAttribute('aria-label', 'Remove ' + file.name);
        rm.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6L6 18"/></svg>';
        rm.addEventListener('click', () => { selectedFiles.splice(i, 1); syncInput(); render(); });
        chip.appendChild(rm);
        list.appendChild(chip);
      });
      const total = selectedFiles.reduce((s, f) => s + f.size, 0);
      if (!selectedFiles.length) {
        totalEl.textContent = '';
        totalEl.className = 'upload-total';
      } else if (total > MAX_UPLOAD_BYTES) {
        totalEl.textContent = `${fmtBytes(total)} total — that's over the 120MB limit for a single submission. Remove a file, or email the rest directly to info@csatab.com.`;
        totalEl.className = 'upload-total over';
      } else {
        totalEl.textContent = `${fmtBytes(total)} total, ${selectedFiles.length} file${selectedFiles.length > 1 ? 's' : ''}.`;
        totalEl.className = 'upload-total';
      }
    };

    const addFiles = (fileList) => {
      Array.from(fileList).forEach((f) => selectedFiles.push(f));
      syncInput();
      render();
    };

    renderUploads = render;

    uploadZone.addEventListener('click', () => uploadInput.click());
    uploadZone.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); uploadInput.click(); }
    });
    uploadInput.addEventListener('click', (e) => e.stopPropagation());
    uploadInput.addEventListener('change', () => { addFiles(uploadInput.files); });
    ['dragenter', 'dragover'].forEach((ev) => uploadZone.addEventListener(ev, (e) => {
      e.preventDefault(); e.stopPropagation(); uploadZone.classList.add('drag');
    }));
    ['dragleave', 'drop'].forEach((ev) => uploadZone.addEventListener(ev, (e) => {
      e.preventDefault(); e.stopPropagation(); uploadZone.classList.remove('drag');
    }));
    uploadZone.addEventListener('drop', (e) => {
      if (e.dataTransfer && e.dataTransfer.files) addFiles(e.dataTransfer.files);
    });
  }

  /* contact form */
  const form = document.getElementById('contact-form');
  if (form) {
    const status = document.getElementById('form-status');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const totalUpload = selectedFiles.reduce((s, f) => s + f.size, 0);
      if (totalUpload > MAX_UPLOAD_BYTES) {
        status.textContent = "Your attached files total " + fmtBytes(totalUpload) + ", over the 120MB limit for one submission. Remove a file above, or email the rest directly to info@csatab.com.";
        status.className = 'form-status err';
        status.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        return;
      }
      const btn = form.querySelector('button[type=submit]');
      const label = btn.textContent;
      btn.disabled = true;
      btn.textContent = selectedFiles.length ? 'Uploading…' : 'Sending…';
      status.className = 'form-status';
      try {
        const res = await fetch(form.getAttribute('action'), {
          method: 'POST',
          body: new FormData(form)
        });
        const data = await res.json().catch(() => ({}));
        if (res.ok && data.ok) {
          status.textContent = 'Thank you — your request is in. A member of the CSA team will reach out shortly.';
          status.classList.add('ok');
          form.reset();
          selectedFiles = [];
          renderUploads();
        } else {
          throw new Error(data.error || 'send failed');
        }
      } catch (err) {
        status.textContent = 'Something went wrong sending your message. Please call us at 623-780-0222 and we will take care of you immediately.';
        status.classList.add('err');
      } finally {
        btn.disabled = false;
        btn.textContent = label;
        status.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    });
  }
})();
