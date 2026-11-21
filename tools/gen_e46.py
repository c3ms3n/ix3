#!/usr/bin/env python3
"""Generates apps/ix3_themes/hud/layouts/e46.json (the E46 theme): the white-faced analog cluster of an E46 M3 GTR (apps/11.jpg),
laid out as in the photo: a big speedometer (red notched km/h scale 20..240, an inner black mph scale 10..150), a big tachometer
(0..8 with the orange and red zones, the M3 GTR badge, V8, 1/min x1000, a small oil gauge at the bottom), a fuel gauge on the left
and a coolant gauge on the right, the dark binnacle with the warning-light plate, the turn arrows, and the orange LCD with the odometer
and the trip. Positions are the photo's pixels (T() maps them onto the 1920x660 layer). Edit this and regenerate."""
import json, math, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'layouts', 'e46.json')
FONT_DIR = os.path.join(ROOT, 'apps', 'ix3_themes', 'hud', 'fonts')
S = 1.37


def T(x, y):
    return ((x - 600.0) * S + 960.0, (y - 575.0) * S + 12.0)


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


def pos(c, radius, deg):
    a = math.radians(deg)
    return (c[0] + radius * math.sin(a), c[1] - radius * math.cos(a))


SC, TC = (415.5, 766.0), (824.0, 766.0)           # the speedometer's and the tachometer's centres (photo px)
RED, ORG, RD = [226, 40, 30], [248, 150, 30], [214, 36, 34]
W = [{'id': 'bg', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 0, 'w': 1920, 'h': 660, 'color': 'bg'}]


def poly(pts, top, bot, ta, ba, fade=0):
    pp = Tp(pts)
    ys = [p[1] for p in pp]
    return {'pts': r1(pp), 'top': round(min(ys), 1), 'bottom': round(max(ys), 1), 'topColor': top + [ta], 'bottomColor': bot + [ba], 'fade': fade}


# ---- the binnacle and the plates (a dark body with the warning plate, the turn arrows and the cruise button)
body = poly([(6, 604), (70, 570), (1130, 570), (1194, 604), (1196, 1000), (1130, 1048), (70, 1048), (4, 1000)],
            [28, 28, 30], [12, 12, 14], 0.98, 0.98)
plate = poly([(538, 566), (698, 566), (698, 610), (538, 610)], [40, 40, 42], [26, 26, 28], 0.95, 0.95)
arrow_l = poly([(150, 700), (190, 676), (190, 692), (206, 692), (206, 708), (190, 708), (190, 724)], [58, 58, 60], [44, 44, 46], 0.9, 0.9)
arrow_r = poly([(1090, 700), (1050, 676), (1050, 692), (1034, 692), (1034, 708), (1050, 708), (1050, 724)], [58, 58, 60], [44, 44, 46], 0.9, 0.9)
cruise = poly([(583, 884), (650, 884), (650, 926), (583, 926)], [34, 34, 36], [22, 22, 24], 0.95, 0.95)
lcd_frame = poly([(470, 950), (760, 950), (760, 1040), (470, 1040)], [10, 10, 11], [10, 10, 11], 1.0, 1.0)
lcd = poly([(487, 962), (745, 962), (745, 1034), (487, 1034)], [255, 112, 48], [255, 84, 30], 1.0, 1.0)
W.append({'id': 'body', 'type': 'gpoly', 'class': 'content', 'z': 1, 'x': 0, 'y': 0, 'w': 1920, 'h': 660,
          'polys': [body, plate, arrow_l, arrow_r, cruise, lcd_frame, lcd], 'lines': [], 'conn': 3})


# ---- the two big dials
def wdial(i, c, signal, mn, mx, start, sweep, notch, inner=None, zones=None, band=11, dashes=False, cap=40.0, conn=1, line=None):
    cx, cy = T(*c)
    size = int(2 * (189 * S + 8))
    d = {'id': i, 'type': 'wdial', 'class': 'content', 'z': 2, 'x': round(cx - size / 2), 'y': round(cy - size / 2), 'w': size, 'h': size, 'conn': conn,
         'signal': signal, 'min': mn, 'max': mx, 'rings': [round(189 * S, 1), round(181 * S, 1), round(168 * S, 1), round(30 * S, 1)],
         'start': start, 'sweep': sweep, 'notch': [notch[0], notch[1], round(notch[2] * S, 1), notch[3]], 'needleLength': round(170 * S, 1), 'needleColor': [244, 54, 28],
         'band': round(band * S, 1), 'gap': 1.2, 'dashes': dashes, 'cap': cap, 'cut': round((933 - c[1]) * S, 1), 'chamfer': round(126 * S, 1), 'line': line}
    if inner:
        d['inner'] = dict(inner, radius=round(inner['radius'] * S, 1), majorLen=round(inner['majorLen'] * S, 1), minorLen=round(inner['minorLen'] * S, 1))
    if zones:
        d['zones'] = zones
    return d


W.append(wdial('spd', SC, 'speed', 0, 240, 210.6, 277.4, (12, 1, 28, 2.1), line=[11.4, 292.0],
               inner={'radius': 109, 'start': 220.5, 'sweep': 262.5, 'ticks': 15, 'minors': 1, 'majorLen': 11, 'minorLen': 6}, cap=35.0))
W.append(wdial('rev', TC, 'rpm', 0, 8000, 240.5, 226.0, (8, 1, 28, 2.1), line=[-2.0, 229.5],
               inner={'radius': 113, 'start': 250.0, 'sweep': 228.0, 'ticks': 0, 'minors': 0, 'majorLen': 0, 'minorLen': 0},
               zones=[{'from': 0.5, 'to': 0.7625, 'color': ORG}, {'from': 0.7625, 'to': 1.0, 'color': RD}], dashes=True, cap=45.0, conn=2, band=8.5))


# ---- the small gauges
def wgauge(i, pivot, face, arc, tick_angles, blocks, needle, pivot_r, conn=3, clip=922.0, acenter=None, hook=0):
    px, py = T(*pivot)
    size = 300
    d = {'id': i, 'type': 'wgauge', 'class': 'content', 'z': 2, 'x': round(px - size / 2), 'y': round(py - size / 2 - 20), 'w': size, 'h': size, 'conn': conn,
         'pivot': [round(px, 1), round(py, 1)], 'arc': {'radius': round(arc[0] * S, 1), 'half': 1.0, 'start': arc[1], 'sweep': arc[2], 'hook': round(hook * S, 1), **({'center': [round(v, 1) for v in T(*acenter)]} if acenter else {})},
         'ticks': {'angles': tick_angles, 'length': round(22 * S, 1), 'width': 2.0},
         'blocks': [dict(b, rin=round(b['rin'] * S, 1), rout=round(b['rout'] * S, 1)) for b in blocks],
         'needle': dict(needle, length=round(needle['length'] * S, 1)), 'pivotRadius': round(pivot_r * S, 1)}
    if face:
        fx, fy = T(*face[0])
        d['face'] = {'center': [round(fx, 1), round(fy, 1)], 'radius': round(face[1] * S, 1), 'clipY': round(T(0, clip)[1], 1), 'rim': 8.0}
    return d


W.append(wgauge('fuel_g', (101, 894), ((100, 872), 104), (87, 316, 93), [316, 338, 2, 25, 49],
                [{'from': 320, 'to': 334, 'rin': 91, 'rout': 117, 'color': [226, 28, 28]}],
                {'length': 112, 'from': 312, 'to': 417, 'signal': 'fuel', 'min': 0, 'max': 1}, 24))
W.append(wgauge('temp_g', (1135, 895), ((1137, 873), 104), (88, 316, 88), [343, 357, 12],
                [{'from': 314, 'to': 330, 'rin': 91, 'rout': 117, 'color': [36, 122, 192]}, {'from': 26, 'to': 42, 'rin': 91, 'rout': 117, 'color': [226, 28, 28]}],
                {'length': 108, 'from': 312, 'to': 408, 'signal': 'coolant', 'min': 50, 'max': 130}, 24, conn=3))
W.append(wgauge('oil_g', (821, 889), None, (168, 322, 76), [355, 7, 21],
                [{'from': 322, 'to': 346, 'rin': 160, 'rout': 168, 'color': [222, 54, 42]}],
                {'length': 77, 'from': 290, 'to': 430, 'signal': 'oil', 'min': 60, 'max': 150}, 22, conn=2, acenter=(821, 991), hook=12))

# ---- the numbers, placed where the photo has them (photo px, read off enlarged crops)
KMH = {20: (308, 852), 40: (286, 803), 60: (286, 750), 80: (304, 701), 100: (339, 665), 120: (387, 644), 140: (442, 641),
       160: (488, 665), 180: (519, 698), 200: (545, 745), 220: (543, 802), 240: (517, 847)}
for v, p in KMH.items():
    W.append(text('kmh%d' % v, T(*p), 60, 'w_red', str(v), 'redn', 'center'))
RPM = {1: (682, 769), 2: (701, 707), 3: (749, 657), 4: (814, 643), 5: (887, 658), 6: (933, 705), 7: (949, 768), 8: (934, 830)}
for v, p in RPM.items():
    W.append(text('rpm%d' % v, T(*p), 40, 'w_red', str(v), 'redn', 'center'))
MPH = {10: (344, 814), 20: (334, 790), 30: (334, 762), 40: (338, 740), 50: (352, 720), 60: (368, 702), 70: (396, 693), 80: (418, 688), 90: (444, 694),
       100: (466, 708), 110: (481, 726), 120: (493, 748), 130: (492, 773), 140: (490, 798), 150: (474, 820)}
for m, p in MPH.items():
    big = m in (10, 20, 30, 50, 70, 90, 110, 130, 150)
    W.append(text('mph%d' % m, T(*p), 40, 'w_blk' if not big else 'w_blk3', str(m), 'inkb', 'center'))
W.append(text('mph_u', T(355, 799), 50, 'w_small', 'MPH', 'inkb', 'center'))
W.append(text('kmh_u', T(535, 826), 60, 'w_small', 'km/h', 'inkb', 'center'))
W.append(text('nfs', T(417, 858), 160, 'w_small', 'NEED FOR SPEED', 'inkb', 'center'))
W.append(text('nfs2', T(424, 876), 200, 'w_small', 'MOST WANTED', 'inkb', 'center', spacing=2))
W.append(text('gtr', T(842, 693), 120, 'w_logo', 'M3 GTR', 'inkb', 'center'))
W.append({'id': 'mstripe', 'type': 'stripe', 'z': 5, 'x': round(T(764, 0)[0]), 'y': round(T(0, 686)[1]), 'w': 52, 'h': 16})
W.append(text('v8', T(748, 769), 70, 'w_blk2', 'V8', 'inkb', 'center'))
W.append(text('rpm_u1', T(893, 763), 70, 'w_small', '1/min', 'inkb', 'center'))
W.append(text('rpm_u2', T(893, 778), 70, 'w_small', 'x1000', 'inkb', 'center'))
W.append(text('ready', T(692, 807), 70, 'w_small', 'READY', 'dim', 'center'))
for v, p in ((0, (27, 802)), (15, (60, 782)), (30, (105, 773)), (45, (148, 782)), (60, (183, 805))):
    W.append(text('fl%d' % v, T(*p), 40, 'w_red', str(v), 'redn', 'center'))
W.append({'id': 'fuel_icon', 'type': 'icon', 'icon': 'fuel', 'z': 5, 'x': round(T(109, 0)[0]) - 12, 'y': round(T(0, 826)[1]) - 14, 'w': 24, 'h': 28, 'color': 'redn'})
W.append({'id': 'temp_icon', 'type': 'icon', 'icon': 'therm', 'z': 5, 'x': round(T(1131, 0)[0]) - 12, 'y': round(T(0, 826)[1]) - 14, 'w': 24, 'h': 28, 'color': 'redn'})
W.append({'id': 'plate_i1', 'type': 'icon', 'icon': 'stack', 'z': 5, 'x': round(T(560, 0)[0]) - 12, 'y': round(T(0, 588)[1]) - 11, 'w': 24, 'h': 22, 'color': 'dim'})
W.append({'id': 'plate_i2', 'type': 'icon', 'icon': 'cog', 'z': 5, 'x': round(T(618, 0)[0]) - 12, 'y': round(T(0, 588)[1]) - 11, 'w': 24, 'h': 22, 'color': 'dim'})
W.append({'id': 'plate_i3', 'type': 'icon', 'icon': 'oilcan', 'z': 5, 'x': round(T(674, 0)[0]) - 14, 'y': round(T(0, 588)[1]) - 10, 'w': 28, 'h': 20, 'color': 'dim'})
# ---- the orange LCD: the odometer (here the range), the trip and the dashes
W.append(text('lcd_odo', T(548, 982), 180, 'w_lcd', '{{range}}', 'lcdink', 'center'))
W.append(text('lcd_km', T(632, 986), 50, 'w_small', '{{u:distLc}}', 'lcdink', 'center'))
W.append(text('lcd_trip', T(695, 982), 140, 'w_lcd', '{{tripDist}}', 'lcdink', 'center'))
W.append(text('lcd_row2', T(642, 1018), 140, 'w_lcd', '-- -- --', 'lcdink', 'center'))
# the bottom row sits under the LCD (clock and outside temperature)
W += [
    {'id': 'strip_cover_l', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 0, 'y': 660, 'w': 1380, 'h': 60, 'color': 'bg', 'stripRow': 'l'},
    {'id': 'strip_cover_r', 'type': 'fill', 'class': 'content', 'z': 0, 'x': 1460, 'y': 660, 'w': 460, 'h': 60, 'color': 'bg', 'stripRow': 'r'},
    text('strip_time', (268.0, 690.0), 130, 'w_blk2', '{{time}}', 'fg', 'right', stripRow='l'),
    text('strip_ampm', (278.0, 693.0), 50, 'w_small', '{{ampmLc}}', 'dim', 'left', stripRow='l'),
    text('strip_out', (1745.0, 690.0), 100, 'w_blk2', '{{ambient}}', 'fg', 'right', stripRow='r'),
    text('strip_out_u', (1755.0, 693.0), 40, 'w_small', '{{u:temp}}', 'dim', 'left', stripRow='r'),
]
L = {'schemaVersion': 2, 'name': 'E46 M3', 'theme': 'e46', 'packWaste': 3,
     '_about': "E46 cluster, generated by tools/gen_e46.py (edit that and regenerate), after a photo of an E46 M3 GTR's white-faced analog cluster (apps/11.jpg): a big speedometer (red notched km/h scale 20..240, an inner black mph scale 10..150), a big tachometer (0..8 with the orange and red zones, the M3 GTR badge, V8, 1/min x1000 and a small oil gauge), a fuel gauge on the left and a coolant gauge on the right, the dark binnacle with the warning-light plate, the turn arrows, and the orange LCD with the range and the trip. No map window. Black covers BMW's gauges. Widget reference: shared/hud.js header.",
     'widgets': W}
with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(L, f, indent=2, ensure_ascii=False)
    f.write('\n')
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import badge_spot; badge_spot.apply(OUT)
print('e46.json:', len(W), 'widgets')
