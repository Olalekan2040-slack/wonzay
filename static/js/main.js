'use strict';

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   INIT
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
document.addEventListener('DOMContentLoaded', () => {
  initReveal();
  initAnnouncementBar();
  initCartDrawer();
  initSearchOverlay();
  initNewsletterPopup();
  initQuickBuy();
  initToasts();
});

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   SCROLL REVEAL â€” adds .visible class
   CSS: .reveal { opacity:0; transform:translateY(24px); transition:... }
         .reveal.visible { opacity:1; transform:translateY(0); }
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function initReveal() {
  const els = document.querySelectorAll('.reveal');
  if (!els.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });

  els.forEach(el => observer.observe(el));
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   ANNOUNCEMENT BAR CYCLING
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function initAnnouncementBar() {
  const bar   = document.getElementById('announcement-bar');
  if (!bar) return;
  const items = bar.querySelectorAll('[data-announcement]');
  if (items.length <= 1) return;

  let idx = 0;
  const show = i => items.forEach((el, j) => el.style.display = j === i ? 'block' : 'none');

  bar.querySelector('[data-bar-prev]')?.addEventListener('click', () => {
    idx = (idx - 1 + items.length) % items.length; show(idx);
  });
  bar.querySelector('[data-bar-next]')?.addEventListener('click', () => {
    idx = (idx + 1) % items.length; show(idx);
  });
  setInterval(() => { idx = (idx + 1) % items.length; show(idx); }, 5000);
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   CART DRAWER
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function initCartDrawer() {
  const drawer  = document.getElementById('cart-drawer');
  const overlay = document.getElementById('cart-overlay');
  const closeBtn = document.getElementById('cart-close');
  if (!drawer) return;

  const openCart = () => {
    drawer.style.transform = 'translateX(0)';
    if (overlay) overlay.style.display = 'block';
    document.body.style.overflow = 'hidden';
    loadCartDrawer();
  };

  const closeCart = () => {
    drawer.style.transform = 'translateX(100%)';
    if (overlay) overlay.style.display = 'none';
    document.body.style.overflow = '';
  };

  document.querySelectorAll('[data-open-cart]').forEach(btn => btn.addEventListener('click', openCart));
  closeBtn?.addEventListener('click', closeCart);
  overlay?.addEventListener('click', closeCart);
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeCart(); });

  function loadCartDrawer() {
    const content = document.getElementById('cart-drawer-content');
    if (!content) return;
    content.innerHTML = '<div style="display:flex;justify-content:center;align-items:center;height:200px;"><div class="spinner"></div></div>';
    fetch('/cart/drawer/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(r => r.text())
      .then(html => { content.innerHTML = html; })
      .catch(() => { content.innerHTML = '<p style="text-align:center;padding:2rem;color:#A7A3C0;font-size:0.9rem;">Could not load cart.</p>'; });
  }
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   SEARCH OVERLAY
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function initSearchOverlay() {
  const overlay = document.getElementById('search-overlay');
  const input   = document.getElementById('search-input');
  const results = document.getElementById('search-results');
  const closeBtn = document.getElementById('search-close');
  if (!overlay) return;

  const open  = () => { overlay.style.display = 'flex'; setTimeout(() => input?.focus(), 60); };
  const close = () => {
    overlay.style.display = 'none';
    if (input) input.value = '';
    if (results) results.innerHTML = '';
  };

  document.querySelectorAll('[data-open-search]').forEach(btn => btn.addEventListener('click', open));
  closeBtn?.addEventListener('click', close);
  overlay.addEventListener('click', e => { if (e.target === overlay) close(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });

  let debounce;
  input?.addEventListener('input', () => {
    clearTimeout(debounce);
    const q = input.value.trim();
    if (q.length < 2) { results.innerHTML = ''; return; }
    debounce = setTimeout(() => {
      fetch(`/search/ajax/?q=${encodeURIComponent(q)}`)
        .then(r => r.json())
        .then(data => {
          if (!results) return;
          if (!data.results?.length) {
            results.innerHTML = `<div style="padding:2rem;text-align:center;color:#A7A3C0;"><svg width="40" height="40" style="margin:0 auto 1rem;display:block;opacity:0.4;" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path stroke-linecap="round" d="M21 21l-4.35-4.35"/></svg><p style="font-size:0.9rem;margin:0;">No results for "<strong>${q}</strong>"</p></div>`;
            return;
          }
          results.innerHTML = data.results.map(p => `
            <a href="${p.url}" style="display:flex;align-items:center;gap:1rem;padding:0.875rem 1.25rem;text-decoration:none;border-bottom:1px solid #F5F3FC;transition:background 0.15s;"
               onmouseover="this.style.background='#F5F3FC'" onmouseout="this.style.background='#fff'">
              <div style="width:50px;height:64px;border-radius:10px;overflow:hidden;background:#EDE9F8;flex-shrink:0;">
                ${p.image ? `<img src="${p.image}" alt="${p.name}" style="width:100%;height:100%;object-fit:cover;" />` : ''}
              </div>
              <div style="flex:1;min-width:0;">
                <p style="font-size:0.9rem;font-weight:600;color:#1A1A2E;margin:0 0 3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${p.name}</p>
                <p style="font-size:0.875rem;font-weight:700;color:#5B4B8A;margin:0;">$${p.price}</p>
              </div>
              <svg width="16" height="16" fill="none" stroke="#A7A3C0" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
            </a>`).join('');
        })
        .catch(() => {});
    }, 280);
  });
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   NEWSLETTER POPUP
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function initNewsletterPopup() {
  if (sessionStorage.getItem('popup_seen')) return;
  const popup = document.getElementById('newsletter-popup');
  if (!popup) return;

  const show  = () => { popup.style.display = 'flex'; };
  const close = () => { popup.style.display = 'none'; sessionStorage.setItem('popup_seen', '1'); };

  setTimeout(show, 8000);
  popup.querySelectorAll('[data-popup-close]').forEach(btn => btn.addEventListener('click', close));
  popup.addEventListener('click', e => { if (e.target === popup) close(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });

  popup.querySelector('form')?.addEventListener('submit', async e => {
    e.preventDefault();
    const form = popup.querySelector('[data-popup-form]');
    const success = popup.querySelector('[data-popup-success]');
    try {
      const res = await fetch('/newsletter/subscribe/', { method: 'POST', body: new FormData(e.target) });
      const data = await res.json().catch(() => ({ success: true }));
      if (data.success !== false) {
        if (form) form.style.display = 'none';
        if (success) success.style.display = 'block';
        setTimeout(close, 2500);
      }
    } catch { /* fail silently */ }
  });
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   QUICK BUY DRAWER
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function initQuickBuy() {
  const drawer  = document.getElementById('quick-buy-drawer');
  const overlay = document.getElementById('quick-buy-overlay');
  if (!drawer) return;

  const close = () => {
    drawer.style.transform = 'translateX(100%)';
    if (overlay) overlay.style.display = 'none';
    document.body.style.overflow = '';
  };

  drawer.querySelector('[data-qb-close]')?.addEventListener('click', close);
  overlay?.addEventListener('click', close);
  document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });

  document.addEventListener('click', e => {
    const btn = e.target.closest('[data-quick-buy]');
    if (!btn) return;
    const slug    = btn.dataset.productSlug;
    const content = document.getElementById('quick-buy-drawer-content');
    if (!slug || !content) return;

    drawer.style.transform = 'translateX(0)';
    if (overlay) overlay.style.display = 'block';
    document.body.style.overflow = 'hidden';

    content.innerHTML = '<div style="display:flex;justify-content:center;align-items:center;height:200px;"><div class="spinner"></div></div>';
    fetch(`/products/${slug}/`)
      .then(r => r.text())
      .then(html => {
        const doc = new DOMParser().parseFromString(html, 'text/html');
        const qbc = doc.getElementById('quick-buy-content');
        content.innerHTML = qbc ? qbc.innerHTML : '<p style="padding:2rem;color:#A7A3C0;text-align:center;">Unable to load product.</p>';
      })
      .catch(() => {
        content.innerHTML = '<p style="padding:2rem;color:#A7A3C0;text-align:center;">Unable to load product.</p>';
      });
  });
}

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   TOAST NOTIFICATIONS
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
function initToasts() {
  document.querySelectorAll('[data-toast]').forEach(t => {
    setTimeout(() => t.style.opacity = '0', 4000);
    setTimeout(() => t.remove(), 4400);
    t.querySelector('[data-toast-close]')?.addEventListener('click', () => t.remove());
  });
}

window.showToast = (message, type = 'success') => {
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.innerHTML = `<span style="flex:1;">${message}</span>
    <button style="background:none;border:none;color:inherit;font-size:1.25rem;line-height:1;cursor:pointer;margin-left:auto;opacity:0.75;" onclick="this.parentElement.remove()">&times;</button>`;
  document.body.appendChild(el);
  setTimeout(() => el.style.opacity = '0', 4000);
  setTimeout(() => el.remove(), 4400);
};

/* â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
   AJAX ADD TO CART
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ */
document.addEventListener('submit', e => {
  const form = e.target;
  if (!form.action?.includes('/cart/add/')) return;
  e.preventDefault();

  const btn = form.querySelector('[type="submit"]');
  const orig = btn?.innerHTML;
  if (btn) { btn.innerHTML = '<span class="spinner" style="width:1rem;height:1rem;"></span>'; btn.disabled = true; }

  fetch(form.action, {
    method: 'POST',
    body: new FormData(form),
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        const name = data.product_name ? `"${data.product_name}" added to cart!` : 'Added to cart!';
        window.showToast(name, 'success');
        // Update cart badge in header
        const badge = document.getElementById('cart-count-badge');
        if (badge && data.cart_count !== undefined) {
          badge.textContent = data.cart_count;
          badge.style.display = data.cart_count > 0 ? 'flex' : 'none';
        }
      } else {
        window.showToast(data.error || 'Could not add to cart.', 'error');
      }
    })
    .catch(() => form.submit())
    .finally(() => {
      if (btn && orig) { btn.innerHTML = orig; btn.disabled = false; }
    });
});
