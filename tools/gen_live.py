#!/usr/bin/env python3
"""Generates apps/ix3_themes/hud/layouts/live.json (the Live Cockpit theme), after a native 1920x720 render of the
cluster (apps/6.png: the blue speed chevron, the red rev chevron, the big speed and gear, the bottom strip) and the photo of
the same cluster (apps/4.jpg, apps/5.jpg: the map in the middle, the small speed and revs while it shows). The shapes come
from tools/live6/measure6.py (render px, tools/live6/measurements.json: the left half; the right half is its mirror about
x = 960), the text from tools/live6/text.json, the rest is read off the render below. Two shader layers per half
(shaders.js LSTRIP, LGAUGE) draw everything but the text. Edit this and regenerate; do not hand-edit the JSON."""
import json, math, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'layouts', 'live.json')
M = json.load(open(os.path.join(ROOT, 'tools', 'live6', 'measurements.json')))
TX = json.load(open(os.path.join(ROOT, 'tools', 'live6', 'text.json')))
FONT_DIR = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'fonts')
H = 660


def mx(x):
    return 1920.0 - x


def mirror(pts):
    return [(mx(x), y) for x, y in pts]


def r1(pts):
    return [[round(x, 1), round(y, 1)] for x, y in pts]


def cell(font):
    return json.load(open(os.path.join(FONT_DIR, font + '.json')))['cellHeight']


def simplify(pts, eps):
    # a closed outline: Douglas-Peucker on both halves
    from math import hypot
    def dp(p, e):
        if len(p) < 3: return p
        (ax, ay), (bx, by) = p[0], p[-1]
        L = hypot(bx - ax, by - ay) or 1e-9
        d = [abs((bx - ax) * (ay - y) - (ax - x) * (by - ay)) / L for x, y in p[1:-1]]
        i = max(range(len(d)), key=lambda k: d[k])
        if d[i] > e:
            l = dp(p[:i + 2], e); r = dp(p[i + 1:], e)
            return l[:-1] + r
        return [p[0], p[-1]]
    n = len(pts)
    far = max(range(n), key=lambda k: hypot(pts[k][0] - pts[0][0], pts[k][1] - pts[0][1]))
    a = dp(pts[:far + 1], eps); b = dp(pts[far:] + [pts[0]], eps)
    return a[:-1] + b[:-1]


# ---------------- the left half (render px), mirrored for the right
OUTER = [tuple(p) for p in M['leftOuter']]
INNER = [tuple(p) for p in M['leftInner']]
BAND = simplify([tuple(p) for p in M['leftBand']], 2.4)
BAND_Y = (125.0, 605.0)
TICKS_L = [(266, 153.5, 279), (234, 208.5, 247), (203, 263.5, 216), (188, 318.5, 199), (220, 373.5, 234), (260, 428.5, 275),
           (302, 483.5, 317), (344, 538.5, 359), (387, 593.5, 402)]
TICKS_R = [(1517, 593.5, 1532), (1566, 530.5, 1581), (1614, 467.5, 1629), (1661, 405.0, 1677), (1707, 342.0, 1721), (1712, 279.5, 1724),
           (1676, 216.5, 1690), (1640, 154.0, 1652)]
SCALE_US = [[0, 593.5], [20, 538.5], [40, 483.5], [60, 428.5], [80, 373.5], [100, 318.5], [120, 263.5], [160, 208.5], [200, 153.5]]
SCALE_KMH = [[0, 593.5], [40, 538.5], [80, 483.5], [120, 428.5], [160, 373.5], [200, 318.5], [240, 263.5], [280, 208.5], [320, 153.5]]
SCALE_RPM = [[0, 593.5], [1, 531.0], [2, 468.0], [3, 405.0], [4, 342.0], [5, 279.5], [6, 217.0], [7, 154.5]]
MARKS_R = [{'seg': [1645.0, 149.0, 1666.0, 181.5], 'color': [255, 51, 51], 'half': 3.0},
           {'seg': [1670.5, 197.0, 1677.5, 193.0], 'color': [255, 217, 26], 'half': 2.4},
           {'seg': [1680.0, 213.0, 1687.0, 209.0], 'color': [255, 217, 26], 'half': 2.4},
           {'seg': [1689.0, 227.5, 1694.5, 224.0], 'color': [255, 217, 26], 'half': 2.4}]


def gauge(name, side):
    left = side == 'left'
    outer = OUTER if left else mirror(OUTER)
    inner = INNER if left else mirror(INNER)
    band = BAND if left else mirror(BAND)
    ticks = [(a, y, a, y) for a, y, b in TICKS_L] if False else None
    t = [[a, y, b, y] for a, y, b in (TICKS_L if left else TICKS_R)]
    if left:
        bar = {'top': (309.5, 359.4), 'bottom': (445.0, 539.7), 'radius': 6.6, 'coldFrac': 0.0, 'thinOffset': -9.0,
               'track': [83, 87, 101], 'cold': [64, 128, 255], 'thin': [102, 106, 118], 'signal': 'fuel', 'min': 0, 'max': 1}
    else:
        bar = {'top': (1609.5, 359.4), 'bottom': (1471.0, 544.7), 'radius': 6.6, 'coldFrac': 0.115, 'thinOffset': 9.0,
               'track': [83, 87, 101], 'cold': [64, 128, 255], 'thin': [102, 106, 118], 'signal': 'oil', 'min': 49, 'max': 149}
    return {'id': name, 'type': 'lgauge', 'class': 'content', 'z': 1, 'x': 0 if left else 960, 'y': 0, 'w': 960, 'h': H,
            'quantity': 'speed' if left else 'rpm',
            'outer': r1(outer), 'inner': r1(inner), 'band': r1(band), 'ticks': r1([(a, y) for a, y, _, _ in t]) if False else [[round(v, 1) for v in s] for s in t],
            'marks': [] if left else MARKS_R, 'bandY': list(BAND_Y),
            'outerColor': [92, 158, 255] if left else [242, 31, 41], 'innerColor': [48, 109, 237] if left else [242, 31, 41],
            'unlit': [32, 73, 191] if left else [81, 15, 24],
            'lit': [[190, 232, 252], [136, 180, 205]] if left else [[232, 54, 64], [184, 38, 46]],
            'lineW': [1.5, 1.0], 'glow': [7.0, 0.28],
            'scale': {'us': SCALE_US, 'metric': SCALE_KMH} if left else SCALE_RPM,
            'bar': {'top': [round(v, 1) for v in bar['top']], 'bottom': [round(v, 1) for v in bar['bottom']], 'radius': bar['radius'],
                    'coldFrac': bar['coldFrac'], 'thinOffset': bar['thinOffset'], 'track': bar['track'], 'cold': bar['cold'], 'thin': bar['thin'],
                    'signal': bar['signal'], 'min': bar['min'], 'max': bar['max']}}


W = []


def text(i, c, w, font, t, color='fg', align='center', **kw):
    h = cell(font)
    d = {'id': i, 'type': 'text', 'z': 5, 'x': round(c[0] - w / 2), 'y': round(c[1] - h / 2), 'w': w, 'h': h, 'text': t, 'font': font,
         'color': color, 'align': align}
    d.update(kw)
    return d


def at(i, key, w, font, t, color, edge, **kw):
    """Text anchored on a blob's right ('r') or left ('l') edge, centred on its height."""
    v = TX[key]
    cy = (v[1] + v[3]) / 2.0
    h = cell(font)
    x = v[2] - w + 1 if edge == 'r' else v[0]
    d = {'id': i, 'type': 'text', 'z': 5, 'x': round(x), 'y': round(cy - h / 2), 'w': w, 'h': h, 'text': t, 'font': font,
         'color': color, 'align': 'right' if edge == 'r' else 'left'}
    d.update(kw)
    return d


def ctr(key, fb=None):
    v = TX.get(key)
    return fb if not v else ((v[0] + v[2]) / 2.0, (v[1] + v[3]) / 2.0)


# the map window of the photo (a parallelogram; the render has the road there instead), mapped onto the 1920x720 render
MAP = [(612, 112), (1308, 112), (1198, 590), (722, 590), (612, 112)]
MAP = [(645, 145), (1235, 145), (1318, 590), (565, 590)]
STRIP = [(447, 625), (1472, 625), (1494, 653), (425, 653)]
DIV = [(461 + 150 * k, 626, 451 + 150 * k, 652) for k in range(7) if k != 3]
xs = [p[0] for p in MAP]; ys = [p[1] for p in MAP]
W.append({'id': 'lstrip', 'type': 'lstrip', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': H,
          'win': r1(MAP), 'strip': r1(STRIP), 'dividers': [[float(v) for v in d] for d in DIV],
          'blue': [[20, 46, 118], [19, 45, 117]], 'red': [[100, 15, 28], [58, 11, 23]],
          'stripY': [625, 653], 'stripMid': 960, 'bottomLine': [384, 1536, 603.5, 1.2],
          'bottomColors': [[73, 126, 204], [194, 24, 33]], 'dividerColors': [[36, 86, 220], [148, 18, 31]],
          'hole': [min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)], 'holeWhen': 'mapUp', 'holeInset': 0})
W.append(gauge('lgauge_l', 'left'))
W.append(gauge('lgauge_r', 'right'))

# ---- the numbers on the scales
LAB_US = ['200', '160', '120', '100', '80', '60', '40', '20', '0']
LAB_KMH = ['320', '280', '240', '200', '160', '120', '80', '40', '0']
LAB_KEYS = ['L200', 'L160', 'L120', 'L100', 'L80', 'L60', 'L40', 'L20', 'L0']
for k, key in enumerate(LAB_KEYS):
    c = ctr(key)
    idx = 8 - k        # the label's index from the bottom (0) up
    W.append(text('spd_us%d' % k, c, 110, 'l_lab', LAB_US[k], 'lblue', 'center', spacing=5.5, toggle='units=us', near=['speed9', idx], nearColor='fg'))
    W.append(text('spd_km%d' % k, c, 110, 'l_lab', LAB_KMH[k], 'lblue', 'center', spacing=5.5, toggle='!units=us', near=['speed9', idx], nearColor='fg'))
for k in range(8):
    key = 'R%d' % (7 - k)
    W.append(text('rpm%d' % (7 - k), ctr(key), 40, 'l_lab', str(7 - k), 'pink', 'center', near=['rpm', 7 - k], nearColor='fg'))
W.append(text('mph_top', ctr('mph_top'), 90, 'l_unit', '{{u:speedLc}}', 'lblue', 'center'))
W.append(text('rpm_top', (1543.0, 100.0), 220, 'l_unit', '1/min x 1000', 'red', 'center'))
# ---- the big speed and gear (the render's view); the small ones while the Waze map shows (the photo's view)
W.append(text('speed', (956.5, 215.0), 280, 'l_big', '{{speed}}', 'fg', 'center', spacing=27, toggle='!mapUp'))
W.append(text('speed_unit', ctr('mph_mid'), 90, 'l_unit', '{{u:speedLc}}', 'lblue', 'center', toggle='!mapUp'))
W.append(text('gear', (893.0, 394.5), 110, 'l_gear', '{{gearnum}}', 'fg', 'center', toggle='!mapUp'))
# the photo's view while the map shows: the speed moves into the left chevron and the revs (thousands) into the right one
W.append(text('mspeed', (534.0, 328.0), 240, 'l_mid', '{{speed}}', 'fg', 'center', spacing=20, toggle='mapUp'))
W.append(text('mspeed_u', (528.0, 384.0), 90, 'l_unit', '{{u:speedLc}}', 'fg', 'center', toggle='mapUp'))
W.append(text('mrevs', (1427.0, 328.0), 260, 'l_mid', '{{revK}}', 'fg', 'center', spacing=10, toggle='mapUp'))
W.append(text('mrevs_u', (1425.0, 384.0), 200, 'l_unit', '1/min x1000', 'fg', 'center', toggle='mapUp'))
# ---- the bars' labels
W.append(text('fuel_1', ctr('fuel1'), 24, 'l_bar', '1', 'fg', 'center'))
W.append(text('fuel_0', ctr('fuel0'), 24, 'l_bar', '0', 'fg', 'center'))
W.append(text('oil_hi', ctr('oil300'), 90, 'l_bar', '{{oilHi}}', 'fg', 'center'))
W.append(text('oil_lo', ctr('oil120'), 90, 'l_bar', '{{oilLo}}', 'fg', 'center'))
# ---- the strip's readouts and the bottom row (anchored on the render's text edges)
W.append(at('psi', 'psi_val', 120, 'l_row', '{{tyreAvg}}', 'fg', 'r'))
W.append(text('psi_u', (847.0 + 20, 640.0), 60, 'l_unit', '{{u:pressure}}', 'fg', 'left'))
W[-1]['x'] = 847
W.append(at('temp', 'temp_val', 120, 'l_row', '{{coolant}}', 'fg', 'r'))
W.append(text('temp_u', (1117.0 + 20, 640.0), 50, 'l_unit', '{{u:temp}}', 'fg', 'left'))
W[-1]['x'] = 1117
W.append({'id': 'strip_cover_l', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 660, 'w': 1380, 'h': 60, 'color': 'bg', 'stripRow': 'l'})
W.append({'id': 'strip_cover_r', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 1460, 'y': 660, 'w': 460, 'h': 60, 'color': 'bg', 'stripRow': 'r'})
W.append(at('strip_time', 'time', 130, 'l_row', '{{time}}', 'fg', 'r', stripRow='l'))
W.append(at('strip_ampm', 'ampm', 50, 'l_unit', '{{ampmLc}}', 'lgrey', 'l', stripRow='l'))
W.append(at('strip_range', 'odo', 110, 'l_row', '{{range}}', 'fg', 'r', stripRow='l'))
W.append(at('strip_range_u', 'mi', 40, 'l_unit', '{{u:distLc}}', 'lgrey', 'l', stripRow='l'))
W.append(at('strip_out', 'out', 110, 'l_row', '{{ambient}}', 'fg', 'r', stripRow='r'))
W.append(at('strip_out_u', 'degf', 40, 'l_unit', '{{u:temp}}', 'lgrey', 'l', stripRow='r'))
W.append(text('stage', (1175.0, 690.0), 30, 'l_row', '{{stage}}', 'fg', 'center', stripRow='l'))
W.append(text('mode', (1275.0, 690.0), 170, 'l_unit', '{{mode}}', 'amber', 'center', stripRow='l'))
W.append({'id': 'fuel_icon', 'type': 'icon', 'icon': 'fuel', 'z': 5, 'x': 407, 'y': 441, 'w': 22, 'h': 26, 'color': 'lgrey'})
W.append({'id': 'oil_icon', 'type': 'icon', 'icon': 'oilcan', 'z': 5, 'x': 1488, 'y': 444, 'w': 28, 'h': 18, 'color': 'lgrey'})

L = {'schemaVersion': 2, 'name': 'Live Cockpit', 'theme': 'live', 'mapLive': False,
     '_about': "Live Cockpit cluster, generated by tools/gen_live.py (edit that and regenerate), after a native 1920x720 render of the cluster (apps/6.png, traced by tools/live6/) and a photo of it (apps/4.jpg, apps/5.jpg): the blue speed chevron (a bright line, a thin inner line, a band lit from the bottom up to the speed with a white cut line, ticks at the numbers 0 to 200 mph, the fuel bar) and the red rev chevron (0 to 7, red marks at the top, the oil temperature bar), the big speed and gear, the blue / red strip along the bottom with the tyre pressure and engine temperature, the clock, range and outside temperature, and an empty middle: the Waze map opens there while 'Show Waze map inside the theme' is on (then the speed shows small, as in the photo). Black covers BMW's gauges. Widget reference: shared/hud.js header.",
     'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(L, f, indent=2, ensure_ascii=False)
    f.write('\n')
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import badge_spot; badge_spot.apply(OUT)
print('live.json:', len(W), 'widgets; band', len(BAND), 'pts')
