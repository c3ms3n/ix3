#!/usr/bin/env python3
"""Generates apps/kurdbimmer_themes/hud/layouts/concept.json (the Concept theme), after a photo of BMW's Concept 8 Series
cluster (apps/3.jpg). The shapes come from tools/concept/measure.py (traced off the photo into
tools/concept/measurements.json, photo px) and a few hand-read positions below; T() maps photo px onto the 1920x660
layer. Shader layers draw everything but the text: CMAP, and per gauge CVIEW cut into three layers for the iX3 (shaders.js
CVIEW_LINE, CVIEW_PANEL, CVIEW_MINI: the whole gauge in one shader restarted its head unit). Edit this and regenerate;
do not hand-edit the JSON."""
import json, math, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'layouts', 'concept.json')
M = json.load(open(os.path.join(ROOT, 'tools', 'concept', 'measurements.json')))
TX = json.load(open(os.path.join(ROOT, 'tools', 'concept', 'text.json')))        # white text blobs (photo px bounding boxes)
ST = json.load(open(os.path.join(ROOT, 'tools', 'concept', 'stars_fit.json')))   # the star lattice, per half

S = 1.62                  # photo px -> layer px
CX = M['cx']              # the photo's centre line (the right half is the left one mirrored)
Y0 = 30.0                 # where the photo's top line (y 372) lands


def T(x, y):
    return ((x - CX) * S + 960.0, (y - 372.0) * S + Y0)


def Tp(pts):
    return [T(*p) for p in pts]


def mir(x):
    return 2 * CX - x


def cumulative(pts):
    c = [0.0]
    for i in range(1, len(pts)):
        c.append(c[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
    return c


def near(path, cum, x, y):
    best = 1e9; bs = 0.0
    for i in range(len(path) - 1):
        ax, ay = path[i]; bx, by = path[i + 1]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        h = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (L * L)))
        d = math.hypot(x - (ax + dx * h), y - (ay + dy * h))
        if d < best:
            best = d; bs = cum[i] + h * L
    return bs


def side_data(name):
    d = M[name]
    return [tuple(p) for p in d['outer']], d['outerCum'], [tuple(p) for p in d['mini']], d['miniCum'], d['swoosh'], d['miniBand']


# ---- the numbers (photo px): text, centre
SPEED = [('0', 462, 712), ('10', 427, 710), ('20', 400, 691), ('30', 381, 662), ('40', 360, 626), ('50', 339, 591),
         ('60', 326, 559), ('80', 352, 522), ('100', 387, 488), ('120', 423, 459), ('140', 466, 432), ('180', 525, 416),
         ('220', 592, 409), ('260', 661, 403)]
SPEED_US = ['0', '5', '10', '15', '25', '30', '40', '50', '60', '75', '90', '110', '135', '160']
SPEED_KMH = [int(t) for t, _, _ in SPEED]
SPEED_MPH = [int(t) for t in SPEED_US]
REVS = [('0', 1141, 711), ('1', 1211, 691), ('2', 1254, 621), ('3', 1277, 552), ('4', 1241, 495), ('5', 1165, 435),
        ('6', 1081, 416), ('7', 988, 405)]


def marks(arcs):
    """A bright mark at each number, a faint one half way between (a negative arc length)."""
    o = []
    for i, a in enumerate(arcs):
        o.append(round(a * S, 1))
        if i + 1 < len(arcs):
            o.append(-round((a + arcs[i + 1]) / 2 * S, 1))
    return o


# the panel's outline (photo px), left half; the right half starts as its mirror
PANEL_L = [(337, 540), (352, 525), (367, 512), (397, 485), (430, 458), (450, 446), (470, 438), (520, 431), (560, 426),
           (600, 421), (630, 419), (634, 423), (628, 430), (600, 433), (570, 438), (558, 442), (545, 456), (535, 471),
           (520, 492), (500, 516), (484, 545), (471, 563), (472, 578), (480, 592), (492, 610), (502, 640), (515, 675),
           (527, 705), (440, 702), (395, 690), (375, 670), (358, 640), (345, 607), (334, 575), (333, 555)]
PANEL_R = [(mir(x), y) for x, y in PANEL_L]


def r1(pts):
    return [[round(x, 1), round(y, 1)] for x, y in pts]


def gauge(name, side):
    outer, cum, mini, mcum, sw, mb = side_data(side)
    total = cum[-1]
    labels = SPEED if side == 'left' else REVS
    arcs = [near(outer, cum, x, y) for _, x, y in labels]
    band = [[round(s_ * S, 1), round(a * S, 1), round(b * S, 1)] for s_, a, b in sw[:12]]
    mini_band = [[round(s_ * S, 1), round(a * S, 1), round(b * S, 1)] for s_, a, b in mb[::2]][:14]
    mini_arcs = [mini_band[0][0], mini_band[-1][0]]
    x0 = 0 if side == 'left' else 960
    d = {'id': name, 'type': 'cview', 'class': 'content', 'z': 1, 'x': x0, 'y': 0, 'w': 960, 'h': 660,
         'flip': 1 if side == 'left' else -1, 'quantity': 'speed' if side == 'left' else 'rpm',
         'path': r1(Tp(outer)),
         'lineW': [[0.0, round(1.8 * S, 1)], [round(0.30 * total * S, 1), round(3.4 * S, 1)], [round(0.62 * total * S, 1), round(3.2 * S, 1)],
                   [round(total * S, 1), round(1.6 * S, 1)]],
         'ticks': marks(arcs), 'swoosh': band, 'panel': r1(Tp(PANEL_L if side == 'left' else PANEL_R)),
         'mini': r1(Tp(mini)), 'miniBand': mini_band, 'miniArcs': mini_arcs,
         'underline': [round(T(457 if side == 'left' else 945, 0)[0], 1), round(T(660 if side == 'left' else 1150, 0)[0], 1), round(T(0, 593.5)[1], 1), 1.6],
         'star': [round(ST[side]['pitch'][0] * S, 2), round(ST[side]['pitch'][1] * S, 2), round(ST[side]['second'][0] * S, 2), round(ST[side]['second'][1] * S, 2)],
         'starOrigin': [round(v, 2) for v in T(*ST[side]['origin'])],
         'steps': {'metric': SPEED_KMH, 'us': SPEED_MPH} if side == 'left' else list(range(8)),
         'arcs': [round(a * S, 1) for a in arcs]}
    return parts(d, x0)


def crop(pts, pad, x0):
    """The layer rect (x, y, w, h) round pts plus pad, inside the gauge's half of the layer."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    l, t = max(x0, math.floor(min(xs) - pad)), max(0, math.floor(min(ys) - pad))
    r, b = min(x0 + 960, math.ceil(max(xs) + pad)), min(660, math.ceil(max(ys) + pad))
    return {'x': l, 'y': t, 'w': r - l, 'h': b - t}


def parts(d, x0):
    """One cview's data as its three layers (hud.js CVIEW_TYPES): the panel, the line with the swoosh, the little gauge."""
    sfx = d['id'][-2:]
    depth = max(max(abs(e[1]), abs(e[2])) for e in d['miniBand'])
    pick = lambda keys: {k: d[k] for k in keys}
    panel = {'id': 'cpanel' + sfx, 'type': 'cpanel', 'class': 'content', 'z': 1, **crop(d['panel'], 4, x0), **pick(['panel', 'star', 'starOrigin'])}
    line = {'id': 'cline' + sfx, 'type': 'cline', 'class': 'content', 'z': 2, 'x': x0, 'y': 0, 'w': 960, 'h': 660,
            **pick(['flip', 'quantity', 'path', 'lineW', 'ticks', 'swoosh', 'underline', 'steps', 'arcs'])}
    mini = {'id': 'cmini' + sfx, 'type': 'cmini', 'class': 'content', 'z': 2, **crop(d['mini'], 40 + depth, x0), **pick(['flip', 'quantity', 'mini', 'miniBand', 'miniArcs'])}
    return [panel, line, mini]


W = []


def text(i, c, w, h, t, font, color='fg', align='center', **kw):
    x, y = T(*c)
    d = {'id': i, 'type': 'text', 'z': 5, 'x': round(x - w / 2), 'y': round(y - h / 2), 'w': w, 'h': h, 'text': t, 'font': font,
         'color': color, 'align': align}
    d.update(kw)
    return d


r1 = lambda pts: [[round(x, 1), round(y, 1)] for x, y in pts]
HOLE = [560, 150, 800, 470]
W.append({'id': 'cmap', 'type': 'cmap', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 660,
          'bars': [[round(v, 1) for v in (*T(a, b), *T(c, d))] for a, b, c, d in [(946, 378, 968, 383), (972, 380, 988, 385), (992, 382, 1008, 387), (1010, 383, 1022, 388), (1024, 385, 1036, 390)]],
          'hole': HOLE, 'holeWhen': 'mapUp', 'holeInset': 0, 'holeOval': 90})
W.extend(gauge('_l', 'left'))
W.extend(gauge('_r', 'right'))
# the numbers, speed, mode and gear: placed on the white blobs found in the photo (tools/concept/measure_text.py)
FONT_DIR = os.path.join(ROOT, 'apps', 'kurdbimmer_themes', 'hud', 'fonts')


def cell(font):
    return json.load(open(os.path.join(FONT_DIR, font + '.json')))['cellHeight']


def blob_c(key, fallback):
    v = TX.get(key)
    if v and (v[3] - v[1]) < 26:
        return ((v[0] + v[2]) / 2.0, (v[1] + v[3]) / 2.0)
    return fallback


for k, (t, x, y) in enumerate(SPEED):
    c = blob_c('speed_' + t, (x, y))
    W.append(text('spd_km%d' % k, c, 100, cell('k_num'), t, 'k_num', toggle='!units=us'))
    W.append(text('spd_us%d' % k, c, 100, cell('k_num'), SPEED_US[k], 'k_num', toggle='units=us'))
for k, (t, x, y) in enumerate(REVS):
    W.append(text('rpm%d' % k, blob_c('rpm_' + t, (x, y)), 60, cell('k_num'), t, 'k_num'))
b40, bk, bc, bd = TX['big_40'], TX['kmh'], TX['comfort'], TX['gear_D']
W.append({'id': 'speed', 'type': 'text', 'z': 5, 'x': round(T(b40[2], 0)[0]) - 260 + 4, 'y': round(T(0, (b40[1] + b40[3]) / 2)[1]) - cell('k_speed') // 2,
          'w': 260, 'h': cell('k_speed'), 'text': '{{speed}}', 'font': 'k_speed', 'color': 'fg', 'align': 'right', 'spacing': 0})
W.append({'id': 'speed_unit', 'type': 'text', 'z': 5, 'x': round(T(bk[0], 0)[0]), 'y': round(T(0, (bk[1] + bk[3]) / 2)[1]) - cell('k_unit') // 2,
          'w': 120, 'h': cell('k_unit'), 'text': '{{u:speedLc}}', 'font': 'k_unit', 'color': 'fg', 'align': 'left'})
W.append({'id': 'mode', 'type': 'text', 'z': 5, 'x': round(T(bc[0], 0)[0]), 'y': round(T(0, (bc[1] + bc[3]) / 2)[1]) - cell('k_unit') // 2,
          'w': 240, 'h': cell('k_unit'), 'text': '{{mode}}', 'font': 'k_unit', 'color': 'fg', 'align': 'left'})
W.append({'id': 'gear', 'type': 'text', 'z': 5, 'x': round(T((bd[0] + bd[2]) / 2, 0)[0]) - 80, 'y': round(T(0, (bd[1] + bd[3]) / 2)[1]) - cell('k_gear') // 2,
          'w': 160, 'h': cell('k_gear'), 'text': '{{stage}}', 'font': 'k_gear', 'color': 'fg', 'align': 'center'})
W.append(text('rpm_unit', (1106, 706), 120, cell('k_small'), '1/min', 'k_small', 'fg', 'center'))
W.append(text('rpm_unit2', (1106, 721), 120, cell('k_small'), 'x1000', 'k_small', 'fg', 'center'))
# the bottom row (clock, range, outside temperature), dim; BMW's own is covered
W += [
    {'id': 'strip_cover_l', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 660, 'w': 1380, 'h': 60, 'color': 'bg', 'stripRow': 'l'},
    {'id': 'strip_cover_r', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 1460, 'y': 660, 'w': 460, 'h': 60, 'color': 'bg', 'stripRow': 'r'},
    {'id': 'strip_time', 'type': 'text', 'z': 3, 'x': 144, 'y': 678, 'w': 124, 'h': 27, 'text': '{{time}}', 'font': 'k_small', 'color': 'dim', 'align': 'right', 'stripRow': 'l'},
    {'id': 'strip_ampm', 'type': 'text', 'z': 3, 'x': 274, 'y': 678, 'w': 35, 'h': 27, 'text': '{{ampmLc}}', 'font': 'k_small', 'color': 'dim', 'align': 'left', 'stripRow': 'l'},
    {'id': 'strip_range', 'type': 'text', 'z': 3, 'x': 874, 'y': 678, 'w': 116, 'h': 27, 'text': '{{range}}', 'font': 'k_small', 'color': 'dim', 'align': 'right', 'stripRow': 'l'},
    {'id': 'strip_range_u', 'type': 'text', 'z': 3, 'x': 996, 'y': 678, 'w': 36, 'h': 27, 'text': '{{u:distLc}}', 'font': 'k_small', 'color': 'dim', 'align': 'left', 'stripRow': 'l'},
    {'id': 'strip_out', 'type': 'text', 'z': 3, 'x': 1676, 'y': 678, 'w': 80, 'h': 27, 'text': '{{ambient}}', 'font': 'k_small', 'color': 'dim', 'align': 'right', 'stripRow': 'r'},
    {'id': 'strip_out_u', 'type': 'text', 'z': 3, 'x': 1762, 'y': 678, 'w': 27, 'h': 27, 'text': '{{u:temp}}', 'font': 'k_small', 'color': 'dim', 'align': 'left', 'stripRow': 'r'},
]

L = {'schemaVersion': 2, 'name': 'Concept', 'theme': 'concept', 'mapLive': True,
     '_about': "Concept cluster, generated by tools/gen_concept.py (edit that and regenerate), after a photo of BMW's Concept 8 Series cluster (apps/3.jpg, traced by tools/concept/measure.py): two curved gauges with a glossy blue line, a dark glass panel of three-pointed stars and an amber swoosh lit from 0 to the value (speed on the left, revs on the right), a little fuel gauge far left and coolant far right, the speed over a bar, the drive mode and the gear, and an empty middle: the photo's navigation picture is the Waze map here, an oval window that opens while 'Show Waze map inside the theme' is on. Black covers BMW's gauges. Widget reference: shared/hud.js header.",
     'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(L, f, indent=2, ensure_ascii=False)
    f.write('\n')
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import badge_spot; badge_spot.apply(OUT)
print('concept.json:', len(W), 'widgets')
