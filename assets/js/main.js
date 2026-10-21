document.addEventListener('DOMContentLoaded', () => {
  const PER = 4; // jumlah video per halaman
  const buttons = Array.from(document.querySelectorAll('.filter-btn'));
  const grid = document.getElementById('videoGrid');
  const nav = document.getElementById('homePagination');
  const cards = Array.from(document.querySelectorAll('.video-card'));
  if (!grid || !nav) return;

  let filter = 'all';
  let page = 1;

  function matching() {
    return cards.filter(c => filter === 'all' || c.dataset.category === filter);
  }

  function makeBtn(label, target, opt) {
    opt = opt || {};
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = label;
    b.className = 'page-btn' + (opt.active ? ' active' : '');
    b.setAttribute('aria-label', opt.aria || ('Halaman ' + target));
    if (opt.active) b.setAttribute('aria-current', 'page');
    if (opt.disabled) b.disabled = true;
    b.addEventListener('click', () => render(target, true));
    return b;
  }

  function pageList(total) {
    const out = [];
    for (let i = 1; i <= total; i++) {
      if (i === 1 || i === total || Math.abs(i - page) <= 1) out.push(i);
      else if (out[out.length - 1] !== '...') out.push('...');
    }
    return out;
  }

  function render(p, scroll) {
    const list = matching();
    const total = Math.max(1, Math.ceil(list.length / PER));
    page = Math.min(Math.max(p, 1), total);

    cards.forEach(c => { c.style.display = 'none'; });
    list.slice((page - 1) * PER, page * PER).forEach(c => { c.style.display = ''; });

    nav.innerHTML = '';
    if (total > 1) {
      nav.appendChild(makeBtn('\u2039', page - 1, { disabled: page === 1, aria: 'Halaman sebelumnya' }));
      pageList(total).forEach(x => {
        if (x === '...') {
          const d = document.createElement('span');
          d.className = 'page-dots';
          d.textContent = '\u2026';
          nav.appendChild(d);
        } else {
          nav.appendChild(makeBtn(x, x, { active: x === page }));
        }
      });
      nav.appendChild(makeBtn('\u203a', page + 1, { disabled: page === total, aria: 'Halaman berikutnya' }));
    }

    try { history.replaceState(null, '', (filter === 'all' && page === 1) ? location.pathname + location.search : '#' + filter + '-' + page); } catch (e) {}
    if (scroll) grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  buttons.forEach(b => b.addEventListener('click', () => {
    buttons.forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    filter = b.dataset.filter;
    render(1, false);
  }));

  // Pulihkan filter & halaman dari URL (mis. saat tombol Kembali dari halaman video)
  const m = /^#([a-z]+)-(\d+)$/.exec(location.hash);
  let startPage = 1;
  if (m && (m[1] === 'all' || buttons.some(b => b.dataset.filter === m[1]))) {
    filter = m[1];
    startPage = parseInt(m[2], 10) || 1;
    buttons.forEach(b => b.classList.toggle('active', b.dataset.filter === filter));
  }
  render(startPage, false);
});
