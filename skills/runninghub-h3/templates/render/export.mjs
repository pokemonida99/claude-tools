// Usage:
//   node export.mjs video [fps=30] [start=0] [end=147.72] [out=../ghost-step-mv.mp4]
//   node export.mjs stills t1 t2 ...        -> ../stills/t_<t>.png (4x contact sheet ready)
//   PAGE='pixel_l2d.html?v' → 9:16 page;  SEGS='0-18.5,29-47.8' → edit: only these song ranges, joined (short versions)
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import puppeteer from 'puppeteer-core';

const ROOT = path.dirname(new URL(import.meta.url).pathname);
const TYPES = { '.html': 'text/html', '.png': 'image/png', '.jpg': 'image/jpeg', '.json': 'application/json', '.mp3': 'audio/mpeg', '.woff2': 'font/woff2', '.js': 'text/javascript', '.mp4': 'video/mp4' };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0);
const port = server.address().port;

const browser = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true, args: ['--autoplay-policy=no-user-gesture-required'] });
const page = await browser.newPage();
const PAGE = process.env.PAGE || 'index.html';
const HI = !/^(index|pixel)/.test(PAGE);
const SEGS = process.env.SEGS ? process.env.SEGS.split(',').map(r => r.split('-').map(Number)) : null;
await page.goto(`http://localhost:${port}/${PAGE}`);
await page.evaluate(() => window.ready);
const [CW, CH] = await page.evaluate(() => [document.getElementById('c').width, document.getElementById('c').height]);
const VF = HI ? [] : ['-vf', CW > CH ? 'scale=1920:1080:flags=neighbor' : 'scale=iw*3:ih*3:flags=neighbor,scale=1080:1920:flags=area'];
const frame = (t, fmt = 'image/png') => page.evaluate(async (t, fmt) => { if (window.prep) await window.prep(t); window.render(t); return document.getElementById('c').toDataURL(fmt, 0.93).split(',')[1]; }, t, fmt);

const [mode, ...args] = process.argv.slice(2);
if (mode === 'stills') {
  const dir = path.join(ROOT, '..', 'stills'); fs.mkdirSync(dir, { recursive: true });
  for (const t of args) fs.writeFileSync(path.join(dir, `t_${t}.${HI ? 'jpg' : 'png'}`), Buffer.from(await frame(+t, HI ? 'image/jpeg' : 'image/png'), 'base64'));
} else {
  const fps = +(args[0] || 30), t0 = +(args[1] || 0), t1 = +(args[2] || 147.72);
  const out = path.resolve(ROOT, args[3] || '../ghost-step-mv.mp4');
  const segs = SEGS || [[t0, t1]];
  const counts = segs.map(([a, b]) => Math.round((b - a) * fps));
  // audio: cut the same ranges from the song and butt-join them (tiny fades hide the seams)
  const FADE = +(process.env.FADE || 0.03);
  const af = segs.map(([a, b], k) => `[1:a]atrim=${a}:${b},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st=${(counts[k] / fps - (k === segs.length - 1 ? FADE : 0.03)).toFixed(3)}:d=${k === segs.length - 1 ? FADE : 0.03}[a${k}]`).join(';')
    + ';' + segs.map((_, k) => `[a${k}]`).join('') + `concat=n=${segs.length}:v=0:a=1[aout]`;
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-i', path.join(ROOT, 'song.mp3'), '-filter_complex', af, '-map', '0:v', '-map', '[aout]',
    ...VF, '-c:v', 'libx264', '-preset', 'medium', '-crf', process.env.CRF || '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '256k', '-shortest', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const times = segs.flatMap(([a], k) => Array.from({ length: counts[k] }, (_, i) => a + i / fps));
  const n = times.length;
  for (let i = 0; i < n; i++) {
    const buf = Buffer.from(await frame(times[i], HI ? 'image/jpeg' : 'image/png'), 'base64');
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 300 === 0) console.log(`frame ${i}/${n}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  console.log('wrote', out);
}
await browser.close();
server.close();
