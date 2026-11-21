#!/usr/bin/env python3
"""Generates apps/ix3_themes/hud/layouts/epower.json (the ePower theme), after a press photo of a BMW plug-in hybrid cluster
(apps/9.jpg): two big round dials on a dark navy face with polished rims, grey-white ticks and numbers and a long red-orange
needle with a white core. Left: the speed (0..260 km/h or 0..160 mph). Right: the POWER % dial, zero at the top, the blue CHARGE
sector to its left and 10..100 to its right. Between them a small clock, the outside temperature and the drive-mode logo; a fuel
dial far left (with the range) and a battery dial far right; TOTAL / TRIP along the bottom. While the Waze map shows inside the
theme the clock, temperature and logo give way to a map window between the dials. Edit this and regenerate."""
import json, math, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'layouts', 'epower.json')
FONT_DIR = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'fonts')
R = 288.0
LC, RC = (470.0, 330.0), (1450.0, 330.0)
FC, BC = (98.0, 440.0), (1822.0, 440.0)
SR = 72.0
TICK = [236, 240, 248]
NEEDLE = [255, 88, 44]
BLUE = [64, 150, 255]


def r1(pts):
    return [[round(x, 1), round(y, 1)] for x, y in pts]


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


def dial(i, center, radius, start, sweep, signal, mn, mx, majors, minors, tick, needle, hub, bezel=16, inner=0.5, **kw):
    s = int(2 * (radius + 4))
    d = {'id': i, 'type': 'adial', 'class': 'content', 'z': 2, 'x': round(center[0] - s / 2), 'y': round(center[1] - s / 2), 'w': s, 'h': s,
         'signal': signal, 'min': mn, 'max': mx, 'radius': radius, 'hub': hub, 'start': start, 'sweep': sweep,
         'majors': majors, 'minors': minors, 'tickLen': tick, 'needle': needle, 'redFrom': None,
         'tickColor': TICK, 'needleColor': NEEDLE, 'redColor': NEEDLE, 'faceColor': [10, 18, 44], 'faceEdge': [2, 4, 14],
         'ring': [0.56, 1.0, bezel], 'bezelColor': [206, 212, 228], 'innerDisc': [inner, 3, 6, 20], 'shadow': [0.0, 0.0, 5.0, 0.0]}
    d.update(kw)
    return d


def arc(i, center, radius, start, sweep, width, color, conn=2, signal=None, mn=0, mx=1, z=3):
    s = round(2 * (radius + width / 2 + 2))
    d = {'id': i, 'type': 'arc', 'class': 'content', 'z': z, 'x': round(center[0] - s / 2), 'y': round(center[1] - s / 2), 'w': s, 'h': s,
         'min': mn, 'max': mx, 'width': width, 'color': color, 'start': round(start, 2), 'sweep': round(sweep, 2), 'conn': conn,
         'signal': signal or 'rpm'}
    if not signal:
        d['min'] = 1000000; d['max'] = 2000000       # a static arc: a signal that never reaches its range
    return d


W = [{'id': 'bg', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg',
      'hole': [790, 150, 340, 330], 'holeWhen': 'mapUp', 'holeInset': 0, 'holeRadius': 28}]
hide = {'toggle': '!mapUp'}
# ---- the speed dial: 0..260 km/h (0..160 mph), 0 at the lower left
SS, SW = 213.0, 245.0
W.append(dial('spd', LC, R, SS, SW, 'speed', 0, {'us': 257.5, 'metric': 260}, {'us': 8, 'metric': 13}, 1, [22, 11], [0.98, 44, 7, 8], 24, conn=1))
LAB = R - 16 - 22 - 36
for v in range(0, 261, 20):
    W.append(text('kmh%d' % v, pos(LC, LAB, SS + SW * v / 260.0), 80, 'p_lab', str(v), 'dim', 'center', toggle='!units=us'))
for v in range(0, 161, 20):
    W.append(text('mph%d' % v, pos(LC, LAB, SS + SW * v / 160.0), 80, 'p_lab', str(v), 'dim', 'center', toggle='units=us'))
W.append(text('speed', (LC[0], LC[1] - 72), 120, 'p_big', '{{speed}}', 'fg', 'right'))
W.append(text('speed_u', (LC[0] + 4, LC[1] - 70), 70, 'p_unit', '{{u:speedLc}}', 'fg', 'left'))
W.append(text('edrive_l', (LC[0] - 118, LC[1] + 34), 70, 'p_unit', 'eDRIVE', 'accent', 'center'))
# ---- the power dial: -20..100 % (the charge sector counts down from the top), 0 at the top
PS, PW = -33.0, 200.0
W.append(dial('pow', RC, R, PS, PW, 'powerPct', -20, 100, 12, 1, [22, 11], [0.98, 44, 7, 8], 24, conn=1))
for v in (10, 20, 40, 60, 80, 100):
    W.append(text('pw%d' % v, pos(RC, LAB, PS + PW * (v + 20) / 120.0), 70, 'p_lab', str(v), 'dim', 'center'))
W.append(arc('chg_arc', RC, R - 70, PS + 4, PW * 20 / 120.0 - 4, 12, 'accent', conn=2))
W.append(arc('edr_arc', RC, 156.0, 276.0, 100.0, 5, 'accent', conn=2))
W.append(text('ready', (RC[0], RC[1] - 232), 120, 'p_row', 'READY', 'fg', 'center'))
W.append(text('edrive_r', (RC[0], RC[1] - 78), 120, 'p_row', 'eDRIVE', 'accent', 'center'))
W.append(text('charge', pos(RC, R - 40, PS + 8), 120, 'p_unit', 'CHARGE', 'accent', 'center'))
W.append(text('power_cap', (RC[0] - 214, RC[1] - 96), 100, 'p_unit', 'POWER %', 'dim', 'center'))
W.append(text('eboost', pos(RC, R - 108, 150.0), 120, 'p_unit', 'eBOOST', 'accent', 'center'))
# ---- the middle: clock, temperature, drive mode logo
W.append({'id': 'clock', 'type': 'aclock', 'class': 'content', 'z': 3, 'x': 881, 'y': 119, 'w': 160, 'h': 160, 'radius': 63, 'tick': [11, 1.4, 6],
          'hands': [255, 96, 52], 'ticks': [244, 246, 250], 'conn': 2, 'toggle': '!mapUp'})
W.append(text('ambient', (961.0, 284.0), 200, 'p_row', '{{ambient}}{{u:temp}}', 'fg', 'center', **hide))
W.append(text('mode_logo', (961.0, 358.0), 200, 'p_row', 'eDrive', 'accent', 'center', **hide))
W.append(text('comfort', (1308.0, 520.0), 140, 'p_unit', '{{mode}}', 'fg', 'center'))
W.append(text('stage', (1424.0, 520.0), 50, 'p_gear', '{{stage}}', 'fg', 'center'))
# ---- the side gauges: fuel (far left) and battery (far right), after the photo's open arcs with inward ticks, a floating radial needle and a curved chrome bracket
K = 1.5                                            # the photo's px -> layout px (its main dials are r~190 px, ours 288)


K2 = 1.3                                           # the side gauges are a little smaller than the main dials' scale so they stay on the screen
FX, FY = 158.0, 478.0                              # the fuel arc's centre on the layout
BX, BY = 1762.0, 478.0                             # the battery arc's centre


def PL(x, y):
    """A photo point of the left side -> the layout."""
    return (FX + (x - 105) * K2, FY + (y - 467.5) * K2)


def PR(x, y):
    """A photo point of the right side -> the layout."""
    return (BX + (x - 1095) * K2, BY + (y - 464) * K2)


def side(i, center, signal, mn, mx, start, sweep, radius, ticks, needle, block=None, fill=None, conn=2):
    size = 330
    x0 = max(0, min(1920 - size, round(center[0] - size / 2)))
    y0 = max(0, min(660 - size, round(center[1] - size / 2)))
    d = {'id': i, 'type': 'eside', 'class': 'content', 'z': 3, 'x': x0, 'y': y0, 'w': size, 'h': size, 'conn': conn,
         'center': [round(center[0], 1), round(center[1], 1)], 'radius': radius, 'half': 1.3, 'start': start, 'sweep': sweep, 'signal': signal, 'min': mn, 'max': mx,
         'needle': needle, 'ticks': ticks}
    if block:
        d['block'] = block
    if fill:
        d['fill'] = fill
    return d


FUEL_C, BATT_C = (FX, FY), (BX, BY)
W.append(side('fuel_side', FUEL_C, 'fuel', 0, 1, 199.0, 122.0, 91.0, {'n': 8, 'every': 4, 'long': 19.0, 'short': 9.5},
              {'inner': 18.0, 'outer': 66.0, 'half': 3.6, 'glow': 4.0}, block=[203.0, 216.0, 72.0, 85.0]))
W.append(side('batt_side', BATT_C, 'hvSoc', 0, 100, 156.0, -116.0, 92.0, {'n': 10, 'every': 5, 'long': 19.0, 'short': 9.5},
              {'inner': 18.0, 'outer': 71.0, 'half': 3.6, 'glow': 4.0}, fill={'inner': 55.0}))


def crescent(pts, tr, tail_in=24.0):
    """The chrome bracket: an outer white line and a dark blue band along its inside, as strips."""
    P = [tr(*p) for p in pts]
    lines = [{'seg': [*P[k], *P[k + 1]], 'color': [226, 232, 248], 'half': 1.5} for k in range(len(P) - 1)]
    polys = []
    n = len(P)
    for k in range(n - 1):
        (x0, y0), (x1, y1) = P[k], P[k + 1]
        def inner(pt, kk):
            # towards the gauge's centre, tapering to zero at both ends
            cx, cy = (FUEL_C if tr is PL else BATT_C)
            dx, dy = cx - pt[0], cy - pt[1]
            L = math.hypot(dx, dy) or 1.0
            w = tail_in * K2 * math.sin(math.pi * kk / (n - 1))
            return (pt[0] + dx / L * w, pt[1] + dy / L * w)
        a0, a1 = inner(P[k], k), inner(P[k + 1], k + 1)
        ys = [y0, y1, a0[1], a1[1]]
        polys.append({'pts': r1([(x0, y0), (x1, y1), a1, a0]), 'top': round(min(ys), 1), 'bottom': round(max(ys), 1),
                      'topColor': [62, 70, 118, 0.9], 'bottomColor': [40, 46, 88, 0.9], 'fade': 0})
    return polys, lines


L_PATH = [(54, 401), (30, 412.5), (16, 430), (10.5, 455), (12, 480), (21, 505), (37.5, 525), (60, 540), (85, 551), (110, 557.5), (135, 560.5), (150, 560)]
R_PATH = [(1148.75, 391), (1170, 400), (1185, 420), (1194, 445), (1191, 470), (1182.5, 495), (1165, 517.5), (1140, 532.5), (1110, 545), (1080, 550.5), (1057.5, 553.75), (1051, 554)]
lp, ll = crescent(L_PATH, PL)
rp, rl = crescent(R_PATH, PR)
W.append({'id': 'brk_l', 'type': 'gpoly', 'class': 'content', 'z': 2, 'x': 0, 'y': 300, 'w': 420, 'h': 360, 'polys': lp[:7], 'lines': ll, 'conn': 3})
W.append({'id': 'brk_r', 'type': 'gpoly', 'class': 'content', 'z': 2, 'x': 1500, 'y': 300, 'w': 420, 'h': 360, 'polys': rp[:7], 'lines': rl, 'conn': 3})
# the labels, placed where the photo has them
W.append(text('fuel_1', PL(77.5, 423.75), 30, 'p_unit', '1', 'fg', 'center'))
W.append(text('fuel_half', PL(69, 470), 50, 'p_unit', '1/2', 'fg', 'center'))
W.append(text('fuel_0', PL(93, 507.5), 30, 'p_unit', '0', 'fg', 'center'))
W.append(text('fuel_km', PL(136, 516), 100, 'p_row', '{{range}}', 'fg', 'center'))
W.append(text('fuel_km_u', PL(144, 535.5), 60, 'p_unit', '{{u:distLc}}', 'dim', 'center'))
W.append({'id': 'fuel_icon', 'type': 'icon', 'icon': 'fuel', 'z': 5, 'x': round(PL(85, 392)[0]) - 12, 'y': round(PL(85, 392)[1]) - 13, 'w': 24, 'h': 26, 'color': 'dim'})
W.append(text('b100', PR(1127, 415), 60, 'p_unit', '100', 'fg', 'center'))
W.append(text('b50', PR(1135, 461), 40, 'p_unit', '50', 'fg', 'center'))
W.append(text('b0', PR(1111, 500), 30, 'p_unit', '0', 'fg', 'center'))
W.append(text('batt_pct', PR(1069, 510), 100, 'p_row', '{{hvSoc}}', 'accent', 'center'))
W.append(text('batt_u', PR(1072, 528), 60, 'p_unit', '%', 'dim', 'center'))
W.append({'id': 'batt_icon', 'type': 'icon', 'icon': 'stack', 'z': 5, 'x': round(PR(1114, 387.5)[0]) - 14, 'y': round(PR(1114, 387.5)[1]) - 10, 'w': 28, 'h': 20, 'color': 'dim'})
# ---- TOTAL / TRIP
W.append(text('total_l', (690.0, 598.0), 90, 'p_unit', 'RANGE', 'dim', 'right'))
W.append(text('total', (700.0, 598.0), 200, 'p_row', '{{range}} {{u:distLc}}', 'fg', 'left'))
W.append(text('trip_l', (1030.0, 598.0), 70, 'p_unit', 'TRIP', 'dim', 'right'))
W.append(text('trip', (1040.0, 598.0), 200, 'p_row', '{{tripDist}} {{u:distLc}}', 'fg', 'left'))
W += [
    {'id': 'strip_cover_l', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 660, 'w': 1380, 'h': 60, 'color': 'bg', 'stripRow': 'l'},
    {'id': 'strip_cover_r', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 1460, 'y': 660, 'w': 460, 'h': 60, 'color': 'bg', 'stripRow': 'r'},
    text('strip_time', (268.0, 690.0), 130, 'p_row', '{{time}}', 'dim', 'right', stripRow='l'),
    text('strip_ampm', (278.0, 693.0), 50, 'p_unit', '{{ampmLc}}', 'dim', 'left', stripRow='l'),
    text('strip_out', (1745.0, 690.0), 100, 'p_row', '{{ambient}}', 'dim', 'right', stripRow='r'),
    text('strip_out_u', (1755.0, 693.0), 40, 'p_unit', '{{u:temp}}', 'dim', 'left', stripRow='r'),
]
L = {'schemaVersion': 2, 'name': 'ePower', 'theme': 'epower', 'packWaste': 3,
     '_about': "ePower cluster, generated by tools/gen_epower.py (edit that and regenerate), after a press photo of a BMW plug-in hybrid cluster (apps/9.jpg): two big round dials on a dark navy face with polished rims, grey-white ticks and numbers and a long red-orange needle (left: the speed, 0..260 km/h or 0..160 mph; right: POWER %, zero at the top, the blue CHARGE sector to its left, 10..100 to its right), a small clock, the outside temperature and the drive mode between them, a fuel dial far left with the range and a battery dial far right, TOTAL / TRIP along the bottom. While the Waze map shows inside the theme the clock, temperature and mode give way to a map window between the dials. Black covers BMW's gauges. Widget reference: shared/hud.js header.",
     'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(L, f, indent=2, ensure_ascii=False)
    f.write('\n')
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import badge_spot; badge_spot.apply(OUT)
print('epower.json:', len(W), 'widgets')
