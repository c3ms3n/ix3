#!/usr/bin/env python3
"""previews_cluster.py - the theme pictures the app's Themes tab shows (shared/page.js, shared/previews.js).

Every theme is shot on the bench with fixed demo values (Chromium through tools/preview/shot.js) and shipped inside the app as
apps/ix3_themes/hud/previews/<layout>.json = { big, small: {w, h, z} } (z = base64 of the zlib-deflated RGBA rows).

    node bench/server.js ix3_themes            # in one terminal (BENCH_PORT=8078 by default)
    python3 tools/previews_cluster.py ix3_themes 8078

The bench's settings are put back afterwards. Needs Pillow and Chromium.
"""
import base64, json, os, subprocess, sys, time, urllib.request, zlib
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT = os.path.join(ROOT, 'tools', 'preview', 'shot.js')
SKIP = {'off', 'grid', 'mapcal', 'wincal'}
SIGNALS = {'rpm': 4200, 'speed': 98, 'gear': 3, 'oil': 95, 'coolant': 90, 'boost': 1.1, 'torque': 290, 'fuelL': 38, 'range': 310,
           'ambient': 18, 'tyreP': 2.4, 'tyreT': 30, 'gLat': 0.1, 'gLong': 0.05, 'hvSoc': 64}
CROP = (30, 107, 1540, 107 + 566)        # the cluster inside the bench page's 1920x1100 viewport
BIG, SMALL = (888, 333), (280, 105)


def post(port, path, body):
    req = urllib.request.Request('http://127.0.0.1:%d%s' % (port, path), data=json.dumps(body).encode(),
                                 headers={'Content-Type': 'application/json'}, method='POST')
    urllib.request.urlopen(req, timeout=5).read()


def shoot(port, out):
    for attempt in range(3):
        if os.path.exists(out):
            os.remove(out)
        try:
            subprocess.run(['node', SHOT, 'http://localhost:%d' % port, out, '9000'], check=True, timeout=120,
                           env=dict(os.environ, CLEAN='1'), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            im = Image.open(out).convert('RGB').crop(CROP)
            if sum(im.convert('L').point(lambda v: 255 if v > 40 else 0).histogram()[255:]) >= 400:
                return im
            print('  (blank, try %d of 3)' % (attempt + 1), flush=True)
        except Exception as e:
            print('  (%s, try %d of 3)' % (type(e).__name__, attempt + 1), flush=True)
    raise SystemExit('no good picture in three tries: ' + out)


def pack(img, size):
    im = img.resize(size, Image.LANCZOS).convert('RGBA')
    return {'w': size[0], 'h': size[1], 'z': base64.b64encode(zlib.compress(im.tobytes(), 9)).decode()}


def main():
    app, port = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 8078
    spec = json.load(open(os.path.join(ROOT, 'apps', app, 'app.json')))
    layouts = [o[0] for o in next(s for s in spec['settings'] if s['key'] == 'hudLayout')['options'] if o[0] not in SKIP]
    only = sys.argv[3:] or layouts
    defaults = {s['key']: s.get('default') for s in spec['settings']}
    raw = os.path.join(ROOT, 'tools', 'preview', 'shots')
    os.makedirs(raw, exist_ok=True)
    dst = os.path.join(ROOT, 'apps', app, 'hud', 'previews')
    os.makedirs(dst, exist_ok=True)
    for k, v in (('byMode', False), ('nightDim', 'off'), ('units', 'metric'), ('mapInTheme', False)):
        post(port, '/setting', {'key': k, 'value': v})
    post(port, '/drive', {'value': 4})
    post(port, '/signals', {'mode': 'manual', 'values': SIGNALS})
    try:
        for name in only:
            post(port, '/setting', {'key': 'hudLayout', 'value': name})
            time.sleep(9)
            img = shoot(port, os.path.join(raw, name + '.png'))
            v = {'big': pack(img, BIG), 'small': pack(img, SMALL)}
            with open(os.path.join(dst, name + '.json'), 'w') as f:
                json.dump(v, f, separators=(',', ':'))
            print('  %s: big %d KB, small %d KB' % (name, len(v['big']['z']) // 1024, len(v['small']['z']) // 1024), flush=True)
    finally:
        for k in ('hudLayout', 'byMode', 'nightDim', 'units', 'mapInTheme'):
            if k in defaults:
                post(port, '/setting', {'key': k, 'value': defaults[k]})
        post(port, '/signals', {'mode': 'demo', 'values': {}})
    # pictures of themes that are gone
    keep = set(layouts)
    for n in os.listdir(dst):
        if n.endswith('.json') and n[:-5] not in keep:
            os.remove(os.path.join(dst, n)); print('  removed the old picture', n)
    print('previews ->', os.path.relpath(dst, ROOT))


if __name__ == '__main__':
    main()
