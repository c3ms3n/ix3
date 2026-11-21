#!/usr/bin/env python3
"""Generates apps/ix3_themes/hud/layouts/eco.json (the Eco theme): two ring dials in the style of the BMW i8's cluster
(apps/6.jpg), made calmer and more precise. Left: the speed ring (0..260 km/h, 0..160 mph) with the efficient-speed window
marked in green and the engine temperature on a thin inner ring. Right: the power ring (0..100 %, blue in the eco range, amber
then red as it rises) with the fuel level on a thin inner ring. Middle: the outside temperature and clock, the drive mode and
gear, a glowing perspective floor. Bottom: the range, the clock and the outside temperature. Edit this and regenerate."""
import json, math, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'layouts', 'eco.json')
FONT_DIR = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'fonts')

LC, RC = (470.0, 325.0), (1450.0, 325.0)     # the dials' centres
R = 232.0                                    # the ring's mid radius
SWEEP = 268.0
LSTART, RSTART = 133.0, 227.0                # the left ring runs clockwise from the bottom right, the right one anticlockwise from the bottom left


def cell(font):
    return json.load(open(os.path.join(FONT_DIR, font + '.json')))['cellHeight']


def pos(center, radius, deg):
    a = math.radians(deg)
    return (center[0] + radius * math.sin(a), center[1] - radius * math.cos(a))


def arc(i, center, radius, start, sweep, width, signal, mn, mx, color, conn, z=2, **kw):
    s = round(2 * (radius + width / 2 + 2))
    d = {'id': i, 'type': 'arc', 'class': 'content', 'z': z, 'x': round(center[0] - s / 2), 'y': round(center[1] - s / 2), 'w': s, 'h': s,
         'min': mn, 'max': mx, 'width': width, 'color': color, 'start': round(start, 2), 'sweep': round(sweep, 2), 'conn': conn}
    if signal:
        d['signal'] = signal
    else:        # a static ring: a signal that never reaches its range, so only the track is drawn
        d['signal'] = 'rpm'; d['min'] = 1000000; d['max'] = 2000000
    d.update(kw)
    return d


def text(i, c, w, font, t, color='fg', align='center', conn=1, **kw):
    h = cell(font)
    x0 = c[0] - w / 2 if align == 'center' else (c[0] - w if align == 'right' else c[0])      # c is the anchor: centre, right edge or left edge
    d = {'id': i, 'type': 'text', 'z': 5, 'x': round(x0), 'y': round(c[1] - h / 2), 'w': w, 'h': h, 'text': t, 'font': font,
         'color': color, 'align': align, 'conn': conn}
    d.update(kw)
    return d


# the background; while the Waze map shows inside the theme ("Show Waze map inside the theme") a window opens between the dials
W = [{'id': 'bg', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg', 'conn': 1,
      'hole': [770, 160, 380, 320], 'holeWhen': 'mapUp', 'holeInset': 0, 'holeRadius': 30}]
# the floor
W.append({'id': 'floor', 'type': 'efloor', 'class': 'content', 'z': 1, 'x': 690, 'y': 420, 'w': 540, 'h': 235, 'vp': [960, 420], 'half': 280,
          'color': [70, 170, 255], 'glow': [20, 80, 200], 'conn': 1, 'toggle': '!mapUp'})

# ---- left: speed
W.append(arc('spd_ring_out', LC, R + 34, LSTART, SWEEP, 3, None, 0, 1, 'dim', 2, z=1))
W.append(arc('spd_ring_in', LC, R - 40, LSTART, SWEEP, 2, None, 0, 1, 'dim', 2, z=1))
W.append(arc('spd_arc', LC, R, LSTART, SWEEP, 30, 'speed', 0, 260, 'cy', 2))
# the efficient-speed window, 80..115 km/h, as a green line just outside the ring
e0, e1 = 80.0 / 260 * SWEEP, 115.0 / 260 * SWEEP
W.append(arc('eco_win', LC, R + 24, LSTART + e0, e1 - e0, 6, 'speed', -2, -1, 'green', 2, z=3))
W.append(arc('cool_arc', LC, R - 56, LSTART, SWEEP * 0.6, 4, 'coolant', 50, 120, 'accent', 2, z=2))
# the scale numbers (km/h; the mph ones by the speed converted)
for k, v in enumerate((0, 50, 100, 150, 200, 260)):
    p = pos(LC, R + 52, LSTART + SWEEP * v / 260.0)
    W.append(text('kmh%d' % v, p, 80, 'e_lab', str(v), 'dim', 'center', 2, toggle='!units=us'))
for v in (0, 40, 80, 120, 160):
    p = pos(LC, R + 52, LSTART + SWEEP * (v / 0.621371) / 260.0)
    W.append(text('mph%d' % v, p, 80, 'e_lab', str(v), 'dim', 'center', 2, toggle='units=us'))
W.append(text('speed', (LC[0], LC[1] - 14), 330, 'e_speed', '{{speed}}', 'fg', 'center', 1))
W.append(text('speed_unit', (LC[0], LC[1] + 84), 160, 'e_unit', '{{u:speedLc}}', 'accent', 'center', 1))
W.append(text('cool_lbl', pos(LC, R - 56, LSTART + SWEEP * 0.6 + 8), 110, 'e_head', '{{coolant}}°', 'dim', 'left', 1))

# ---- right: power
P0, P1 = 0.60 * SWEEP, 0.85 * SWEEP
W.append(arc('pow_ring_out', RC, R + 34, RSTART, -SWEEP, 3, None, 0, 1, 'dim', 3, z=1))
W.append(arc('pow_ring_in', RC, R - 40, RSTART, -SWEEP, 2, None, 0, 1, 'dim', 3, z=1))
W.append(arc('pow_eco', RC, R, RSTART, -P0, 30, 'powerPct', 0, 60, 'cy', 3))
W.append(arc('pow_mid', RC, R, RSTART - P0, -(P1 - P0), 30, 'powerPct', 60, 85, 'amber', 3))
W.append(arc('pow_hi', RC, R, RSTART - P1, -(SWEEP - P1), 30, 'powerPct', 85, 100, 'hot', 3))
W.append(arc('fuel_arc', RC, R - 56, RSTART, -SWEEP * 0.6, 4, 'fuel', 0, 1, 'amber', 3, z=2))
# mild hybrid: the charge sector in the ring's gap, from the zero point the other way, lit by the estimated recharging (hud _recupTick)
CHG = 62.0
W.append(arc('chg_trk', RC, R, RSTART, CHG, 30, None, 0, 1, 'dim', 3, z=1))
W.append(arc('chg_arc', RC, R, RSTART, CHG, 30, 'recup', 0, 100, 'green', 3))
W.append(text('chg_lbl', pos(RC, R + 100, RSTART + CHG * 0.5), 110, 'e_head', 'CHARGE', 'green', 'center', 3, spacing=2))
for v in (0, 25, 50, 75, 100):
    p = pos(RC, R + 52, RSTART - SWEEP * v / 100.0)
    W.append(text('pow%d' % v, p, 80, 'e_lab', str(v), 'dim', 'center', 3))
W.append(text('pow_head', (RC[0], RC[1] - 110), 260, 'e_head', 'POWER %', 'accent', 'center', 1, spacing=3))
W.append(text('power', (RC[0], RC[1] - 14), 300, 'e_mid', '{{powerPct}}', 'fg', 'center', 1))
W.append(text('mode', (RC[0], RC[1] + 72), 260, 'e_unit', '{{mode}}', 'green', 'center', 1, spacing=2))
W.append(text('fuel_lbl', pos(RC, R - 56, RSTART - SWEEP * 0.6 - 8), 110, 'e_head', '{{fuelPct}}%', 'dim', 'right', 1))

# ---- middle
W.append(text('ambient', (960.0, 70.0), 240, 'e_clock', '{{ambient}}{{u:temp}}', 'fg', 'center', 1))
W.append(text('clock', (960.0, 126.0), 240, 'e_clock', '{{time}}', 'dim', 'center', 1))
W.append(text('stage', (960.0, 320.0), 120, 'e_mid', '{{stage}}', 'fg', 'center', 1, toggle='!mapUp'))
W.append(text('gear', (960.0, 388.0), 120, 'e_unit', 'GEAR {{gearnum}}', 'dim', 'center', 1, spacing=2, toggle='!mapUp'))
# the bottom row
W += [
    {'id': 'strip_cover_l', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 660, 'w': 1380, 'h': 60, 'color': 'bg', 'stripRow': 'l'},
    {'id': 'strip_cover_r', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 1460, 'y': 660, 'w': 460, 'h': 60, 'color': 'bg', 'stripRow': 'r'},
    text('strip_time', (268.0, 690.0), 130, 'e_unit', '{{time}}', 'fg', 'right', 1, stripRow='l'),
    text('strip_ampm', (278.0, 693.0), 50, 'e_head', '{{ampmLc}}', 'dim', 'left', 1, stripRow='l'),
    text('strip_range', (960.0, 690.0), 110, 'e_unit', '{{range}}', 'fg', 'right', 1, stripRow='l'),
    text('strip_range_u', (970.0, 693.0), 40, 'e_head', '{{u:distLc}}', 'dim', 'left', 1, stripRow='l'),
    text('strip_out', (1745.0, 690.0), 100, 'e_unit', '{{ambient}}', 'fg', 'right', 1, stripRow='r'),
    text('strip_out_u', (1755.0, 693.0), 40, 'e_head', '{{u:temp}}', 'dim', 'left', 1, stripRow='r'),
]
L = {'schemaVersion': 2, 'name': 'Eco', 'theme': 'eco', 'packWaste': 3,
     '_about': "Eco cluster, generated by tools/gen_eco.py (edit that and regenerate), in the style of the BMW i8's cluster (apps/6.jpg) but calmer: a speed ring on the left (0..260 km/h or 0..160 mph, the efficient 80..115 km/h window marked in green, the engine temperature on a thin inner ring), a power ring on the right (blue in the eco range, amber then red as the load rises, the fuel level on a thin inner ring), the outside temperature and clock on top, the drive mode and gear, a glowing perspective floor, and the range, clock and outside temperature along the bottom. Black covers BMW's gauges. While the Waze map shows inside the theme a window opens between the dials (the floor and gear give way). Widget reference: shared/hud.js header.",
     'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(L, f, indent=2, ensure_ascii=False)
    f.write('\n')
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import badge_spot; badge_spot.apply(OUT)
print('eco.json:', len(W), 'widgets')
