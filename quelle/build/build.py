#!/usr/bin/env python3
"""Baut site/ : index.html (mit eingebetteten Rezepten), Manifest, Service Worker, Icons."""
import json, pathlib, subprocess, sys, hashlib

root = pathlib.Path(sys.argv[1])
subprocess.run([sys.executable, str(root / "build" / "parse.py"), str(root)], check=True)
site = root / "site"
(site / "").mkdir(parents=True, exist_ok=True)

recs = json.loads((site / "recipes.json").read_text(encoding="utf-8"))
imgs = json.loads((root / "build" / "images.json").read_text(encoding="utf-8"))
for r in recs:
    r["img"] = imgs.get(r["id"], "")
data = json.dumps(recs, ensure_ascii=False)
html = (root / "src" / "index.template.html").read_text(encoding="utf-8")
assert "/*__DATA__*/[]" in html
html = html.replace("/*__DATA__*/[]", data.replace("</", "<\\/"))
(site / "index.html").write_text(html, encoding="utf-8")
(site / "recipes.json").unlink()  # steckt jetzt in index.html

(site / "manifest.webmanifest").write_text(json.dumps({
    "name": "Kochbuch", "short_name": "Kochbuch", "lang": "de",
    "start_url": "./", "scope": "./", "display": "standalone",
    "background_color": "#f7f3ec", "theme_color": "#d4501e",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ]}, indent=2), encoding="utf-8")

ver = hashlib.md5(html.encode()).hexdigest()[:8]
(site / "sw.js").write_text(f"""const CACHE = 'kochbuch-{ver}';
const FILES = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'apple-touch-icon.png'];
self.addEventListener('install', e => {{ e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); }});
self.addEventListener('activate', e => {{ e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); }});
self.addEventListener('fetch', e => {{
  if (e.request.method !== 'GET' || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(caches.match(e.request, {{ignoreSearch: true}}).then(hit => hit || fetch(e.request)));
}});
""", encoding="utf-8")

# Icons (Pillow)
from PIL import Image, ImageDraw
def icon(size):
    S = size * 4
    im = Image.new("RGB", (S, S), "#d4501e")
    d = ImageDraw.Draw(im)
    # Verlauf
    for y in range(S):
        t = y / S
        c = (int(224 - 30 * t), int(96 - 30 * t), int(40 - 10 * t))
        d.line([(0, y), (S, y)], fill=c)
    cx, cy = S / 2, S * 0.56
    w = S * 0.56
    # Topf
    d.rounded_rectangle([cx - w / 2, cy - S * 0.02, cx + w / 2, cy + S * 0.24], radius=S * 0.07, fill="#fff")
    d.rounded_rectangle([cx - w / 2 - S * 0.07, cy + S * 0.0, cx - w / 2 + S * 0.01, cy + S * 0.06], radius=S * 0.03, fill="#fff")
    d.rounded_rectangle([cx + w / 2 - S * 0.01, cy + S * 0.0, cx + w / 2 + S * 0.07, cy + S * 0.06], radius=S * 0.03, fill="#fff")
    d.rounded_rectangle([cx - w / 2 - S * 0.015, cy - S * 0.06, cx + w / 2 + S * 0.015, cy + S * 0.0], radius=S * 0.025, fill="#fff")
    # Dampf
    for dx in (-0.14, 0, 0.14):
        x = cx + S * dx
        pts = [(x, cy - S * 0.12), (x + S * 0.03, cy - S * 0.19), (x - S * 0.03, cy - S * 0.26), (x, cy - S * 0.33)]
        d.line(pts, fill="#fff", width=int(S * 0.028), joint="curve")
        for p in (pts[0], pts[-1]):
            r = S * 0.014; d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill="#fff")
    return im.resize((size, size), Image.LANCZOS)
for name, s in (("icon-192.png", 192), ("icon-512.png", 512), ("apple-touch-icon.png", 180)):
    icon(s).save(site / "" / name)
print("gebaut:", sorted(str(p.relative_to(site)) for p in site.glob("*") if p.is_file()))
