#!/usr/bin/env python3
"""badge_spot.py - puts the badge on every theme: one "badgemark" widget per layout (shared/hud.js: the owner's logo PNG for the model
the Badge tab picked, else its name as text), at a spot of the theme that is free. The generators call apply(path) after writing their
layout; `python3 tools/badge_spot.py` does it for every layout (hybrid.json has no generator). It replaces a badge text widget a layout
had (apex, hybrid) and an earlier badgemark, so it can run again and again.

SPOTS: layout -> (x, y, w, h, align, font, colour role, toggle). A toggle of "!mapUp" hides it while the Waze map window covers the spot.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAYOUTS = os.path.join(HERE, '..', 'apps', 'ix3_themes', 'hud', 'layouts')
SPOTS = {
    'alpina':      (800, 330, 320, 80, 'center', 'badge', 'dim', '!mapUp'),
    'apex':        (810, 22, 300, 64, 'center', 'badge', 'dim', None),
    'bluedials':   (830, 592, 200, 58, 'center', 'badge', 'dim', None),
    'classic':     (810, 40, 300, 90, 'center', 'badge', 'dim', None),
    'classic_map': (810, 24, 300, 50, 'center', 'badge', 'dim', None),
    'concept':     (810, 40, 300, 80, 'center', 'badge', 'dim', None),
    'e46':         (936, 438, 98, 60, 'center', 'badge', 'dim', None),
    'eco':         (810, 180, 300, 80, 'center', 'badge', 'dim', '!mapUp'),
    'epower':      (810, 24, 300, 80, 'center', 'badge', 'dim', None),
    'glass':       (810, 30, 300, 80, 'center', 'badge', 'dim', None),
    'hybrid':      (810, 56, 300, 60, 'center', 'badge', 'dim', None),
    'live':        (800, 40, 320, 90, 'center', 'badge', 'dim', None),
    'luxe':        (810, 22, 300, 62, 'center', 'badge', 'accent', None),
    'mdigital':    (810, 24, 300, 34, 'center', 'badge', 'dim', None),
    'neon':        (800, 440, 320, 70, 'center', 'badge', 'dim', '!mapUp'),
    'night':       (810, 40, 300, 80, 'center', 'badge', 'dim', None),
    'rain':        (800, 540, 320, 70, 'center', 'badge', 'dim', '!mapUp'),
}


def apply(path):
    name = os.path.splitext(os.path.basename(path))[0]
    if name not in SPOTS:
        return False
    x, y, w, h, align, font, color, toggle = SPOTS[name]
    L = json.load(open(path, encoding='utf-8'))
    L['widgets'] = [wd for wd in L['widgets'] if wd.get('type') != 'badgemark' and not (wd['id'] == 'badge' and wd.get('type') == 'text')]
    d = {'id': 'badgemark', 'type': 'badgemark', 'z': 5, 'x': x, 'y': y, 'w': w, 'h': h, 'font': font, 'color': color, 'align': align}
    if toggle:
        d['toggle'] = toggle
    # before the bottom row (its strip_* widgets stay last)
    i = next((k for k, wd in enumerate(L['widgets']) if str(wd['id']).startswith('strip_')), len(L['widgets']))
    L['widgets'].insert(i, d)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(L, f, indent=2, ensure_ascii=False)
        f.write('\n')
    return True


if __name__ == '__main__':
    for n in sorted(SPOTS):
        p = os.path.join(LAYOUTS, n + '.json')
        if os.path.exists(p):
            print(n, apply(p))
