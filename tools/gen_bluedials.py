#!/usr/bin/env python3
"""Generates apps/ix3_themes/hud/layouts/bluedials.json (the Blue Dials theme), after a photo of a BMW 5 Series analog-style
digital cluster (apps/8.jpeg): two round dials with a vivid blue face, white ticks and numbers, a dark inner disc and a tapered
red needle (speed 0..330 km/h or 0..200 mph on the left, revs 0..7 on the right), a small fuel dial far left and a small
temperature dial far right, a blue road floor in the middle with the speed, the temperature and the gear. While the Waze map
shows inside the theme the road gives way to a map window and the speed stays above it. Edit this and regenerate."""
import json, math, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'layouts', 'bluedials.json')
FONT_DIR = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'fonts')
R = 272.0
LC, RC = (470.0, 330.0), (1450.0, 330.0)
FC, TC = (100.0, 410.0), (1820.0, 410.0)
SR = 64.0
WHITE = [245, 246, 252]
NEEDLE = [255, 36, 58]


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


def dial(i, center, radius, start, sweep, signal, mn, mx, majors, minors, tick, needle, hub, red=None, ring=0.7, bezel=12, inner=0.42, **kw):
    s = int(2 * (radius + 4))
    d = {'id': i, 'type': 'adial', 'class': 'content', 'z': 2, 'x': round(center[0] - s / 2), 'y': round(center[1] - s / 2), 'w': s, 'h': s,
         'signal': signal, 'min': mn, 'max': mx, 'radius': radius, 'hub': hub, 'start': start, 'sweep': sweep,
         'majors': majors, 'minors': minors, 'tickLen': tick, 'needle': needle, 'redFrom': red,
         'tickColor': WHITE, 'needleColor': NEEDLE, 'redColor': [255, 40, 60], 'faceColor': [14, 30, 255], 'faceEdge': [2, 6, 130],
         'ring': [ring, 1.0, bezel], 'bezelColor': [226, 216, 196], 'innerDisc': [inner, 3, 6, 34],
         'shadow': [1.0, 0.0, 5.0, 0.0]}
    d.update(kw)
    return d


W = [{'id': 'bg', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg',
      'hole': [745, 170, 430, 420], 'holeWhen': 'mapUp', 'holeInset': 0, 'holeRadius': 30}]
hide = {'toggle': '!mapUp'}
# the road floor in the middle (it gives way to the map window)
W.append({'id': 'floor', 'type': 'efloor', 'class': 'content', 'z': 1, 'x': 745, 'y': 290, 'w': 430, 'h': 330, 'vp': [960, 290], 'half': 215,
          'color': [86, 156, 255], 'glow': [16, 58, 210], 'toggle': '!mapUp'})
# the dials: speed (0..330 km/h in 11 steps; 0..200 mph in 10) and revs (0..7)
SPEED_START = 207.0
W.append(dial('spd', LC, R, SPEED_START, 244.0, 'speed', 0, {'us': 321.87, 'metric': 330}, {'us': 10, 'metric': 11}, 2,
              [26, 14], [0.94, 36, 12, 7], 26, bezel=16))
W.append(dial('rev', RC, R, 270.0, 230.0, 'rpm', 0, 7000, 7, 4, [26, 14], [0.94, 36, 12, 7], 26, red=6.5 / 7.0, bezel=16))
LAB_R = R - 12 - 26 - 34
for v in range(20, 201, 20):                       # mph, every 20
    W.append(text('mph%d' % v, pos(LC, LAB_R, SPEED_START + 244.0 * v / 200.0), 80, 'g_lab', str(v), 'fg', 'center', toggle='units=us'))
for v in range(30, 331, 30):                       # km/h, every 30 (from 30)
    W.append(text('kmh%d' % v, pos(LC, LAB_R, SPEED_START + 244.0 * v / 330.0), 80, 'g_lab', str(v), 'fg', 'center', toggle='!units=us'))
for v in range(0, 8):
    W.append(text('rpm%d' % v, pos(RC, LAB_R, 270.0 + 230.0 * v / 7.0), 60, 'g_lab', str(v), 'fg', 'center'))
W.append(text('rpm_u', (RC[0] - 120, RC[1] + 40), 140, 'g_small', '1/min x1000', 'fg', 'center'))
W.append(text('rpm_off', (RC[0] - 100, RC[1] + 190), 70, 'g_small', 'OFF', 'fg', 'center'))
# the small dials
W.append(dial('fuel_dial', FC, SR, 205.0, 150.0, 'fuel', 0, 1, 2, 4, [13, 7], [0.82, 10, 5, 3], 8, ring=0.74, bezel=6, inner=0.0, conn=2, shadow=[0.0, 0.0, 5.0, 0.0]))
W.append(dial('temp_dial', TC, SR, 205.0, 150.0, 'coolant', 50, 130, 2, 4, [13, 7], [0.82, 10, 5, 3], 8, ring=0.74, bezel=6, inner=0.0, conn=2, shadow=[0.0, 0.0, 5.0, 0.0]))
W.append(text('fuel_1', (FC[0] - 40, FC[1] - 48), 40, 'g_small', '1', 'fg', 'center'))
W.append(text('fuel_0', (FC[0] + 44, FC[1] + 14), 40, 'g_small', '0', 'fg', 'center'))
W.append(text('temp_c', (TC[0] - 44, TC[1] + 14), 40, 'g_small', 'C', 'fg', 'center'))
W.append(text('temp_h', (TC[0] + 40, TC[1] - 48), 40, 'g_small', 'H', 'fg', 'center'))
# the middle: the speed (it stays above the map), the temperature, the gear and the drive mode
W.append(text('speed', (960.0, 86.0), 220, 'g_big', '{{speed}}', 'fg', 'center'))
W.append(text('speed_u', (960.0, 134.0), 120, 'g_small', '{{u:speedLc}}', 'fg', 'center'))
W.append(text('ambient', (960.0, 190.0), 200, 'g_unit', '{{ambient}}{{u:temp}}', 'fg', 'center', **hide))
W.append(text('range', (960.0, 262.0), 240, 'g_small', 'RANGE {{range}} {{u:distLc}}', 'fg', 'center', **hide))
W.append(text('stage', (1085.0, 590.0), 60, 'g_gear', '{{stage}}', 'fg', 'center', **hide))
W.append(text('mode', (1180.0, 590.0), 140, 'g_small', '{{mode}}', 'fg', 'left', **hide))
W += [
    {'id': 'strip_cover_l', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 660, 'w': 1380, 'h': 60, 'color': 'bg', 'stripRow': 'l'},
    {'id': 'strip_cover_r', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 1460, 'y': 660, 'w': 460, 'h': 60, 'color': 'bg', 'stripRow': 'r'},
    text('strip_time', (268.0, 690.0), 130, 'g_unit', '{{time}}', 'fg', 'right', stripRow='l'),
    text('strip_ampm', (278.0, 693.0), 50, 'g_small', '{{ampmLc}}', 'fg', 'left', stripRow='l'),
    text('strip_range', (960.0, 690.0), 110, 'g_unit', '{{range}}', 'fg', 'right', stripRow='l'),
    text('strip_range_u', (970.0, 693.0), 40, 'g_small', '{{u:distLc}}', 'fg', 'left', stripRow='l'),
    text('strip_out', (1745.0, 690.0), 100, 'g_unit', '{{ambient}}', 'fg', 'right', stripRow='r'),
    text('strip_out_u', (1755.0, 693.0), 40, 'g_small', '{{u:temp}}', 'fg', 'left', stripRow='r'),
]
L = {'schemaVersion': 2, 'name': 'Blue Dials', 'theme': 'bluedials', 'packWaste': 3,
     '_about': "Blue Dials cluster, generated by tools/gen_bluedials.py (edit that and regenerate), after a photo of a BMW 5 Series cluster (apps/8.jpeg): two round dials with a vivid blue face, white ticks and numbers, a dark inner disc and a tapered red needle (speed 0..330 km/h or 0..200 mph on the left, revs 0..7 on the right), a small fuel dial far left and a small temperature dial far right, a blue road floor in the middle with the speed, the temperature, the range, the gear and the drive mode. While the Waze map shows inside the theme the road, temperature, range, gear and mode give way to a map window and the speed stays above it. Black covers BMW's gauges. Widget reference: shared/hud.js header.",
     'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(L, f, indent=2, ensure_ascii=False)
    f.write('\n')
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import badge_spot; badge_spot.apply(OUT)
print('bluedials.json:', len(W), 'widgets')
