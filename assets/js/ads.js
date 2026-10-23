/**
 * MyPhatshala: AdSense loader
 * Any element <div class="ad-slot" data-slot="top"></div> becomes an ad.
 * - adsenseClient set  → loads Google's script and fills the slots
 * - not set, on your PC (file:// or localhost) → shows a grey placeholder
 * - not set, on the live site → slot stays hidden (no empty boxes)
 */
(function () {
  const cfg = window.MP_CONFIG || {};
  const slots = document.querySelectorAll(".ad-slot");
  const isLocal = location.protocol === "file:" || /^(localhost|127\.|192\.168\.)/.test(location.hostname);

  if (!cfg.adsenseClient) {
    slots.forEach(el => {
      if (isLocal) {
        el.classList.add("ad-slot--placeholder");
        el.innerHTML = `<span>Advertisement · AdSense “${el.dataset.slot}” slot</span>`;
      } else {
        el.hidden = true;
      }
    });
    return;
  }

  const already = document.querySelector('script[src*="pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"]');
  if (!already) {
  const s = document.createElement("script");
  s.async = true;
  s.crossOrigin = "anonymous";
  s.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + encodeURIComponent(cfg.adsenseClient);
  document.head.appendChild(s);
  }

  slots.forEach(el => {
    const slotId = (cfg.adSlots || {})[el.dataset.slot];
    if (!slotId) { el.hidden = true; return; }
    el.innerHTML =
      `<span class="ad-label">Advertisement</span>` +
      `<ins class="adsbygoogle" style="display:block" data-ad-client="${cfg.adsenseClient}" ` +
      `data-ad-slot="${slotId}" data-ad-format="auto" data-full-width-responsive="true"></ins>`;
    (window.adsbygoogle = window.adsbygoogle || []).push({});
  });
})();
