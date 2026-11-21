#!/usr/bin/env python3
"""Generates apps/ix3_themes/hud/layouts/neon.json (the Neon City theme): a Cyberpunk-style sport cluster. A lit night-city
skyline along the bottom with twinkling neon windows (the windows twinkle faster with the speed), angular neon frames in yellow,
cyan and magenta, the speed huge in yellow with a cyan ghost, a slanted rev strip that runs yellow, orange, magenta with a peak
mark, the gear and drive mode in magenta, and data cards left and right. While the Waze map shows inside the theme a window opens
under the speed (the skyline is cut out of it and the gear gives way). Edit this and regenerate; do not hand-edit the JSON."""
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'layouts', 'neon.json')
FONT_DIR = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'fonts')
Y, C, M, WH = [252, 238, 10], [20, 242, 255], [255, 30, 150], [255, 255, 255]


def cell(font):
    return json.load(open(os.path.join(FONT_DIR, font + '.json')))['cellHeight']


def text(i, c, w, font, t, color='fg', align='center', **kw):
    h = cell(font)
    x0 = c[0] - w / 2 if align == 'center' else (c[0] - w if align == 'right' else c[0])
    d = {'id': i, 'type': 'text', 'z': 5, 'x': round(x0), 'y': round(c[1] - h / 2), 'w': w, 'h': h, 'text': t, 'font': font,
         'color': color, 'align': align}
    d.update(kw)
    return d


def poly(pts, color, half, close=False):
    seq = pts + ([pts[0]] if close else [])
    return [{'seg': [*seq[i], *seq[i + 1]], 'color': color, 'half': half} for i in range(len(seq) - 1)]


def card(x, y, w, h, cut, color):
    """A frame with its top-right and bottom-left corners cut."""
    return poly([(x, y), (x + w - cut, y), (x + w, y + cut), (x + w, y + h), (x + cut, y + h), (x, y + h - cut)], color, 1.6, close=True)


hide = {'toggle': '!mapUp'}
HOLE = [690, 320, 540, 250]
lines = []
lines += poly([(520, 205), (520, 68), (562, 28), (1358, 28), (1400, 68), (1400, 205)], Y, 2.4)          # the speed frame
lines += poly([(540, 205), (540, 76), (572, 46), (1348, 46), (1380, 76), (1380, 205)], C, 1.0)
lines += poly([(520, 205), (520, 190)], M, 4.0) + poly([(1400, 205), (1400, 190)], M, 4.0)
lines += poly([(700, 28), (760, 28)], M, 4.0) + poly([(1160, 28), (1220, 28)], M, 4.0)
lines += card(60, 330, 430, 240, 36, C) + card(1430, 330, 430, 240, 36, M)
lines += poly([(60, 330), (130, 330)], Y, 4.0) + poly([(1790, 570), (1860, 570)], Y, 4.0)
lines += poly([(350, 296), (1570, 296)], C, 1.0)
W = [{'id': 'bg', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg',
      'hole': HOLE, 'holeWhen': 'mapUp', 'holeInset': 0, 'holeRadius': 14},
     {'id': 'sky', 'type': 'csky', 'class': 'content', 'z': 1, 'x': 0, 'y': 300, 'w': 1920, 'h': 360, 'baseY': 0.965, 'building': 44, 'brightness': 0.95,
      'clear': [[60, 330, 430, 240], [1430, 330, 430, 240], [690, 320, 540, 250]], 'clearDim': 0.7, 'feather': 10,
      'hole': HOLE, 'holeWhen': 'mapUp', 'holeInset': 0, 'holeRadius': 14, 'conn': 2},
     {'id': 'frames', 'type': 'neon', 'class': 'content', 'z': 3, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'lines': lines,
      'strip': {'rect': [380, 238, 1140, 34], 'cells': 50, 'slant': 24, 'gap': 5, 'orange': 0.62, 'magenta': 0.86, 'max': 8000}, 'conn': 3}]
# the speed: a cyan ghost under the yellow digits
W.append(text('speed_g', (965.0, 123.0), 760, 'q_big', '{{speed}}', 'accent', 'center', spacing=14, conn=1))
W.append(text('speed', (960.0, 118.0), 760, 'q_big', '{{speed}}', 'fg', 'center', spacing=14, conn=1, hotWhen='now'))
W.append(text('speed_u', (960.0, 196.0), 200, 'q_txt', '{{u:speed}}', 'accent', 'center', spacing=8, conn=1))
W.append(text('rpm_l', (380.0, 312.0), 100, 'q_txt', 'RPM', 'accent', 'left', conn=1))
W.append(text('rpm_v', (1520.0, 312.0), 260, 'q_txt', '{{rpm}}', 'fg', 'right', conn=1))
W.append(text('gear', (960.0, 400.0), 300, 'q_mid', '{{stage}}{{gearnum}}', 'hot', 'center', conn=1, hotWhen='now', **hide))
W.append(text('mode', (960.0, 470.0), 400, 'q_txt', '{{mode}}', 'accent', 'center', spacing=6, conn=1, **hide))
LEFT = (('TMP', '{{coolant}}{{u:temp}}'), ('OIL', '{{oil}}{{u:temp}}'), ('FUEL', '{{fuelPct}}%'), ('BOOST', '{{boost}} {{u:boost}}'))
RIGHT = (('RNG', '{{range}} {{u:dist}}'), ('OUT', '{{ambient}}{{u:temp}}'), ('AVG', '{{avgSpeed}} {{u:speed}}'), ('TIME', '{{time}}'))
for k, (lab, tok) in enumerate(LEFT):
    y = 366.0 + 50 * k
    W.append(text('tl%d' % k, (100.0, y), 150, 'q_txt', lab, 'accent', 'left', conn=1))
    extra = {'toggle': 'showBoost'} if lab == 'BOOST' else {}
    W.append(text('tv%d' % k, (470.0, y), 240, 'q_txt', tok, 'fg', 'right', conn=1, **extra))
for k, (lab, tok) in enumerate(RIGHT):
    y = 366.0 + 50 * k
    W.append(text('rl%d' % k, (1470.0, y), 150, 'q_txt', lab, 'hot' if False else 'accent', 'left', conn=1))
    W.append(text('rv%d' % k, (1840.0, y), 280, 'q_txt', tok, 'fg', 'right', conn=1))
W += [
    {'id': 'strip_cover_l', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 660, 'w': 1380, 'h': 60, 'color': 'bg', 'stripRow': 'l'},
    {'id': 'strip_cover_r', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 1460, 'y': 660, 'w': 460, 'h': 60, 'color': 'bg', 'stripRow': 'r'},
    text('strip_time', (268.0, 690.0), 130, 'q_txt', '{{time}}', 'accent', 'right', stripRow='l'),
    text('strip_range', (960.0, 690.0), 110, 'q_txt', '{{range}}', 'fg', 'right', stripRow='l'),
    text('strip_range_u', (970.0, 693.0), 90, 'q_txt', '{{u:dist}}', 'accent', 'left', stripRow='l'),
    text('strip_out', (1745.0, 690.0), 100, 'q_txt', '{{ambient}}', 'fg', 'right', stripRow='r'),
    text('strip_out_u', (1755.0, 693.0), 60, 'q_txt', '{{u:temp}}', 'accent', 'left', stripRow='r'),
]
L = {'schemaVersion': 2, 'name': 'Neon City', 'theme': 'neon', 'packWaste': 3,
     '_about': "Neon City cluster, generated by tools/gen_neon.py (edit that and regenerate): a Cyberpunk-style sport cluster. A lit night-city skyline along the bottom with twinkling neon windows (they twinkle faster with the speed), angular neon frames in yellow, cyan and magenta, the speed huge in yellow with a cyan ghost, a slanted rev strip that runs yellow, orange, magenta with a peak mark, the gear and drive mode, and data cards left and right. While the Waze map shows inside the theme a window opens under the speed (the skyline is cut out of it and the gear gives way). Black covers BMW's gauges. Widget reference: shared/hud.js header.",
     'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(L, f, indent=2, ensure_ascii=False)
    f.write('\n')
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import badge_spot; badge_spot.apply(OUT)
print('neon.json:', len(W), 'widgets;', len(lines), 'line segments')
