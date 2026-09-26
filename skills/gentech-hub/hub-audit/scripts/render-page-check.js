#!/usr/bin/env node
/* render-page-check.js - run a hub page's OWN <script> under a DOM shim and print what a
 * reader would actually see.
 *
 * WHY: tag balance proves the document PARSES; it does not prove the page RENDERS. The only
 * proof that a JS-rendered dashboard produces the right values is to execute its own script
 * (sliced byte-for-byte out of the SERVED html, not a re-implementation) against a real payload.
 *
 * usage: node render-page-check.js <dir> <page.html> <id,id,id>
 *   <dir> must contain page.html plus every JSON file the page fetches, same filenames.
 *   Query strings are stripped, so cache-busted fetches resolve to the local file.
 *
 * Print JSON: {page, threw, fields:{id:text}}. '<unset>' means the node was absent or the
 * page never wrote to it - which is itself the assertion for "this tile was removed".
 *
 * Assumes the page's script defines a global load() to start rendering; if the page has a
 * different entry point, call it in the `return (...)` line and pass an empty ids list first
 * to confirm it runs at all.
 *
 * To prove a DEGRADED path: copy the dir, overwrite the payload with the failure shape
 * (e.g. {"status":"unknown"}), and run again. Good output on the healthy payload and
 * UNKNOWN-with-reason on the broken one is the proof; one run alone is not.
 */
const fs = require('fs');
const dir = process.argv[2], page = process.argv[3];
const ids = (process.argv[4] || '').split(',').map(s => s.trim()).filter(Boolean);

const html = fs.readFileSync(dir + '/' + page, 'utf8');
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error('no <script> in ' + page); process.exit(2); }

const els = {};
const mk = id => (els[id] = {
  id, textContent: '', innerHTML: '', className: '', style: {},
  classList: { add() {}, remove() {}, toggle() {} },
  setAttribute() {}, appendChild() {}, removeChild() {},
  querySelectorAll: () => [], querySelector: () => null,
});
const documentShim = {
  getElementById: id => els[id] || mk(id),
  querySelector: () => null, querySelectorAll: () => [],
  createElement: () => mk('_' + Math.random()),
  createElementNS: () => mk('_' + Math.random()),
  addEventListener() {},
};
const fetchShim = async u => {
  const f = String(u).split('?')[0].replace(/^.*\//, '');
  return {
    ok: true, status: 200,
    json: async () => JSON.parse(fs.readFileSync(dir + '/' + f, 'utf8')),
    text: async () => fs.readFileSync(dir + '/' + f, 'utf8'),
  };
};

// a repeating timer would keep the process alive forever
let code = m[1].replace(/setInterval\([^)]*\)\s*;?/g, '');
const fn = new Function('document', 'fetch', 'setInterval', 'window',
  code + '\n;return (typeof load === "function") ? load() : null;');

(async () => {
  let threw = null;
  try { await fn(documentShim, fetchShim, () => 0, globalThis); }
  catch (e) { threw = String(e && e.message); }
  await new Promise(r => setTimeout(r, 2000));   // let the fetch chain settle
  const out = { page, threw, fields: {} };
  for (const i of ids) out.fields[i] = (els[i] && els[i].textContent) || '<unset>';
  console.log(JSON.stringify(out, null, 1));
})().then(() => process.exit(0));
