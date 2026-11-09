(function () {
  'use strict';
  if (navigator.doNotTrack === '1' || navigator.globalPrivacyControl || !window.crypto || !crypto.getRandomValues) return;
  var endpoint = '/api/traffic/event/';
  var current = null;
  var queue = Promise.resolve();
  var lastInteraction = performance.now();
  var lastLocation = '';
  var stopped = false;

  function uuid() {
    var bytes = new Uint8Array(16);
    crypto.getRandomValues(bytes);
    bytes[6] = (bytes[6] & 15) | 64;
    bytes[8] = (bytes[8] & 63) | 128;
    var hex = Array.prototype.map.call(bytes, function (v) { return v.toString(16).padStart(2, '0'); }).join('');
    return hex.slice(0, 8) + '-' + hex.slice(8, 12) + '-' + hex.slice(12, 16) + '-' + hex.slice(16, 20) + '-' + hex.slice(20);
  }
  function tick(page) {
    var now = performance.now();
    if (page && page.active) page.seconds += Math.max(0, Math.min(now - page.tick, 15000, lastInteraction + 60000 - page.tick)) / 1000;
    if (page) { page.tick = now; page.active = !document.hidden && document.hasFocus() && now - lastInteraction < 60000; }
  }
  function heartbeat(page) {
    if (!page || !page.token || stopped) return;
    var body = JSON.stringify({ event: 'heartbeat', token: page.token, active_seconds: Math.floor(page.seconds) });
    if (navigator.sendBeacon && navigator.sendBeacon(endpoint, new Blob([body], { type: 'application/json' }))) return;
    fetch(endpoint, { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' }, body: body, keepalive: true }).catch(function () {});
  }
  function pageview(force) {
    if (stopped) return;
    var locationKey = location.pathname + location.search;
    if (!force && locationKey === lastLocation) return;
    lastLocation = locationKey;
    tick(current);
    heartbeat(current);
    if (current) current.ended = true;
    if (/^\/(admin|api|static|media|r)(\/|$)/.test(location.pathname)) { current = null; return; }
    var page = { seconds: 0, token: '', tick: performance.now(), active: !document.hidden && document.hasFocus(), ended: false };
    current = page;
    var data = { event: 'page', page_id: uuid(), path: location.pathname, referrer: document.referrer };
    var query = new URLSearchParams(location.search);
    ['cl', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'].forEach(function (key) { data[key] = (query.get(key) || '').slice(0, 120); });
    queue = queue.then(function () {
      return fetch(endpoint, { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data), keepalive: true })
        .then(function (response) {
          if (response.status === 204) { stopped = true; return null; }
          return response.ok ? response.json() : null;
        }).then(function (result) { if (result) { page.token = result.token; if (page.ended) heartbeat(page); } });
    }).catch(function () {});
  }
  ['pointerdown', 'keydown', 'scroll', 'touchstart'].forEach(function (event) {
    window.addEventListener(event, function () {
      if (performance.now() - lastInteraction > 30 * 60000) pageview(true);
      tick(current); lastInteraction = performance.now();
      if (current) current.active = !document.hidden && document.hasFocus();
    }, { passive: true });
  });
  ['focus', 'blur'].forEach(function (event) { window.addEventListener(event, function () { tick(current); heartbeat(current); }); });
  document.addEventListener('visibilitychange', function () { tick(current); heartbeat(current); });
  window.addEventListener('pagehide', function () { tick(current); if (current) current.ended = true; heartbeat(current); });
  window.addEventListener('pageshow', function (event) { if (event.persisted) pageview(true); });
  ['pushState', 'replaceState'].forEach(function (method) {
    var original = history[method];
    history[method] = function () { var result = original.apply(this, arguments); pageview(false); return result; };
  });
  window.addEventListener('popstate', function () { pageview(false); });
  setInterval(function () { tick(current); heartbeat(current); }, 15000);
  pageview(false);
}());
