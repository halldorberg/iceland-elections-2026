// Floating "Ertu frambjóðandi?" button + modal — shared across all pages

const EMAIL = 'halldor.berg@inno.link';

const BUTTON_HTML = `
<button class="outreach-btn" id="outreach-btn" aria-label="Ertu frambjóðandi eða í forsvari fyrir framboð?">
  <span class="outreach-btn-icon">🙋</span>
  <span class="outreach-btn-text">Ertu frambjóðandi?</span>
</button>`;

const MODAL_HTML = `
<div class="outreach-overlay" id="outreach-overlay" role="dialog" aria-modal="true" aria-labelledby="outreach-title">
  <div class="outreach-card" id="outreach-card">
    <button class="outreach-close" id="outreach-close" aria-label="Loka">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
    </button>
    <div class="outreach-icon-header">🙋</div>
    <h2 class="outreach-title" id="outreach-title">Ertu frambjóðandi eða í forsvari fyrir framboð?</h2>
    <p class="outreach-body">
      Það eru yfir 3500 frambjóðendur fyrir þessar kosningar og við viljum leggja metnað í að hafa
      upplýsingar og myndir fyrir sem flest ykkar! Ég er með gervigreind sem reynir að finna sem
      flest um alla framboð og frambjóðendur og skannar helstu síður daglega — en ef það er ekki
      að finna réttar upplýsingar og myndir um þig og þitt framboð, endilega sendu mér línu á
      <a href="mailto:${EMAIL}" class="outreach-email">${EMAIL}</a>
      og ég laga það í hvelli.
    </p>
    <p class="outreach-body">
      Láttu endilega fylgja með hlekk á mynd/myndir og upplýsingar um bakgrunn og stefnumál —
      líka í lagi að bæta við hlekkjum á samfélagsmiðla eða greinar þar sem hægt er að fræðast
      meira um þín mál.
    </p>
    <a href="mailto:${EMAIL}" class="outreach-mailto-btn">
      Senda tölvupóst →
    </a>
  </div>
</div>`;

function init() {
  // Inject HTML
  document.body.insertAdjacentHTML('beforeend', BUTTON_HTML + MODAL_HTML);

  const btn     = document.getElementById('outreach-btn');
  const overlay = document.getElementById('outreach-overlay');
  const closeBtn = document.getElementById('outreach-close');

  function open()  { overlay.classList.add('is-open');  document.body.style.overflow = 'hidden'; }
  function close() { overlay.classList.remove('is-open'); document.body.style.overflow = ''; }

  btn.addEventListener('click', open);
  closeBtn.addEventListener('click', close);
  overlay.addEventListener('click', e => { if (e.target === overlay) close(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });

  // One-shot attention pulse after 1.8 s, then remove the class so it never repeats
  setTimeout(() => {
    btn.classList.add('outreach-btn--pulse');
    btn.addEventListener('animationend', () => btn.classList.remove('outreach-btn--pulse'), { once: true });
  }, 1800);
}

// Run after DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
