#!/usr/bin/env python3
"""Generates apps/ix3_themes/hud/layouts/rain.json (the Digital Rain theme): falling green glyph columns behind the gauges
(one shader layer, shaders.js MRAIN; the rain runs faster with the speed and is dimmed behind the readouts so they stay readable),
the speed in huge seven-segment digits at the top with a segmented rev bar under it, the gear big in the middle, terminal lines
on each side (TMP / OIL / FUEL / BOOST left, RNG / OUT / AVG / TIME right). While the Waze map shows inside the theme a window opens
in the middle and the gear gives way. Edit this and regenerate; do not hand-edit the JSON."""
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'layouts', 'rain.json')
FONT_DIR = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'fonts')


def cell(font):
    return json.load(open(os.path.join(FONT_DIR, font + '.json')))['cellHeight']


def text(i, c, w, font, t, color='fg', align='center', **kw):
    h = cell(font)
    x0 = c[0] - w / 2 if align == 'center' else (c[0] - w if align == 'right' else c[0])
    d = {'id': i, 'type': 'text', 'z': 5, 'x': round(x0), 'y': round(c[1] - h / 2), 'w': w, 'h': h, 'text': t, 'font': font,
         'color': color, 'align': align}
    d.update(kw)
    return d


hide = {'toggle': '!mapUp'}
SPEED_BOX = [560, 30, 800, 190]
RPM_BOX = [340, 205, 1240, 90]
GEAR_BOX = [660, 300, 600, 260]
LEFT_BOX = [60, 305, 470, 280]
RIGHT_BOX = [1390, 305, 470, 280]
W = [{'id': 'bg', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg',
      'hole': [670, 290, 580, 330], 'holeWhen': 'mapUp', 'holeInset': 0, 'holeRadius': 24},
     {'id': 'rain', 'type': 'mrain', 'class': 'content', 'z': 1, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'cell': [22, 30], 'color': [0, 235, 80],
      'brightness': 0.9, 'clear': [SPEED_BOX, RPM_BOX, GEAR_BOX, LEFT_BOX, RIGHT_BOX], 'clearDim': 0.78, 'feather': 14, 'tail': 1.0,
      'speedGain': 0.035, 'conn': 2, 'heat': {'at': [0.62, 0.88], 'mid': [255, 190, 30], 'hot': [255, 40, 30], 'rush': 14.0}, 'hole': [670, 290, 580, 330], 'holeWhen': 'mapUp', 'holeInset': 0, 'holeRadius': 24}]
# the speed, huge, with the unit
W.append(text('speed', (960.0, 112.0), 700, 'r_big', '{{speed}}', 'fg', 'center', spacing=18, conn=1, hotWhen='now'))
W.append(text('speed_u', (960.0, 204.0), 200, 'r_txt', '{{u:speed}}', 'accent', 'center', spacing=6, conn=1))
# the rev bar under it, and its number
W.append({'id': 'revs', 'type': 'meter', 'class': 'content', 'z': 2, 'x': 360, 'y': 226, 'w': 1200, 'h': 30, 'signal': 'rpm', 'min': 0, 'max': 8000,
          'segments': 48, 'gap': 4, 'colors': ['accent', 'amber', 'hot'], 'at': [0.62, 0.86], 'trackColor': 'track', 'peak': 2500, 'peakColor': 'fg', 'conn': 3})
W.append(text('rpm_l', (360.0, 276.0), 120, 'r_txt', 'RPM', 'dim', 'left', conn=1))
W.append(text('rpm_v', (1560.0, 276.0), 300, 'r_txt', '{{rpm}}', 'fg', 'right', conn=1))
# the gear, big, in the middle (it gives way to the map window)
W.append(text('gear', (960.0, 430.0), 420, 'r_big', '{{gearnum}}', 'fg', 'center', conn=1, hotWhen='now', **hide))
W.append(text('mode', (960.0, 540.0), 400, 'r_txt', '{{mode}}', 'accent', 'center', spacing=4, conn=1, **hide))
# terminal lines, left and right
LEFT = (('TMP', '{{coolant}}{{u:temp}}'), ('OIL', '{{oil}}{{u:temp}}'), ('FUEL', '{{fuelPct}}%'), ('BOOST', '{{boost}} {{u:boost}}'))
RIGHT = (('RNG', '{{range}} {{u:dist}}'), ('OUT', '{{ambient}}{{u:temp}}'), ('AVG', '{{avgSpeed}} {{u:speed}}'), ('TIME', '{{time}}'))
for k, (lab, tok) in enumerate(LEFT):
    y = 340.0 + 62 * k
    W.append(text('tl%d' % k, (100.0, y), 150, 'r_txt', lab, 'dim', 'left', conn=1))
    extra = {'toggle': 'showBoost'} if lab == 'BOOST' else {}
    W.append(text('tv%d' % k, (500.0, y), 260, 'r_txt', tok, 'fg', 'right', conn=1, **extra))
for k, (lab, tok) in enumerate(RIGHT):
    y = 340.0 + 62 * k
    W.append(text('rl%d' % k, (1430.0, y), 150, 'r_txt', lab, 'dim', 'left', conn=1))
    W.append(text('rv%d' % k, (1830.0, y), 300, 'r_txt', tok, 'fg', 'right', conn=1))
W += [
    {'id': 'strip_cover_l', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 660, 'w': 1380, 'h': 60, 'color': 'bg', 'stripRow': 'l'},
    {'id': 'strip_cover_r', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 1460, 'y': 660, 'w': 460, 'h': 60, 'color': 'bg', 'stripRow': 'r'},
    text('strip_time', (268.0, 690.0), 130, 'r_txt', '{{time}}', 'fg', 'right', stripRow='l'),
    text('strip_range', (960.0, 690.0), 110, 'r_txt', '{{range}}', 'fg', 'right', stripRow='l'),
    text('strip_range_u', (970.0, 693.0), 40, 'r_txt', '{{u:dist}}', 'dim', 'left', stripRow='l'),
    text('strip_out', (1745.0, 690.0), 100, 'r_txt', '{{ambient}}', 'fg', 'right', stripRow='r'),
    text('strip_out_u', (1755.0, 693.0), 40, 'r_txt', '{{u:temp}}', 'dim', 'left', stripRow='r'),
]
L = {'schemaVersion': 2, 'name': 'Digital Rain', 'theme': 'rain', 'packWaste': 3,
     '_about': "Digital Rain cluster, generated by tools/gen_rain.py (edit that and regenerate): falling green glyph columns behind the gauges (one shader layer; the rain runs faster with the speed and is dimmed behind the readouts), the speed in huge seven-segment digits at the top with a segmented rev bar under it, the gear big in the middle, terminal lines on each side (TMP / OIL / FUEL / BOOST left, RNG / OUT / AVG / TIME right). While the Waze map shows inside the theme a window opens in the middle and the gear and mode give way. Black covers BMW's gauges. Widget reference: shared/hud.js header.",
     'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(L, f, indent=2, ensure_ascii=False)
    f.write('\n')
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import badge_spot; badge_spot.apply(OUT)
print('rain.json:', len(W), 'widgets')
