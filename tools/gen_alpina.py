#!/usr/bin/env python3
"""Generates apps/ix3_themes/hud/layouts/alpina.json (the Alpina theme), after a photo of the Alpina cluster
(apps/1.png). Every shape below is measured off that photo in CROP coordinates (the photo cropped to the cluster and
enlarged 4x: x 0..1600, y 0..660) and mapped onto the 1920x660 layer by T(). One aview shader layer (shaders.js
ALPINA) draws everything but the text. Edit this and regenerate; do not hand-edit the JSON."""
import json, math, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'layouts', 'alpina.json')

K = 1.22                      # crop px -> layer px
CX0, CY0 = 808, 61            # the photo's centre line and the top line
LX0, LY0 = 960, 42            # where they land on the layer


def T(x, y):
    return ((x - CX0) * K + LX0, (y - CY0) * K + LY0)


def Tp(pts):
    return [T(*p) for p in pts]


def mirror_x(x):
    return 2 * CX0 - x


# ---- the left scale's line (crop px), bottom end to top end: bottom corner, the tip, the top corner, the top line's end
BOT, TIP, TOPC, TOPE = (253, 537), (59, 250), (217, 61), (420, 61)


def unit(a, b):
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    return ((b[0] - a[0]) / d, (b[1] - a[1]) / d)


def round_corner(a, v, b, r):
    i, o = unit(a, v), unit(v, b)
    pa = (v[0] - i[0] * r, v[1] - i[1] * r)
    pb = (v[0] + o[0] * r, v[1] + o[1] * r)
    pm = (0.25 * pa[0] + 0.5 * v[0] + 0.25 * pb[0], 0.25 * pa[1] + 0.5 * v[1] + 0.25 * pb[1])
    return [pa, pm, pb]


path_c = [(253, 537)]
path_c += round_corner(BOT, TIP, TOPC, 26)
path_c += round_corner(TIP, TOPC, TOPE, 14)
path_c += [TOPE]
# the bottom corner is nearly sharp: start the line a little up the leg
path = Tp(path_c)
cum = [0.0]
for i in range(1, len(path)):
    cum.append(cum[-1] + math.hypot(path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]))
# the arc length of the top corner (after its rounding)
corner_arc = cum[len(path) - 2]


def arc_at_y(y_crop):
    """Arc length of the line where it crosses the crop row y (the first crossing from the bottom)."""
    y = T(0, y_crop)[1]
    for i in range(len(path) - 1):
        (x0, y0), (x1, y1) = path[i], path[i + 1]
        if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
            t = (y - y0) / (y1 - y0)
            return cum[i] + t * (cum[i + 1] - cum[i])
    return cum[-1]


# ---- the numbers: crop y of each white mark (0 = bottom end, 7 = the top)
TICK_Y_L = [538, 467, 395, 323, 250, 190, 127, 66]
TICK_Y_R = [538, 475, 403, 330, 255, 203, 150, 100]
ticks_l = [round(arc_at_y(y), 1) for y in TICK_Y_L]
ticks_r = [round(arc_at_y(y), 1) for y in TICK_Y_R]
ticks_l[0] = ticks_r[0] = 0.0
ticks_l[7] = round(corner_arc, 1)
ticks_r[7] = round(min(corner_arc - 10, ticks_r[7]), 1)

# the numbers' centres (crop px)
LAB_L = [(325, 523), (295, 462), (250, 392), (212, 327), (186, 258), (240, 196), (292, 138), (340, 83)]
LAB_R = [(1279, 528), (1319, 471), (1359, 399), (1405, 330), (1430, 265), (1388, 213), (1347, 160), (1300, 107)]

# ---- the shapes (crop px)
NAVY = [(150, 61), (420, 61), (398, 101), (306, 213), (227, 300), (363, 505), (363, 540), (150, 540)]
# both glass panels as one convex shape (the divider line under the speed splits it)
PANEL = [(227, 300), (398, 101), (430, 101), (645, 395), (640, 420), (603, 505), (363, 505)]
LINE1 = (400, 101, 227, 300)
LINE2 = (306, 213, 497, 505)
BOTTOM = (253, 540, 705)
RADIUS = 26.0         # corner radius in layer px


def inset(poly, r):
    """Inset a convex polygon by r (layer px): the shader draws it grown by r again, with round corners."""
    def area(p):
        return abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))) / 2

    def build(sgn):
        n = len(poly)
        lines = []
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            dx, dy = unit(a, b)
            nx, ny = -dy * sgn, dx * sgn
            lines.append(((a[0] + nx * r, a[1] + ny * r), (dx, dy)))
        out = []
        for i in range(n):
            (p1, d1), (p2, d2) = lines[i - 1], lines[i]
            den = d1[0] * d2[1] - d1[1] * d2[0]
            t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
            out.append((p1[0] + d1[0] * t, p1[1] + d1[1] * t))
        return out
    a, b = build(1), build(-1)
    return a if area(a) < area(b) else b


def r2(pts):
    return [[round(x, 1), round(y, 1)] for x, y in pts]


W = []


def text(i, c, w, h, t, font, color='fg', align='center', **kw):
    """A text widget centred on crop point c."""
    x, y = T(*c)
    d = {'id': i, 'type': 'text', 'z': 5, 'x': round(x - w / 2), 'y': round(y - h / 2), 'w': w, 'h': h, 'text': t, 'font': font,
         'color': color, 'align': align}
    d.update(kw)
    return d


band = 82
shapes = {
    'id': 'aview', 'type': 'aview', 'class': 'content', 'z': 1, 'x': 0, 'y': 0, 'w': 1920, 'h': 660,
    'path': r2(path), 'band': band, 'cornerArc': round(corner_arc, 1), 'thinX': round(T(303, 0)[0], 1), 'topY': round(T(0, 61)[1], 1),
    'ticksL': ticks_l, 'ticksR': ticks_r,
    'labelsL': r2(Tp(LAB_L)), 'labelsR': r2([T(mirror_x(x), y) for x, y in LAB_R]),
    'navy': r2(Tp(NAVY)),
    'panel': r2(inset(Tp(PANEL), RADIUS)), 'panelRadius': round(RADIUS, 1),
    'line1': [round(v, 1) for v in (*T(LINE1[0], LINE1[1]), *T(LINE1[2], LINE1[3]))],
    'line2': [round(v, 1) for v in (*T(LINE2[0], LINE2[1]), *T(LINE2[2], LINE2[3]))],
    'bottom': [round(T(BOTTOM[0], 0)[0], 1), round(T(0, BOTTOM[1])[1], 1), round(T(BOTTOM[2], 0)[0], 1)],
    'needle': [47, 180],
    'mark': [960, round(T(0, 160)[1], 1), 42],
    'hole': [740, 90, 440, 540], 'holeWhen': 'mapUp', 'holeInset': 0, 'holeOval': 70,
    'halo': [round(T(408, 0)[0], 1), round(T(0, 275)[1], 1), 105, 72],
    'speedSteps': {'metric': [0, 30, 60, 90, 150, 210, 270, 340], 'us': [0, 20, 40, 60, 90, 130, 170, 210]},
}
W.append(shapes)

SPD_KM = ['0', '30', '60', '90', '150', '210', '270', '340']
SPD_US = ['0', '20', '40', '60', '90', '130', '170', '210']
for k in range(8):
    c = LAB_L[k]
    if k == 7:
        c = (338, 83)
    W.append(text('spd_km%d' % k, c, 110, 34, SPD_KM[k], 'a_num', toggle='!units=us'))
    W.append(text('spd_us%d' % k, c, 110, 34, SPD_US[k], 'a_num', toggle='units=us'))
for k in range(8):
    # the rev numbers mirror the left ones' x positions, as the shader mirrors the line
    W.append(text('rpm%d' % k, (mirror_x(mirror_x(LAB_R[k][0])), LAB_R[k][1]), 110, 34, str(k), 'a_num'))
# the units over the scales
W.append(text('scale_unit', (408, 85), 100, 33, '{{u:speedLc}}', 'a_unit', 'fg', 'left', **{}))
W.append(text('rpm_unit', (1190, 92), 190, 33, '1/min x1000', 'a_unit', 'fg', 'right'))
# the big speed and gear
W.append({'id': 'speed', 'type': 'text', 'z': 5, 'x': round(T(437, 0)[0]) - 240 + 8, 'y': round(T(0, 275)[1]) - 45, 'w': 240, 'h': 90,
          'text': '{{speed}}', 'font': 'a_big', 'color': 'fg', 'align': 'right'})
W.append({'id': 'speed_unit', 'type': 'text', 'z': 5, 'x': round(T(441, 0)[0]) + 10, 'y': round(T(0, 296)[1]) - 14, 'w': 100, 'h': 33,
          'text': '{{u:speedLc}}', 'font': 'a_unit', 'color': 'fg', 'align': 'left'})
W.append(text('gear', (1212, 277), 160, 90, '{{gearnum}}', 'a_big', 'fg', 'center', hotWhen='now'))
W.append(text('mode', (1212, 340), 220, 33, '{{mode}}', 'a_unit', 'dim', 'center'))
# the wordmark is drawn by the shader (aview 'mark')
# the bottom row: range, clock, outside temperature
W += [
    {'id': 'strip_cover_l', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 660, 'w': 1380, 'h': 60, 'color': 'bg', 'stripRow': 'l'},
    {'id': 'strip_cover_r', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 1460, 'y': 660, 'w': 460, 'h': 60, 'color': 'bg', 'stripRow': 'r'},
]
rx, ry = T(110, 565)
W.append({'id': 'strip_range', 'type': 'text', 'z': 3, 'x': round(rx), 'y': 650, 'w': 80, 'h': 26, 'text': '{{range}}', 'font': 'a_val',
          'color': 'fg', 'align': 'right', 'stripRow': 'l'})
W.append({'id': 'strip_range_u', 'type': 'text', 'z': 3, 'x': round(rx) + 86, 'y': 650, 'w': 40, 'h': 29, 'text': '{{u:distLc}}', 'font': 'a_unit',
          'color': 'fg', 'align': 'left', 'stripRow': 'l'})
tx, ty = T(280, 590)
W.append({'id': 'strip_time', 'type': 'text', 'z': 3, 'x': round(tx), 'y': 684, 'w': 110, 'h': 26, 'text': '{{time}}', 'font': 'a_val',
          'color': 'fg', 'align': 'left', 'stripRow': 'l'})
ox, oy = T(1230, 597)
W.append({'id': 'strip_out', 'type': 'text', 'z': 3, 'x': round(ox), 'y': 692, 'w': 100, 'h': 26, 'text': '{{ambient}}', 'font': 'a_val',
          'color': 'fg', 'align': 'right', 'stripRow': 'r'})
W.append({'id': 'strip_out_u', 'type': 'text', 'z': 3, 'x': round(ox) + 106, 'y': 690, 'w': 30, 'h': 29, 'text': '{{u:temp}}', 'font': 'a_unit',
          'color': 'fg', 'align': 'left', 'stripRow': 'r'})

L = {'schemaVersion': 2, 'name': 'Alpina', 'theme': 'alpina', 'mapLive': True,
     '_about': "Alpina cluster, generated by tools/gen_alpina.py (edit that and regenerate), after a photo of the Alpina cluster (apps/1.png): a white chevron line left (speed, 0 to 340 km/h) and right (revs, 0 to 7, red from the redline) with a light blue hatched band and white marks, the numbers on dark backings, two blue glass panels cut by black lines with the speed on the left and the gear on the right, the ALPINA wordmark between, a red needle across each band and the bottom line with its blue glow. While the Waze map shows inside the theme, an oval between the panels is cut see-through for it (and the wordmark goes), opened and closed without a rebuild. Everything that isn't text is one shader (aview). Black covers BMW's gauges. Widget reference: shared/hud.js header.",
     'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(L, f, indent=2, ensure_ascii=False)
    f.write('\n')
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import badge_spot; badge_spot.apply(OUT)
print('alpina.json:', len(W), 'widgets; ticks L', ticks_l, 'R', ticks_r, 'cornerArc', round(corner_arc, 1), 'path pts', len(path))
