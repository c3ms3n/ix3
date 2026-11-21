#!/usr/bin/env python3
"""Generates apps/ix3_themes/hud/layouts/mdigital.json (the M Digital theme), after a product image of an aftermarket digital
M cluster (apps/9, a 600 px image: the numbers and shapes are read off a 8x enlargement, so this is the same layout, not a
tracing): two tall curved rev bands (0..8) round a centre column with the big speed over a divider and the gear under it, the M
stripe on top, a rounded panel on each side (left: the driver-assist panel, which becomes the Waze map window while the map shows;
right: a trip list), a small fuel gauge far left and a small temperature gauge far right. Edit this and regenerate."""
import json, math, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'layouts', 'mdigital.json')
FONT_DIR = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'fonts')
S = 0.68                       # the enlarged crop's px -> layout px
AX = 680.0                     # the crop's mirror axis x
CY = 470.0                     # the crop's middle y


def T(x, y):
    return ((x - AX) * S + 960.0, (y - CY) * S + 330.0)


def Tp(pts):
    return [T(*p) for p in pts]


def r1(pts):
    return [[round(x, 1), round(y, 1)] for x, y in pts]


def cell(font):
    return json.load(open(os.path.join(FONT_DIR, font + '.json')))['cellHeight']


def text(i, c, w, font, t, color='fg', align='center', **kw):
    h = cell(font)
    x0 = c[0] - w / 2 if align == 'center' else (c[0] - w if align == 'right' else c[0])
    d = {'id': i, 'type': 'text', 'z': 5, 'x': round(x0), 'y': round(c[1] - h / 2), 'w': w, 'h': h, 'text': t, 'font': font,
         'color': color, 'align': align}
    d.update(kw)
    return d


def line(pts, color, half):
    return [{'seg': [round(v, 1) for v in (*pts[i], *pts[i + 1])], 'color': color, 'half': half} for i in range(len(pts) - 1)]


WHITE = [244, 246, 248]
GREY = [150, 150, 154]
# the left band's centre line (crop px), bottom to top, and the thin arc inside it
BAND = [(150, 848), (92, 760), (52, 640), (34, 520), (44, 410), (90, 290), (150, 190), (222, 98)]
INNER = [(190, 850), (135, 760), (100, 640), (84, 520), (92, 410), (125, 300), (175, 200), (232, 96)]
TOPB = [(355, 100), (378, 128), (430, 142), (680, 148), (930, 142), (982, 128), (1005, 100)]
BOTB = [(262, 850), (300, 832), (350, 826), (680, 826), (1010, 826), (1060, 832), (1098, 850)]
DIV_L, DIV_R = (250, 508), (1110, 508)
lines = []
lines += line(Tp(TOPB), WHITE, 1.8) + line(Tp(BOTB), WHITE, 1.8)
dl, dr = T(*DIV_L), T(*DIV_R)
lines += line([dl, (dl[0] + 70, dl[1])], WHITE, 2.2) + line([(dl[0] + 70, dl[1]), (dr[0] - 70, dr[1])], GREY, 1.6) + line([(dr[0] - 70, dr[1]), dr], WHITE, 2.2)

W = [{'id': 'bg', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg',
      'hole': [60, 130, 470, 400], 'holeWhen': 'mapUp', 'holeInset': 0, 'holeRadius': 56}]
# the side panels (dark rounded shapes)
W.append({'id': 'panel_l', 'type': 'apanel', 'class': 'content', 'z': 1, 'x': 40, 'y': 110, 'w': 510, 'h': 440, 'rect': [60, 130, 470, 400], 'radius': 60,
          'top': [20, 20, 22], 'bottom': [8, 8, 10], 'ribs': [0, 0, 1, 0.3], 'toggle': '!mapUp'})
W.append({'id': 'panel_r', 'type': 'apanel', 'class': 'content', 'z': 1, 'x': 1370, 'y': 110, 'w': 510, 'h': 440, 'rect': [1390, 130, 470, 400], 'radius': 60,
          'top': [20, 20, 22], 'bottom': [8, 8, 10], 'ribs': [0, 0, 1, 0.3]})
W.append({'id': 'bands', 'type': 'mband', 'class': 'content', 'z': 2, 'x': 0, 'y': 0, 'w': 1920, 'h': 660,
          'band': r1(Tp(BAND)), 'axis': 960.0, 'halfWidth': 17.0, 'inner': r1(Tp(INNER)), 'lines': lines, 'redFrom': 0.82, 'tickSpacing': 14.0, 'edge': 1.6,
          'orange': [255, 112, 40], 'fill': [118, 119, 124]})
# the rev numbers inside the bands: 8, 6, 4, 2, 0 (left and right)
for v, (cx, cy) in zip((8, 6, 4, 2, 0), ((262, 135), (215, 290), (150, 465), (190, 660), (262, 820))):
    xl, yl = T(cx, cy); xr = 1920 - xl
    W.append(text('rl%d' % v, (xl, yl), 40, 'z_num', str(v), 'fg', 'center'))
    W.append(text('rr%d' % v, (xr, yl), 40, 'z_num', str(v), 'fg', 'center'))
W.append(text('rpm_u', (1510.0, 570.0), 200, 'z_small', '1/min x1000', 'dim', 'left'))
# the centre column
sx, sy = T(655, 410)
W.append(text('speed', (sx, sy), 330, 'z_big', '{{speed}}', 'fg', 'center', spacing=4))
ux, uy = T(960, 458)
W.append(text('speed_u', (ux, uy), 120, 'z_unit', '{{u:speed}}', 'fg', 'left'))
gx, gy = T(662, 628)
W.append(text('gear', (gx, gy), 300, 'z_gear', '{{stage}}{{gearnum}}', 'fg', 'center', spacing=3))
mx, my = T(660, 242)
W.append({'id': 'mstripe', 'type': 'stripe', 'z': 5, 'x': round(mx - 70), 'y': round(my - 8), 'w': 70, 'h': 14})
W.append(text('mletter', (mx + 22, my), 40, 'z_unit', 'M', 'fg', 'left'))
# the left panel: the driver-assist words (the Waze map's window while the map shows)
W.append(text('mode', (320.0, 240.0), 300, 'z_small', '{{mode}}', 'dim', 'center', toggle='!mapUp'))
W.append(text('assist', (320.0, 190.0), 300, 'z_small', 'Adaptive cruise', 'fg', 'center', toggle='!mapUp'))
# the right panel: a trip list
for k, (lab, tok) in enumerate((('Range', '{{range}} {{u:distLc}}'), ('Avg', '{{avgSpeed}} {{u:speedLc}}'), ('Out', '{{ambient}}{{u:temp}}'))):
    W.append(text('tl%d' % k, (1470.0, 220.0 + 46 * k), 90, 'z_small', lab, 'fg', 'left'))
    W.append(text('tv%d' % k, (1830.0, 220.0 + 46 * k), 250, 'z_small', tok, 'fg', 'right'))
# the small gauges: fuel (far left) and engine temperature (far right)
W.append({'id': 'fuel_arc', 'type': 'arc', 'class': 'content', 'z': 3, 'x': 56, 'y': 380, 'w': 150, 'h': 150, 'signal': 'fuel', 'min': 0, 'max': 1, 'width': 7,
          'color': 'fg', 'start': 200.0, 'sweep': 140.0, 'conn': 2})
W.append({'id': 'temp_arc', 'type': 'arc', 'class': 'content', 'z': 3, 'x': 1714, 'y': 380, 'w': 150, 'h': 150, 'signal': 'coolant', 'min': 50, 'max': 130, 'width': 7,
          'color': 'fg', 'start': 160.0, 'sweep': -140.0, 'conn': 2})
W.append(text('fuel_1', (110.0, 392.0), 30, 'z_small', '1', 'fg', 'center'))
W.append(text('fuel_0', (190.0, 520.0), 30, 'z_small', '0', 'fg', 'center'))
W.append(text('temp_h', (1810.0, 392.0), 30, 'z_small', 'H', 'fg', 'center'))
W.append(text('temp_c', (1730.0, 520.0), 30, 'z_small', 'C', 'fg', 'center'))
# the bottom row
W += [
    {'id': 'strip_cover_l', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 660, 'w': 1380, 'h': 60, 'color': 'bg', 'stripRow': 'l'},
    {'id': 'strip_cover_r', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 1460, 'y': 660, 'w': 460, 'h': 60, 'color': 'bg', 'stripRow': 'r'},
    text('strip_time', (268.0, 690.0), 130, 'z_small', '{{time}}', 'fg', 'right', stripRow='l'),
    text('strip_ampm', (278.0, 693.0), 50, 'z_small', '{{ampmLc}}', 'dim', 'left', stripRow='l'),
    text('strip_range', (960.0, 690.0), 110, 'z_small', '{{range}}', 'fg', 'right', stripRow='l'),
    text('strip_range_u', (970.0, 693.0), 40, 'z_small', '{{u:distLc}}', 'dim', 'left', stripRow='l'),
    text('strip_out', (1745.0, 690.0), 100, 'z_small', '{{ambient}}', 'fg', 'right', stripRow='r'),
    text('strip_out_u', (1755.0, 693.0), 40, 'z_small', '{{u:temp}}', 'dim', 'left', stripRow='r'),
]
L = {'schemaVersion': 2, 'name': 'M Digital', 'theme': 'mdigital', 'packWaste': 3,
     '_about': "M Digital cluster, generated by tools/gen_mdigital.py (edit that and regenerate), after a product image of a digital M cluster (apps/9): two tall curved rev bands (0..8: orange edges, grey fill up to the revs, the top turning yellow then red from the redline) round a centre column with the big speed over a divider and the gear under it, the M stripe on top, a rounded panel on each side (left: the driver-assist words, which becomes the Waze map's window while 'Show Waze map inside the theme' is on; right: a trip list), a small fuel gauge far left and a small temperature gauge far right. Black covers BMW's gauges. Widget reference: shared/hud.js header.",
     'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(L, f, indent=2, ensure_ascii=False)
    f.write('\n')
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import badge_spot; badge_spot.apply(OUT)
print('mdigital.json:', len(W), 'widgets')
