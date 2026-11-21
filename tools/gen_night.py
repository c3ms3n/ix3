#!/usr/bin/env python3
"""Generates apps/ix3_themes/hud/layouts/night.json (the Night Drive theme): a very dark, quiet cluster for night driving.
Two slim dials (speed left, revs right) with a thin bronze bezel, hairline ticks, a few warm-white numbers and a dim amber
needle with a soft glow; the speed digitally inside the left dial, the gear and drive mode inside the right one, and a large
slim clock in the middle with the range and outside temperature under it. While the Waze map shows inside the theme a window
opens in the middle (the clock gives way). Edit this and regenerate; do not hand-edit the JSON."""
import json, math, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'layouts', 'night.json')
FONT_DIR = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'fonts')
R = 238.0
LC, RC = (330.0, 325.0), (1590.0, 325.0)
TICK = [150, 122, 92]
NEEDLE = [236, 148, 52]
RED = [200, 70, 44]
BEZEL = [150, 112, 70]


def cell(font):
    return json.load(open(os.path.join(FONT_DIR, font + '.json')))['cellHeight']


def pos(center, radius, deg):
    a = math.radians(deg)
    return (center[0] + radius * math.sin(a), center[1] - radius * math.cos(a))


def text(i, c, w, font, t, color='fg', align='center', **kw):
    h = cell(font)
    x0 = c[0] - w / 2 if align == 'center' else (c[0] - w if align == 'right' else c[0])
    d = {'id': i, 'type': 'text', 'z': 5, 'x': round(x0), 'y': round(c[1] - h / 2), 'w': w, 'h': h, 'text': t, 'font': font,
         'color': color, 'align': align}
    d.update(kw)
    return d


def dial(i, center, start, sweep, signal, mn, mx, majors, minors, red=None):
    s = int(2 * (R + 4))
    return {'id': i, 'type': 'adial', 'class': 'content', 'z': 2, 'x': round(center[0] - s / 2), 'y': round(center[1] - s / 2), 'w': s, 'h': s,
            'signal': signal, 'min': mn, 'max': mx, 'radius': R, 'hub': 14, 'start': start, 'sweep': sweep,
            'majors': majors, 'minors': minors, 'tickLen': [16, 8], 'needle': [0.9, 26, 6, 9], 'redFrom': red,
            'tickColor': TICK, 'needleColor': NEEDLE, 'redColor': RED, 'faceColor': [7, 6, 8], 'faceEdge': [2, 2, 3],
            'ring': [0.7, 0.9, 6], 'bezelColor': BEZEL}


W = [{'id': 'bg', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg',
      'hole': [640, 70, 640, 480], 'holeWhen': 'mapUp', 'holeInset': 0, 'holeRadius': 34}]
hide = {'toggle': '!mapUp'}
SS, SW = 232.0, 265.0          # the speed scale's start / sweep (degrees)
RS, RW = 231.0, 245.0
W.append(dial('spd', LC, SS, SW, 'speed', {'us': 0, 'metric': 0}, {'us': 257.5, 'metric': 260}, {'us': 8, 'metric': 13}, 1))
W.append(dial('rev', RC, RS, RW, 'rpm', 0, 7000, 7, 4, red=6.5 / 7.0))
LAB_R = R - 6 - 16 - 28
for v in range(0, 161, 40):        # mph: a number every 40
    W.append(text('mph%d' % v, pos(LC, LAB_R, SS + SW * v / 160.0), 80, 'e_lab', str(v), 'dim', 'center', toggle='units=us'))
for v in range(0, 261, 40):
    W.append(text('kmh%d' % v, pos(LC, LAB_R, SS + SW * v / 260.0), 80, 'e_lab', str(v), 'dim', 'center', toggle='!units=us'))
for v in range(0, 8):
    W.append(text('rpm%d' % v, pos(RC, LAB_R, RS + RW * v / 7.0), 60, 'e_lab', str(v), 'dim', 'center'))
W.append(text('speed', (LC[0], LC[1] + 78), 220, 'e_mid', '{{speed}}', 'fg', 'center'))
W.append(text('speed_u', (LC[0], LC[1] + 140), 120, 'e_head', '{{u:speedLc}}', 'accent', 'center', spacing=2))
W.append(text('stage', (RC[0], RC[1] + 78), 120, 'e_mid', '{{stage}}', 'fg', 'center'))
W.append(text('mode', (RC[0], RC[1] + 140), 220, 'e_head', '{{mode}}', 'accent', 'center', spacing=2))
W.append(text('rpm_u', (RC[0], RC[1] - 96), 200, 'e_head', '1/min x 1000', 'dim', 'center'))
# the middle: a large slim clock, the range and the outside temperature (they give way to the map)
W.append(text('clock', (960.0, 270.0), 560, 'n_time', '{{time}}', 'fg', 'center', **hide))
W.append(text('range', (850.0, 392.0), 260, 'e_unit', '{{range}} {{u:distLc}}', 'accent', 'center', **hide))
W.append(text('ambient', (1070.0, 392.0), 200, 'e_unit', '{{ambient}}{{u:temp}}', 'dim', 'center', **hide))
W += [
    {'id': 'strip_cover_l', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 660, 'w': 1380, 'h': 60, 'color': 'bg', 'stripRow': 'l'},
    {'id': 'strip_cover_r', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 1460, 'y': 660, 'w': 460, 'h': 60, 'color': 'bg', 'stripRow': 'r'},
    text('strip_time', (268.0, 690.0), 130, 'e_unit', '{{time}}', 'dim', 'right', stripRow='l'),
    text('strip_ampm', (278.0, 693.0), 50, 'e_head', '{{ampmLc}}', 'dim', 'left', stripRow='l'),
    text('strip_range', (960.0, 690.0), 110, 'e_unit', '{{range}}', 'dim', 'right', stripRow='l'),
    text('strip_range_u', (970.0, 693.0), 40, 'e_head', '{{u:distLc}}', 'dim', 'left', stripRow='l'),
    text('strip_out', (1745.0, 690.0), 100, 'e_unit', '{{ambient}}', 'dim', 'right', stripRow='r'),
    text('strip_out_u', (1755.0, 693.0), 40, 'e_head', '{{u:temp}}', 'dim', 'left', stripRow='r'),
]
L = {'schemaVersion': 2, 'name': 'Night Drive', 'theme': 'night_drive', 'packWaze': 0, 'packWaste': 3,
     '_about': "Night Drive cluster, generated by tools/gen_night.py (edit that and regenerate): a very dark, quiet cluster for night driving. Two slim dials (speed left, revs right) with a thin bronze bezel, hairline ticks, a few warm-white numbers and a dim amber needle with a soft glow, the speed digitally inside the left dial, the gear and drive mode inside the right one, and a large slim clock in the middle with the range and outside temperature under it. While the Waze map shows inside the theme a window opens in the middle and the clock gives way. Black covers BMW's gauges. Widget reference: shared/hud.js header.",
     'widgets': W}
del L['packWaze']
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(L, f, indent=2, ensure_ascii=False)
    f.write('\n')
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import badge_spot; badge_spot.apply(OUT)
print('night.json:', len(W), 'widgets')
