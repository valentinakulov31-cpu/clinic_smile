const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const crypto = require('node:crypto');
const source = fs.readFileSync(__dirname + '/static/traffic/tracker-v1.js', 'utf8');

function setup(options = {}) {
  const listeners = {};
  const calls = [];
  const beacons = [];
  let now = 0;
  let interval;
  const location = { pathname: '/', search: '?utm_source=banner&cl=banner1&phone=private' };
  const document = { hidden: false, referrer: 'https://example.com/', hasFocus: () => !document.hidden,
    addEventListener: (name, callback) => { listeners[name] = callback; } };
  const context = { document, location, performance: { now: () => now }, Uint8Array, URLSearchParams, Blob, Promise,
    crypto: crypto.webcrypto, navigator: { ...options.navigator, sendBeacon: (url, body) => { beacons.push(body); return true; } },
    setInterval: (callback) => { interval = callback; },
    fetch: async (url, settings) => { calls.push(JSON.parse(settings.body)); if (options.fail) throw new Error('offline');
      return { ok: true, status: options.status || 200, json: async () => ({ token: 'signed-token' }) }; },
    history: { pushState: (_, __, path) => { location.pathname = path; location.search = ''; }, replaceState: () => {} },
    addEventListener: (name, callback) => { listeners[name] = callback; }
  };
  context.window = context;
  vm.runInNewContext(source, context);
  return { context, calls, beacons, listeners, advance: (ms) => { now += ms; if (interval) interval(); } };
}
const settle = () => new Promise(resolve => setImmediate(resolve));

test('captures only UTM, starts once, and tracks SPA navigation', async () => {
  const state = setup(); await settle();
  assert.equal(state.calls.length, 1);
  assert.equal(state.calls[0].utm_source, 'banner');
  assert.equal(state.calls[0].phone, undefined);
  state.context.history.replaceState({}, '', '/'); await settle();
  assert.equal(state.calls.length, 1);
  state.context.history.pushState({}, '', '/contacts'); await settle();
  assert.equal(state.calls.length, 2);
  assert.notEqual(state.calls[0].page_id, state.calls[1].page_id);
});
test('active time is cumulative, excludes hidden time and caps idle at 60s', async () => {
  const state = setup(); await settle();
  state.advance(15000);
  assert.equal(JSON.parse(await state.beacons.at(-1).text()).active_seconds, 15);
  state.context.document.hidden = true; state.listeners.visibilitychange();
  state.advance(15000);
  assert.equal(JSON.parse(await state.beacons.at(-1).text()).active_seconds, 15);
  state.context.document.hidden = false; state.listeners.visibilitychange();
  state.advance(15000); state.advance(15000); state.advance(15000); state.advance(15000);
  assert.equal(JSON.parse(await state.beacons.at(-1).text()).active_seconds, 45);
});
test('DNT and GPC disable all tracking', async () => {
  for (const navigator of [{ doNotTrack: '1' }, { globalPrivacyControl: true }]) {
    const state = setup({ navigator }); await settle(); assert.equal(state.calls.length, 0);
  }
});
test('server exclusion stops later page events', async () => {
  const state = setup({ status: 204 }); await settle();
  state.context.history.pushState({}, '', '/contacts'); await settle();
  assert.equal(state.calls.length, 1); assert.equal(state.beacons.length, 0);
});
test('network errors do not stop navigation', async () => {
  const state = setup({ fail: true }); await settle();
  state.context.history.pushState({}, '', '/contacts'); await settle();
  assert.equal(state.context.location.pathname, '/contacts'); assert.equal(state.calls.length, 2);
});
test('a new interaction after 30 idle minutes starts a new page session', async () => {
  const state = setup(); await settle();
  state.advance(31 * 60000); state.listeners.pointerdown(); await settle();
  assert.equal(state.calls.length, 2);
});
