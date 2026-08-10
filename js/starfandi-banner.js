/* starfandi.is advertisement banner — self-contained, fixed at page bottom.
   Lottie robot animation loads lazily and replays occasionally. */
(function () {
  var css = `
    .starfandi-wrap {
      position: fixed;
      bottom: 0; left: 0; right: 0;
      z-index: 950;
      display: flex;
      justify-content: center;
      padding: 28px 12px 12px;
      background: linear-gradient(to top, rgba(245,249,255,0.96) 0%, rgba(245,249,255,0.75) 55%, rgba(245,249,255,0) 100%);
      pointer-events: none;
    }
    body.sb-dark .starfandi-wrap { background: none; }
    .starfandi-banner {
      pointer-events: auto;
      position: relative;
      display: flex;
      align-items: center;
      gap: 20px;
      width: calc(80% - 32px);
      max-width: 928px;
      padding: 10px 22px 10px 14px;
      background: linear-gradient(105deg, #ffffff 0%, #f2f6ff 55%, #e8efff 100%);
      border: 1px solid rgba(26,86,219,0.18);
      border-radius: 16px;
      box-shadow: 0 4px 18px rgba(0,0,0,0.16);
      text-decoration: none;
      text-align: left;
      font-family: 'Inter', sans-serif;
      transition: transform 0.15s, box-shadow 0.15s;
      overflow: hidden;
    }
    .starfandi-banner:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(0,0,0,0.22); }
    .starfandi-banner::after {
      content: '';
      position: absolute;
      right: -60px; top: -60px;
      width: 180px; height: 180px;
      background: radial-gradient(circle, rgba(26,86,219,0.10) 0%, transparent 70%);
      pointer-events: none;
    }
    .starfandi-banner .sb-anim { width: 100px; aspect-ratio: 773/359; flex-shrink: 0; }
    .starfandi-banner .sb-text { min-width: 0; flex: 1; }
    .starfandi-banner .sb-label {
      font-size: 0.58rem; font-weight: 600; letter-spacing: 0.12em;
      text-transform: uppercase; color: #94a3b8; margin-bottom: 2px;
    }
    .starfandi-banner .sb-title { font-weight: 700; font-size: 0.98rem; color: #0f1923; line-height: 1.3; }
    .starfandi-banner .sb-title span { color: #1a56db; }
    .starfandi-banner .sb-sub { font-size: 0.8rem; color: #4a5568; line-height: 1.4; margin-top: 2px; }
    .starfandi-banner .sb-cta {
      flex-shrink: 0;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 10px 22px;
      background: #1a56db;
      color: #fff;
      border-radius: 999px;
      font-size: 0.84rem;
      font-weight: 700;
      white-space: nowrap;
      box-shadow: 0 2px 10px rgba(26,86,219,0.35);
      transition: background 0.15s;
    }
    .starfandi-banner:hover .sb-cta { background: #1543ab; }
    @media (max-width: 800px) {
      .starfandi-banner { width: 100%; gap: 12px; padding: 8px 14px 8px 10px; }
      .starfandi-banner .sb-anim { width: 76px; }
      .starfandi-banner .sb-title { font-size: 0.84rem; }
      .starfandi-banner .sb-sub { display: none; }
      .starfandi-banner .sb-cta { padding: 8px 14px; font-size: 0.76rem; }
    }
    @media (max-width: 560px) { .starfandi-banner .sb-cta { display: none; } }
    /* Leave a slot at the far left for the site's info (ℹ) badge */
    @media (max-width: 1150px) { .starfandi-wrap { padding-left: 54px; } }
  `;
  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  // Dark-theme pages (archive/municipality) have light text — skip the white gradient there
  var bodyColor = getComputedStyle(document.body).color.match(/\d+/g) || [0, 0, 0];
  var lum = 0.299 * bodyColor[0] + 0.587 * bodyColor[1] + 0.114 * bodyColor[2];
  if (lum > 128) document.body.classList.add('sb-dark');

  var wrap = document.createElement('div');
  wrap.className = 'starfandi-wrap';
  var a = document.createElement('a');
  a.className = 'starfandi-banner';
  a.href = 'https://starfandi.is';
  a.target = '_blank';
  a.rel = 'noopener noreferrer';
  a.innerHTML =
    '<div class="sb-anim"></div>' +
    '<div class="sb-text">' +
      '<div class="sb-label">Auglýsing</div>' +
      '<div class="sb-title"><span>starfandi.is</span> — Ég get hjálpað þér að finna vinnu á Íslandi</div>' +
      '<div class="sb-sub">Gervigreindin vaktar atvinnuleitarsíður á Íslandi og finnur stöður sem smellpassa fyrir þig.</div>' +
    '</div>' +
    '<div class="sb-cta">Prófa frítt →</div>';
  wrap.appendChild(a);
  document.body.appendChild(wrap);

  // Reserve space so the bottom-most content can scroll clear of the banner
  function reserve() {
    document.body.style.paddingBottom = (wrap.offsetHeight + 8) + 'px';
  }
  reserve();
  window.addEventListener('resize', reserve);

  var loaded = false;
  function loadLottie() {
    if (loaded) return;
    loaded = true;
    var s = document.createElement('script');
    s.src = 'https://unpkg.com/lottie-web@5.12.2/build/player/lottie_light.min.js';
    s.onload = function () {
      var anim = window.lottie.loadAnimation({
        container: a.querySelector('.sb-anim'),
        renderer: 'svg',
        loop: false,
        autoplay: true,
        path: '/images/starfandi-robot.json',
      });
      // Replay occasionally to draw attention
      setInterval(function () { anim.goToAndPlay(0, true); }, 14000);
    };
    document.head.appendChild(s);
  }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries, obs) {
      if (entries[0].isIntersecting) { loadLottie(); obs.disconnect(); }
    }, { rootMargin: '200px' }).observe(a);
  } else {
    loadLottie();
  }
})();
