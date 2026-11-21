#!/usr/bin/env python3
"""Generates apps/ix3_themes/hud/layouts/glass.json (the Glass theme), after a render of a clean modern cluster (apps/10.jpg):
two big glass-ring dials on a dark navy ground (speed 0..270 km/h or 0..180 mph on the left, revs 0..9 on the right) with a thin
white outer ring, a steel-blue glass ring carrying the white ticks, a blue comet glow behind a thin blue needle with a white edge,
a red dashed band at the top of the rev scale, and a bright rounded level arc low on each face (fuel left, engine temperature
right); in the middle two bracket bars with the outside temperature, the clock, the drive mode and the range / trip along them, and the
middle itself left clear for Waze on Cluster: while the Waze map shows inside the theme a window opens there (no road is drawn). Positions come from the render (T() maps its 1000x562 px onto the 1920x660 layer). Edit this and regenerate."""
import json, math, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'layouts', 'glass.json')
FONT_DIR = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'fonts')
S = 1.17


def T(x, y):
    return ((x - 500.0) * S + 960.0, y * S)


def Tp(pts):
    return [T(*p) for p in pts]


def cell(font):
    return json.load(open(os.path.join(FONT_DIR, font + '.json')))['cellHeight']


def text(i, c, w, font, t, color='fg', align='center', **kw):
    h = cell(font)
    x0 = c[0] - w / 2 if align == 'center' else (c[0] - w if align == 'right' else c[0])
    d = {'id': i, 'type': 'text', 'z': 5, 'x': round(x0), 'y': round(c[1] - h / 2), 'w': w, 'h': h, 'text': t, 'font': font,
         'color': color, 'align': align}
    d.update(kw)
    return d


def pos(center, radius, deg):
    a = math.radians(deg)
    return (center[0] + radius * math.sin(a), center[1] - radius * math.cos(a))


def r1(pts):
    return [[round(x, 1), round(y, 1)] for x, y in pts]


K = 1.24                                         # the dials' size relative to the render (1.0 = as in the render)
LC, RC = (372.0, 346.0), (1548.0, 346.0)         # the dials' centres on the full-screen layout
DIAL = int(2 * (166 * S * K + 8))                # the layer's size (px): the outer ring's radius plus room
START, SWEEP = 226.5, 270.0


def dial(i, c, signal, mn, mx, majors, level, red=None, conn=1):
    return {'id': i, 'type': 'gdial', 'class': 'content', 'z': 2, 'x': round(c[0] - DIAL / 2), 'y': round(c[1] - DIAL / 2), 'w': DIAL, 'h': DIAL, 'conn': conn,
            'signal': signal, 'min': mn, 'max': mx, 'rings': [round(166 * S * K, 1), round(129 * S * K, 1), round(156 * S * K, 1), round(142 * S * K, 1)],
            'start': START, 'sweep': SWEEP, 'tail': 38.0, 'majors': majors, 'minors': 1, 'tickLen': [round(16 * S * K, 1), round(8 * S * K, 1)],
            'level': level, 'redBand': red, 'redDash': 6.0, 'needle': {'length': round(150 * S * K, 1), 'tail': round(26 * S * K, 1), 'width': 5.2 * K}, 'glow': [60, 120, 255]}


hide = {'toggle': '!mapUp'}
mx0, my0, mx1, my1 = 650.0, 140.0, 1270.0, 520.0     # the map window (layout px): between the big dials
W = [{'id': 'bg', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg',
      'hole': [round(mx0), round(my0), round(mx1 - mx0), round(my1 - my0)], 'holeWhen': 'mapUp', 'holeInset': 0, 'holeRadius': 18}]
W.append(dial('spd', LC, 'speed', 0, {'us': 180.0, 'metric': 270.0}, 9, {'radius': round(150 * S * K, 1), 'width': 9.0 * K, 'start': 212.0, 'sweep': -92.0,
              'signal': 'fuel', 'min': 0, 'max': 1}))
W.append(dial('rev', RC, 'rpm', 0, 9000, 9, {'radius': round(150 * S * K, 1), 'width': 9.0 * K, 'start': 216.0, 'sweep': -86.0, 'signal': 'coolant', 'min': 50, 'max': 130},
              red=[0.70, 0.995], conn=2))
# ---- the road in the middle (it gives way to the map window)
def poly(pts, top, bot, ta, ba, fade=0):
    pp = Tp(pts)
    ys = [p[1] for p in pp]
    return {'pts': r1(pp), 'top': round(min(ys), 1), 'bottom': round(max(ys), 1), 'topColor': top + [ta], 'bottomColor': bot + [ba], 'fade': fade}


road = [
    poly([(403, 225), (597, 225), (597, 231), (403, 231)], [200, 214, 244], [200, 214, 244], 0.9, 0.9, 38),
    poly([(403, 239), (597, 239), (597, 243), (403, 243)], [170, 186, 224], [170, 186, 224], 0.75, 0.75, 38),
    poly([(409, 249), (591, 249), (591, 263), (409, 263)], [105, 122, 166], [105, 122, 166], 0.8, 0.8, 46),
    poly([(430, 363), (481, 205), (498, 205), (490, 363)], [44, 54, 98], [124, 140, 186], 0.55, 0.9),
    poly([(490, 363), (496, 266), (509, 266), (514, 363)], [4, 7, 22], [4, 7, 22], 0.95, 0.95),
    poly([(514, 363), (509, 205), (528, 205), (572, 363)], [44, 54, 98], [124, 140, 186], 0.55, 0.9),
    poly([(527, 301), (551, 326), (519, 328)], [64, 196, 255], [64, 196, 255], 1.0, 1.0),
]
route = [{'seg': [*T(527, 182), *T(528, 295)], 'color': [236, 240, 250], 'half': 1.6}, {'seg': [*T(528, 295), *T(543, 368)], 'color': [236, 240, 250], 'half': 1.6},
         {'seg': [*T(521, 186), *T(517, 220)], 'color': [150, 165, 210], 'half': 1.0}]
# ---- the brackets along the top and the bottom (always)
BR = (440, 118, 560, 136)
brackets = []
WID = -10.0                                      # the brackets are this much wider on each side (render px; negative: narrower)
for a, b in (((330 - WID, 118), (368 - WID, 135)), ((368 - WID, 135), (632 + WID, 135)), ((632 + WID, 135), (670 + WID, 118)),
             ((334 - WID, 444), (372 - WID, 423)), ((372 - WID, 423), (628 + WID, 423)), ((628 + WID, 423), (666 + WID, 444)),
             ((402 - WID, 409), (598 + WID, 409))):
    brackets.append({'seg': [*T(*a), *T(*b)], 'color': [220, 232, 250] if a[1] != 409 else [60, 120, 150], 'half': 1.3})
W.append({'id': 'brackets', 'type': 'gpoly', 'class': 'content', 'z': 1, 'x': 640, 'y': 0, 'w': 640, 'h': 660, 'polys': [
    poly([(405 - WID, 410), (595 + WID, 410), (595 + WID, 423), (405 - WID, 423)], [18, 62, 74], [30, 96, 110], 0.55, 0.85, 60)], 'lines': brackets, 'conn': 3})
# ---- the numbers on the dials
LAB = 106 * S * K
for v in range(0, 271, 30):
    W.append(text('kmh%d' % v, pos(LC, LAB, START + v), 70, 'h_lab', str(v), 'fg', 'center', toggle='!units=us'))
for v in range(0, 181, 20):
    W.append(text('mph%d' % v, pos(LC, LAB, START + v * 270.0 / 180.0 * 1.0), 70, 'h_lab', str(v), 'fg', 'center', toggle='units=us'))
for v in range(0, 10):
    W.append(text('rpm%d' % v, pos(RC, LAB, START + v * 30.0), 50, 'h_lab', str(v), 'fg', 'center'))
def DP(c, dx, dy):
    """A point at the render's offset (dx, dy) from a dial's centre, scaled with the dial."""
    return (c[0] + dx * S * K, c[1] + dy * S * K)


W.append(text('speed_u', DP(LC, 4, -71), 120, 'h_sm', '{{u:speedLc}}', 'dim', 'center'))
W.append(text('rpm_u', DP(RC, -7, -71), 160, 'h_sm', 'rpm x1000', 'dim', 'center'))
W.append(text('fuel_v', DP(LC, 6, 112), 150, 'h_val', '{{range}}{{u:distLc}}', 'fg', 'left'))
W.append({'id': 'fuel_icon', 'type': 'icon', 'icon': 'fuel', 'z': 5, 'x': round(DP(LC, -24, 112)[0]) - 12, 'y': round(DP(LC, 0, 112)[1]) - 13, 'w': 24, 'h': 26, 'color': 'dim'})
W.append(text('temp_v', DP(RC, -14, 110), 130, 'h_val', '{{coolant}}{{u:temp}}', 'fg', 'left'))
W.append({'id': 'temp_icon', 'type': 'icon', 'icon': 'therm', 'z': 5, 'x': round(DP(RC, -33, 110)[0]) - 12, 'y': round(DP(RC, 0, 110)[1]) - 13, 'w': 24, 'h': 26, 'color': 'dim'})
# ---- the middle: temperature and clock on top, the drive mode, the range and the trip below
W.append(text('ambient', T(385 - WID * 0.5, 120), 120, 'h_sm', '{{ambient}}{{u:temp}}', 'fg', 'center'))
W.append(text('clock', T(606 + WID * 0.5, 120), 120, 'h_val', '{{time}}', 'fg', 'center'))
W.append({'id': 'damper', 'type': 'icon', 'icon': 'shock', 'z': 5, 'x': round(T(466, 404)[0]) - 12, 'y': round(T(0, 404)[1]) - 11, 'w': 24, 'h': 22, 'color': 'amber', 'toggle': '!mapUp'})
W.append(text('mode', T(486, 404), 150, 'h_val', '{{mode}}', 'fg', 'left', **hide))
W.append(text('total_l', T(420 - WID * 0.5, 440), 90, 'h_sm', 'RANGE', 'dim', 'right'))
W.append(text('total', T(424 - WID * 0.5, 440), 150, 'h_val', '{{range}} {{u:distLc}}', 'fg', 'left'))
W.append(text('trip_l', T(558 + WID * 0.5, 440), 70, 'h_sm', 'TRIP', 'dim', 'right'))
W.append(text('trip', T(562 + WID * 0.5, 440), 150, 'h_val', '{{tripDist}} {{u:distLc}}', 'fg', 'left'))
W += [
    {'id': 'strip_cover_l', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 660, 'w': 1380, 'h': 60, 'color': 'bg', 'stripRow': 'l'},
    {'id': 'strip_cover_r', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 1460, 'y': 660, 'w': 460, 'h': 60, 'color': 'bg', 'stripRow': 'r'},
    text('strip_time', (268.0, 690.0), 130, 'h_row', '{{time}}', 'fg', 'right', stripRow='l'),
    text('strip_ampm', (278.0, 693.0), 50, 'h_sm', '{{ampmLc}}', 'dim', 'left', stripRow='l'),
    text('strip_out', (1745.0, 690.0), 100, 'h_row', '{{ambient}}', 'fg', 'right', stripRow='r'),
    text('strip_out_u', (1755.0, 693.0), 40, 'h_sm', '{{u:temp}}', 'dim', 'left', stripRow='r'),
]
L = {'schemaVersion': 2, 'name': 'Glass', 'theme': 'glass', 'packWaste': 3,
     '_about': "Glass cluster, generated by tools/gen_glass.py (edit that and regenerate), after a render of a clean modern cluster (apps/10.jpg): two big glass-ring dials on a dark navy ground (speed 0..270 km/h or 0..180 mph left, revs 0..9 right) with a thin white outer ring, a steel-blue glass ring carrying the white ticks, a blue comet glow behind a thin blue needle with a white edge, a red dashed band at the top of the rev scale and a bright rounded level arc low on each face (fuel left, engine temperature right); in the middle a lit highway with the route line and the blue position arrow between two bracket bars, with the outside temperature, the clock, the drive mode, the range and the trip along them. While the Waze map shows inside the theme the middle is a clear window for Waze on Cluster (no road is drawn). Black covers BMW's gauges. Widget reference: shared/hud.js header.",
     'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(L, f, indent=2, ensure_ascii=False)
    f.write('\n')
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import badge_spot; badge_spot.apply(OUT)
print('glass.json:', len(W), 'widgets')
