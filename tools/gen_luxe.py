#!/usr/bin/env python3
"""Generates apps/ix3_themes/hud/layouts/luxe.json (the Luxe theme): a classic, luxurious e-drive cluster. Two big round dials
on warm espresso faces with champagne-gold bezels and ivory numerals: the speed on the left (0..260 km/h or 0..160 mph) and the POWER
dial on the right (zero at the top, the CHARGE sector to its left, 10..100 to its right), a fuel level under the speed and the battery
charge under the power. Between them an analog clock, the drive mode, the battery and the range. While the Waze map
shows inside the theme the clock and the readouts give way to a map window between the dials. Built from the same light drawing
as the ePower and Night Drive themes (round dials, thin arcs, text). Edit this and regenerate."""
import json, math, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'layouts', 'luxe.json')
FONT_DIR = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'fonts')
STRIP = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'layouts', 'night.json')    # its bottom row (strip_*) is the shared one
R = 262.0
LC, RC = (470.0, 330.0), (1450.0, 330.0)
TICK = [238, 226, 196]
NEEDLE = [236, 200, 120]
GOLD = [201, 168, 106]


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


def dial(i, center, start, sweep, signal, mn, mx, majors, minors, conn=1):
    s = int(2 * (R + 4))
    return {'id': i, 'type': 'adial', 'class': 'content', 'z': 2, 'x': round(center[0] - s / 2), 'y': round(center[1] - s / 2), 'w': s, 'h': s,
            'signal': signal, 'min': mn, 'max': mx, 'radius': R, 'hub': 22, 'start': start, 'sweep': sweep,
            'majors': majors, 'minors': minors, 'tickLen': [20, 10], 'needle': [0.98, 42, 6, 8], 'redFrom': None,
            'tickColor': TICK, 'needleColor': NEEDLE, 'redColor': NEEDLE, 'faceColor': [26, 19, 14], 'faceEdge': [6, 4, 3],
            'ring': [0.6, 1.0, 14], 'bezelColor': GOLD, 'shadow': [0.0, 0.0, 5.0, 0.0], 'conn': conn}


def arc(i, center, radius, start, sweep, width, color, signal=None, mn=0, mx=1, conn=2, z=3):
    s = round(2 * (radius + width / 2 + 2))
    d = {'id': i, 'type': 'arc', 'class': 'content', 'z': z, 'x': round(center[0] - s / 2), 'y': round(center[1] - s / 2), 'w': s, 'h': s,
         'min': mn, 'max': mx, 'width': width, 'color': color, 'start': round(start, 2), 'sweep': round(sweep, 2), 'conn': conn,
         'signal': signal or 'rpm'}
    if not signal:
        d['min'] = 1000000; d['max'] = 2000000       # a static arc: a signal that never reaches its range
    return d


hide = {'toggle': 'centre=clock'}       # the clock view: not while the map shows, not while charging
W = [{'id': 'bg', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg',
      'hole': [760, 130, 400, 440], 'holeWhen': 'mapUp', 'holeInset': 0, 'holeRadius': 30}]
# ---- the speed dial: 0..260 km/h (0..160 mph), 0 at the lower left
SS, SW = 213.0, 245.0
W.append(dial('spd', LC, SS, SW, 'speed', 0, {'us': 257.5, 'metric': 260}, {'us': 8, 'metric': 13}, 1))
LAB = R - 14 - 20 - 36
for v in range(0, 261, 20):
    W.append(text('kmh%d' % v, pos(LC, LAB, SS + SW * v / 260.0), 80, 'e_lab', str(v), 'dim', 'center', toggle='!units=us'))
for v in range(0, 161, 20):
    W.append(text('mph%d' % v, pos(LC, LAB, SS + SW * v / 160.0), 80, 'e_lab', str(v), 'dim', 'center', toggle='units=us'))
W.append(text('speed', (LC[0], LC[1] + 70), 220, 'e_mid', '{{speed}}', 'fg', 'center'))
W.append(text('speed_u', (LC[0], LC[1] + 114), 120, 'e_head', '{{u:speedLc}}', 'accent', 'center', spacing=2))
W.append(text('fuel_lbl', (LC[0], LC[1] + 154), 200, 'e_head', 'FUEL {{fuelPct}}%', 'dim', 'center'))
W.append(arc('ring_l', LC, 140.0, 0.0, 359.0, 2, 'dim'))
# ---- the power dial: -20..100 % (the charge sector counts down from the top), 0 at the top
PS, PW = -33.0, 200.0
W.append(dial('pow', RC, PS, PW, 'powerPct', -20, 100, 12, 1, 1))
for v in (10, 20, 40, 60, 80, 100):
    W.append(text('pw%d' % v, pos(RC, LAB, PS + PW * (v + 20) / 120.0), 70, 'e_lab', str(v), 'dim', 'center'))
W.append(arc('chg_arc', RC, R - 76, PS + PW * 20 / 120.0 - 0.4, -(PW * 20 / 120.0 - 4), 12, 'green', 'recup', 0, 100, conn=2))      # lit by the estimated recharging, from the top leftwards
W.append(text('charge', pos(RC, R - 40, PS + 7), 120, 'e_head', 'CHARGE', 'green', 'center', spacing=2))
W.append(text('power', (RC[0], RC[1] + 70), 200, 'e_mid', '{{powerPct}}', 'fg', 'center'))
W.append(text('power_cap', (RC[0], RC[1] + 114), 200, 'e_head', 'POWER %', 'accent', 'center', spacing=2))
W.append(text('batt_lbl', (RC[0], RC[1] + 154), 240, 'e_head', 'BATTERY {{hvSoc}}%', 'dim', 'center'))
W.append(arc('ring_r', RC, 140.0, 0.0, 359.0, 2, 'dim'))
# ---- the middle: an analog clock, the drive mode, the range (they give way to the map)
W.append({'id': 'clock', 'type': 'aclock', 'class': 'content', 'z': 3, 'x': 851, 'y': 90, 'w': 220, 'h': 220, 'radius': 92, 'tick': [12, 1.4, 6],
          'hands': NEEDLE, 'ticks': TICK, 'conn': 2, 'toggle': 'centre=clock'})
W.append(text('mode', (961.0, 360.0), 300, 'e_unit', '{{evstate}}  {{mode}}', 'accent', 'center', spacing=3, **hide))
W.append(text('stage', (961.0, 440.0), 120, 'e_mid', '{{stage}}', 'fg', 'center', **hide))
W.append(text('range', (961.0, 520.0), 260, 'e_unit', '{{range}} {{u:distLc}}', 'dim', 'center', **hide))
W.append(text('ambient', (961.0, 570.0), 200, 'e_head', '{{ambient}}{{u:temp}}', 'dim', 'center', **hide))
# ---- the charging view in the middle (while plugged in and charging; the map takes the middle before it)
chg = {'toggle': 'centre=charging'}
W.append({'id': 'chg_bolt', 'type': 'icon', 'icon': 'bolt', 'z': 5, 'x': 916, 'y': 96, 'w': 90, 'h': 110, 'color': 'green', 'toggle': 'centre=charging'})
W.append(text('chg_title', (961.0, 236.0), 300, 'e_unit', 'CHARGING', 'green', 'center', spacing=4, **chg))
W.append(text('chg_kw', (940.0, 316.0), 200, 'e_mid', '{{chargeKw}}', 'fg', 'right', **chg))
W.append(text('chg_kw_u', (952.0, 322.0), 80, 'e_head', 'kW', 'accent', 'left', **chg))
W.append({'id': 'chg_bar', 'type': 'meter', 'class': 'content', 'z': 2, 'x': 771, 'y': 380, 'w': 380, 'h': 18, 'signal': 'hvSoc', 'min': 0, 'max': 100,
          'segments': 30, 'gap': 4, 'colors': ['green', 'green', 'green'], 'at': [1, 1], 'conn': 2, 'toggle': 'centre=charging'})
W.append(text('chg_soc', (961.0, 450.0), 260, 'e_mid', '{{hvSoc}}%', 'fg', 'center', **chg))
W.append(text('chg_eta', (961.0, 520.0), 300, 'e_head', 'FULL IN {{chargeEta}}', 'dim', 'center', spacing=2, **chg))
for w in json.load(open(STRIP))['widgets']:
    if w['id'].startswith('strip_'):
        W.append(w)

L = {'schemaVersion': 2, 'name': 'Luxe', 'theme': 'luxe', 'packWaste': 3,
     '_about': "Luxe cluster, generated by tools/gen_luxe.py (edit that and regenerate): a classic, luxurious e-drive cluster. Two big round dials on warm espresso faces with champagne-gold bezels and ivory numerals, the speed on the left and the POWER dial on the right (zero at the top, the CHARGE sector to its left), the fuel and battery readouts inside the dials, and between them an analog clock, the drive mode, the gear and the range. While the Waze map shows inside the theme a window opens between the dials. Black covers BMW's gauges. Widget reference: shared/hud.js header.",
     'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(L, f, indent=2, ensure_ascii=False)
    f.write('\n')
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import badge_spot; badge_spot.apply(OUT)
print('luxe.json:', len(W), 'widgets')
