// Screen-records vicereplay.com's interactive map at phone size (1080x1920) for "interactive map tutorial" Shorts
// (owner Nov 26, Phase 3 #5/#16: interactive map demonstrations). Our own site, served from the local checkout, so no
// network and no third-party footage; the map tiles are Rockstar's official map (allowed, credited on the page).
//   node tools/record_map_demo.js <site dir> <page path> <search text> <pin anchor> <out.mp4>
//   node tools/record_map_demo.js ../vicereplay-site guides/gta-6-map-leonida-places/ shoe flip-flop-house-shoe-store media/site/map-demo-shoe-en.mp4
//   node tools/record_map_demo.js ../vicereplay-site <page path> --script steps.json <out.mp4>    (Phase 4: any demo)
//   steps.json: [{"wait": ms} | {"click": "css"} | {"type": ["css", "text"]} | {"pin": "anchor"} | {"eval": "js"}]
//   (waits are in video time; the page runs in slow motion while recording)
//
// How: Chrome's recorders capture CSS pixels (432x768 here), so the page runs in slow motion instead (its clock,
// timers, animation frames and CSS transitions at RATE) while full-resolution screenshots (1080x1920) are taken as
// fast as possible; each frame is then placed at its slow-motion time x RATE, giving ~20+ fps at real speed.
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs'), path = require('path'), os = require('os');
const RATE = 0.25;

const CLOCK = `(() => {
  const pn = performance.now.bind(performance), raf = window.requestAnimationFrame.bind(window);
  const st = window.setTimeout.bind(window), si = window.setInterval.bind(window), dn = Date.now;
  const c = { rate: 1, real: pn(), virt: pn() }, d0 = dn() - pn();
  const virt = () => c.virt + (pn() - c.real) * c.rate;
  window.__setRate = r => { const v = virt(); c.real = pn(); c.virt = v; c.rate = r; };
  performance.now = virt;
  Date.now = () => Math.round(d0 + virt());
  window.requestAnimationFrame = cb => raf(() => cb(virt()));
  window.setTimeout = (f, ms, ...a) => st(f, (ms || 0) / c.rate, ...a);
  window.setInterval = (f, ms, ...a) => si(f, (ms || 0) / c.rate, ...a);
})();`;

(async () => {
  const argv = process.argv.slice(2);
  const scripted = argv[2] === '--script';
  const [site, page] = argv;
  const steps = scripted ? JSON.parse(fs.readFileSync(argv[3], 'utf8')) : null;
  const out = scripted ? argv[4] : argv[4];
  const [query, pin] = scripted ? [null, null] : [argv[2], argv[3]];
  const port = 8700 + Math.floor(Math.random() * 90);
  const srv = spawn('python3', ['-m', 'http.server', String(port), '--bind', '127.0.0.1'], { cwd: site, stdio: 'ignore' });
  await new Promise(r => setTimeout(r, 900));
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'rec-'));
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 432, height: 768 }, deviceScaleFactor: 2.5 });
  await ctx.addInitScript(CLOCK);
  const p = await ctx.newPage();
  const cdp = await ctx.newCDPSession(p);
  const frames = [];
  let rec = false, t0 = 0;
  const shoot = async () => {
    while (rec) {
      const t = Date.now();
      let buf;
      try { buf = await p.screenshot({ type: 'jpeg', quality: 92 }); } catch (e) { break; }  // browser closing
      frames.push({ t: (t - t0) / 1000 * RATE, buf });
    }
  };
  const slow = ms => p.waitForTimeout(ms / RATE);  // wait `ms` of video time
  try {
    await p.goto(`http://127.0.0.1:${port}/${page}`, { waitUntil: 'networkidle' });
    await p.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
    await p.reload({ waitUntil: 'networkidle' });
    await p.waitForSelector('.leaflet-marker-icon');
    await p.evaluate(() => document.getElementById('vrmap').scrollIntoView({ block: 'center' }));
    if (await p.isVisible('.vrtoggle')) await p.click('.vrtoggle');
    await p.click('[data-full]');
    await p.waitForTimeout(1200);                      // tiles settle in full screen (real time)
    await p.evaluate(r => window.__setRate(r), RATE);
    await cdp.send('Animation.enable');
    await cdp.send('Animation.setPlaybackRate', { playbackRate: RATE });
    rec = true; t0 = Date.now();
    const loop = shoot();
    const clickPin = async a => {
      const ok = await p.evaluate(x => { const e = document.querySelector(`[data-pin][href="#${x}"]`); if (e) e.click(); return !!e; }, a);
      if (!ok) throw new Error(`no pin link for #${a}`);
    };
    if (steps) {
      for (const st of steps) {
        if (st.wait) await slow(st.wait);
        else if (st.click) {  // clicked inside the page: slow-motion animations never look "stable" to Playwright
          const ok = await p.evaluate(sel => { const e = document.querySelector(sel); if (e) e.click(); return !!e; }, st.click);
          if (!ok) throw new Error(`step click: nothing matches ${st.click}`);
        }
        else if (st.type) { await p.click(st.type[0]); for (const ch of st.type[1]) { await p.keyboard.type(ch); await slow(150); } }
        else if (st.pin) await clickPin(st.pin);
        else if (st.eval) await p.evaluate(st.eval);
      }
    } else {
      await slow(1300);                                // the whole state, every pin
      await p.click('.vrsearch');
      for (const ch of query) { await p.keyboard.type(ch); await slow(150); }  // the search filters pins as you type
      await slow(900);
      await clickPin(pin);
      await slow(3000);                                // fly to the pin + its popup
    }
    rec = false;
    await loop;
    if (frames.length < 20) throw new Error(`only ${frames.length} frames captured`);
    let list = '';
    frames.forEach((f, i) => {
      const name = path.join(dir, `f${String(i).padStart(5, '0')}.jpg`);
      fs.writeFileSync(name, f.buf);
      const next = i + 1 < frames.length ? frames[i + 1].t : f.t + 0.2;
      list += `file '${name}'\nduration ${Math.max(0.001, next - f.t).toFixed(4)}\n`;
    });
    list += `file '${path.join(dir, `f${String(frames.length - 1).padStart(5, '0')}.jpg`)}'\n`;
    fs.writeFileSync(path.join(dir, 'list.txt'), list);
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', path.join(dir, 'list.txt'),
      '-vf', 'scale=1080:1920,fps=30,format=yuv420p', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-an', out]);
    const dur = frames[frames.length - 1].t + 0.2;
    console.log(`recorded ${out}: ${frames.length} frames (${(frames.length / dur).toFixed(1)} fps), ${dur.toFixed(1)} s`);
  } finally {
    rec = false;
    await b.close(); srv.kill();
    fs.rmSync(dir, { recursive: true, force: true });
  }
})().catch(e => { console.error(e.message); process.exit(1); });
