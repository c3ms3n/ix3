#!/usr/bin/env python3
"""Bake the HUD's bitmap font atlases from the TTFs in tools/fonts-src/ (Barlow, Michroma, Orbitron, DSEG7, Outfit).

    UV_CACHE_DIR=... uv run --no-project --with pillow python tools/bake_fonts.py [app_id ...]

Runs on the Mac only (needs Pillow). The car never rasterizes fonts: it blits
these pre-drawn glyphs (shared/hud_text.js). Each app has its own set (FONTS below); output per
font, in apps/<app_id>/hud/fonts/<name>.json: the metrics plus the atlas as
one alpha byte per pixel (coverage), base64 in "alpha". JSON because the kit's
build packs the app's data folders into hud.pack, which holds JSON only, and
because then the car needs no PNG decoder. Barlow is SIL OFL 1.1; the licence
ships in each app's NOTICE.

Metrics: every glyph cell is the same height, from the highest ink to the lowest
ink across the font's glyph set, so a widget's y is the top of its tallest
character. `ox` shifts a cell from the pen position (ink overhang), `advance`
moves the pen. Digits get one shared advance (tabular), so a changing number
doesn't shift sideways.
"""
import base64, json, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'fonts-src')
APPS = os.path.join(HERE, '..', 'apps')

UPPER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
DIGITS = '0123456789'
LOWER = 'abcdefghijklmnopqrstuvwxyz'
# HUD Widgets, fitted to the part of the 800x480 HUD the driver can see (485x278 from the Nov 5 2026 grid
# photo; 560x280 since Nov 9, the sizes stayed): hero 140 -> 96, big 42 -> 34, mid 30 -> 24; label and small stay, BMW's own "mph" is that size.
HUD_FONTS = [
    # name, file, px size, characters
    ('hero', 'BarlowSemiCondensed-SemiBold.ttf', 96, DIGITS + 'PRND-'),
    ('big', 'BarlowSemiCondensed-Medium.ttf', 34, DIGITS + ':.-° PRNDSM'),
    ('mid', 'BarlowSemiCondensed-Medium.ttf', 24, DIGITS + ':.-° ' + UPPER),
    ('label', 'Barlow-Medium.ttf', 15, UPPER + DIGITS + '/.:-°%>· '),
    ('small', 'Barlow-Medium.ttf', 13, UPPER + DIGITS + '/.:-°%>· '),
    # Retro: seven-segment digits (DSEG7 Classic, SIL OFL; the unlit 8s behind are the same font in "track")
    ('d7_hero', 'DSEG7Classic-Bold.ttf', 76, DIGITS + 'PRN-', 0, None, {'R': 'r', 'N': 'n'}),   # r and n: seven segments can't draw R or N
    ('d7_mid', 'DSEG7Classic-Bold.ttf', 26, DIGITS + '-.:'),
    # Vector: now playing (any printable ASCII: a song's text is folded to it, hud.js mediaText)
    ('np_title', 'BarlowSemiCondensed-SemiBold.ttf', 22, ''.join(chr(i) for i in range(32, 127))),
    ('np_small', 'Barlow-Medium.ttf', 16, ''.join(chr(i) for i in range(32, 127))),
]
# Cluster Themes, 1920x720 LCD. GT3: the race-dash look, Barlow Condensed.
CLUSTER_FONTS = [
    ('gear', 'BarlowCondensed-Bold.ttf', 330, DIGITS + 'PRND-'),
    ('big', 'BarlowCondensed-Bold.ttf', 124, DIGITS + '.:-'),   # 124: "20.3 PSI" fits a 280 px box beside the hood; ':' for a clock in a readout slot
    ('value', 'BarlowCondensed-Bold.ttf', 92, DIGITS + '.:- PRND°', 0, None, None, '°'),   # °: a readout slot showing a temperature (tucked: the cell keeps its height)
    ('small', 'BarlowCondensed-Bold.ttf', 50, DIGITS + '.:-° '),
    ('unit', 'BarlowCondensed-SemiBold.ttf', 34, UPPER + DIGITS + '/°%>·.: -'),
    ('head', 'BarlowCondensed-SemiBold.ttf', 24, UPPER + DIGITS + '/°%>·.: -'),
    ('scale', 'BarlowCondensed-SemiBold.ttf', 30, DIGITS),
    ('badge', 'BarlowCondensed-SemiBold.ttf', 30, UPPER + LOWER + DIGITS + ' -'),   # the model badge (shared/badges.js)
    # M: the wide squared numbers (Michroma, SIL OFL) and Barlow for the small print
    ('m_num', 'Orbitron[wght].ttf', 36, DIGITS, 0, 'Black', {'0': 'O'}),
    ('m_gear', 'Orbitron[wght].ttf', 125, 'PRNDSM-' + DIGITS, 3, 'Black', {'0': 'O'}),
    ('m_speed', 'Orbitron[wght].ttf', 78, DIGITS + '-', 3, 'Black', {'0': 'O'}),
    ('m_gl', 'Orbitron[wght].ttf', 25, DIGITS + '/.-', 0, 'Black', {'0': 'O'}),
    ('m_val', 'Barlow-Medium.ttf', 54, DIGITS + ':+-.'),
    ('m_mid', 'Orbitron[wght].ttf', 34, DIGITS + ':+-.', 0, 'Bold', {'0': 'O'}),
    ('m_tyre', 'Orbitron[wght].ttf', 25, DIGITS + '.-:', 0, 'Bold', {'0': 'O'}),   # ':' for M's map-view clock (fit)
    ('m_unit', 'Barlow-Medium.ttf', 30, LOWER + UPPER + '°/-.'),
    ('m_label', 'Orbitron[wght].ttf', 20, UPPER + DIGITS + ' -/%°', 0, 'Bold'),   # digits, / % °: the M readout slots' names and units
    ('m_tiny', 'Barlow-Medium.ttf', 26, LOWER + DIGITS + 'CF./ -°'),
    ('m_badge', 'Barlow-Medium.ttf', 26, UPPER + LOWER + DIGITS + ' -'),
    # Sport: BMW Live Cockpit style, the wide numbers in Michroma like BMW's own
    ('s_scale', 'Michroma-Regular.ttf', 27, DIGITS, 1),
    ('s_speed', 'Michroma-Regular.ttf', 74, DIGITS + '-', 3),
    ('s_hero', 'Michroma-Regular.ttf', 132, DIGITS + '-', 3),   # the big speed in the middle while no map shows (Nov 13 2026)
    ('s_gear', 'Michroma-Regular.ttf', 70, DIGITS + 'PRNDSM-', 3),
    ('s_val', 'Michroma-Regular.ttf', 26, DIGITS + ':+-.', 1),
    ('s_unit', 'Barlow-Medium.ttf', 24, LOWER + UPPER + DIGITS + '°/-. '),
    ('s_label', 'BarlowSemiCondensed-SemiBold.ttf', 30, UPPER + DIGITS + ' .'),
    # Classic: Barlow numbers for the analog dials and the lit display
    ('f_lab', 'BarlowSemiCondensed-SemiBold.ttf', 44, DIGITS, 0),
    ('f_lab2', 'BarlowSemiCondensed-SemiBold.ttf', 34, DIGITS, 0),
    ('f_big', 'BarlowSemiCondensed-SemiBold.ttf', 70, DIGITS + '-', 0),
    ('f_disp', 'BarlowCondensed-SemiBold.ttf', 40, DIGITS + ':+-.°' + LOWER + UPPER + ' ', 0),
    ('f_small', 'Barlow-Medium.ttf', 26, UPPER + LOWER + DIGITS + '/ .%°+-:', 0),
    ('f_gear', 'BarlowCondensed-SemiBold.ttf', 56, 'PRNDSM' + DIGITS + '-', 0),
    # E46: the bold humanist numerals of the white-faced cluster (Barlow Condensed / Semi Condensed)
    ('w_red', 'BarlowCondensed-SemiBold.ttf', 24, DIGITS, 0),
    ('w_blk', 'Barlow-Medium.ttf', 19, DIGITS, 0),
    ('w_blk3', 'Barlow-Medium.ttf', 24, DIGITS, 0),
    ('w_blk2', 'BarlowSemiCondensed-SemiBold.ttf', 36, DIGITS + 'V8:+-.°', 0),
    ('w_logo', 'BarlowCondensed-Bold.ttf', 34, UPPER + DIGITS + ' ', 0),
    ('w_small', 'Barlow-Medium.ttf', 15, UPPER + LOWER + DIGITS + '/ .%-°', 0),
    ('w_lcd', 'DSEG7Classic-Bold.ttf', 34, DIGITS + ' -.:', 0),
    # Glass: the clean sans-serif numerals of the glass-dial cluster (Barlow)
    ('h_lab', 'BarlowSemiCondensed-SemiBold.ttf', 42, DIGITS, 0),
    ('h_sm', 'Barlow-Medium.ttf', 22, UPPER + LOWER + DIGITS + '/ .%°+-:', 0),
    ('h_val', 'Barlow-Medium.ttf', 28, UPPER + LOWER + DIGITS + '/ .%°+-:', 0),
    ('h_row', 'Barlow-Medium.ttf', 22, UPPER + LOWER + DIGITS + '/ .%°+-: ', 0),
    # Neon City: Orbitron Black for the big numbers, Orbitron Bold for the rest
    ('q_big', 'Orbitron[wght].ttf', 150, DIGITS + '-', 0, 'Black', {'0': 'O'}),
    ('q_mid', 'Orbitron[wght].ttf', 66, 'PRNDSM' + DIGITS + '-', 0, 'Black', {'0': 'O'}),
    ('q_txt', 'Orbitron[wght].ttf', 27, UPPER + DIGITS + ' :.+-/%°', 0, 'Bold', {'0': 'O'}),
    # Digital Rain: seven-segment digits for the big numbers, Orbitron for the terminal lines
    ('r_big', 'DSEG7Classic-Bold.ttf', 150, DIGITS + '-', 0),
    ('r_mid', 'DSEG7Classic-Bold.ttf', 70, DIGITS + ':.-', 0),
    ('r_txt', 'Orbitron[wght].ttf', 27, UPPER + DIGITS + ' :.+-/%°', 0, 'Bold', {'0': 'O'}),
    # ePower (the plug-in hybrid cluster): thin grey-white numerals
    ('p_lab', 'BarlowSemiCondensed-Medium.ttf', 40, DIGITS, 0),
    ('p_big', 'BarlowSemiCondensed-Medium.ttf', 52, DIGITS + '-', 0),
    ('p_unit', 'Barlow-Medium.ttf', 24, UPPER + LOWER + DIGITS + '/ .%°+-:', 0),
    ('p_row', 'BarlowSemiCondensed-SemiBold.ttf', 34, UPPER + LOWER + DIGITS + '/ .%°+-:', 0),
    ('p_gear', 'BarlowCondensed-SemiBold.ttf', 56, 'PRNDSM' + DIGITS + '-', 0),
    # Blue dials (the G30-style cluster): white numerals and the centre readouts (Barlow)
    ('g_lab', 'BarlowSemiCondensed-SemiBold.ttf', 40, DIGITS, 0),
    ('g_big', 'BarlowSemiCondensed-SemiBold.ttf', 78, DIGITS + '-', 0),
    ('g_gear', 'BarlowCondensed-SemiBold.ttf', 52, 'PRNDSM' + DIGITS + '-', 0),
    ('g_unit', 'Barlow-Medium.ttf', 28, UPPER + LOWER + DIGITS + '/ .%°+-:', 0),
    ('g_small', 'Barlow-Medium.ttf', 22, UPPER + LOWER + DIGITS + '/ .%°+-:', 0),
    # M Digital: wide squared numerals (Orbitron) for the big speed, the gear, the rev numbers
    ('z_big', 'Orbitron[wght].ttf', 114, '0123456789-', 0, 'Bold', {'0': 'O'}),
    ('z_gear', 'Orbitron[wght].ttf', 118, 'PRNDSM0123456789-', 0, 'Bold', {'0': 'O'}),
    ('z_num', 'Orbitron[wght].ttf', 34, '0123456789', 0, 'Bold', {'0': 'O'}),
    ('z_unit', 'Orbitron[wght].ttf', 28, UPPER + DIGITS + '/ .', 0, 'Bold'),
    ('z_small', 'Barlow-Medium.ttf', 28, UPPER + LOWER + DIGITS + '/ .%°+-:', 0),
    # Night: a slim clock for the middle
    ('n_time', 'Outfit[wght].ttf', 150, DIGITS + ':', 0, 'ExtraLight'),
    # Eco: slim Outfit numerals and labels (the i8-style dials)
    ('e_speed', 'Outfit[wght].ttf', 190, DIGITS + '-', 0, 'Light'),
    ('e_mid', 'Outfit[wght].ttf', 96, DIGITS + '-.%', 0, 'Light'),
    ('e_lab', 'Outfit[wght].ttf', 32, DIGITS, 0, 'Regular'),
    ('e_unit', 'Outfit[wght].ttf', 30, UPPER + LOWER + DIGITS + '/ .%°+-:', 0, 'Regular'),
    ('e_head', 'Outfit[wght].ttf', 24, UPPER + LOWER + DIGITS + '/ .%°+-:', 0, 'Medium'),
    ('e_clock', 'Outfit[wght].ttf', 46, DIGITS + ':+-.°', 0, 'Regular'),
    # Live Cockpit: the wide squared digits of the native render (Orbitron): scale numbers, the big speed and gear, the bottom row
    ('l_lab', 'Orbitron[wght].ttf', 30, '0123456789', 0, 'Bold', {'0': 'O'}, '', 0.9),
    ('l_big', 'Orbitron[wght].ttf', 151, '0123456789.', 0, 'Black', {'0': 'O'}, '', 0.88),
    ('l_mid', 'Orbitron[wght].ttf', 115, '0123456789.', 0, 'Black', {'0': 'O'}, '', 0.88),
    ('l_gear', 'Orbitron[wght].ttf', 82, 'PRNDSM0123456789-', 0, 'Black', {'0': 'O'}, '', 0.79),
    ('l_row', 'Orbitron[wght].ttf', 29, '0123456789:+-.PRNDSM', 0, 'Bold', {'0': 'O'}),
    ('l_bar', 'Orbitron[wght].ttf', 24, '0123456789', 0, 'Bold', {'0': 'O'}),
    ('l_unit', 'Barlow-Medium.ttf', 24, UPPER + LOWER + DIGITS + '/ .°-+', 0),
    # Concept: Outfit, thin and calm like BMW's Concept cluster: the big speed and gear, the scale numbers, the units
    ('k_speed', 'Outfit[wght].ttf', 110, DIGITS + '-', 1, 'Regular', None, '', 0.74),
    ('k_gear', 'Outfit[wght].ttf', 110, 'PRNDSM' + DIGITS + '-', 1, 'Regular', None, '', 0.74),
    ('k_num', 'Barlow-Medium.ttf', 37, DIGITS, 0),
    ('k_unit', 'Barlow-Medium.ttf', 30, UPPER + LOWER + DIGITS + '/ .', 1),
    ('k_small', 'Outfit[wght].ttf', 24, UPPER + LOWER + DIGITS + '/ .:+-', 0, 'Regular'),
    # Alpina: BMW-like numbers (Barlow Semi Condensed), the big speed and gear, the small units
    ('a_num', 'BarlowSemiCondensed-SemiBold.ttf', 40, DIGITS + '-', 1),
    ('a_unit', 'BarlowSemiCondensed-SemiBold.ttf', 28, LOWER + UPPER + DIGITS + '/ .°-+', 0),
    ('a_val', 'BarlowSemiCondensed-SemiBold.ttf', 30, DIGITS + ':+-.° ' + LOWER + UPPER, 0),
    ('a_big', 'BarlowSemiCondensed-SemiBold.ttf', 112, DIGITS + 'PRNDSM-', 3),
    ('s_gl', 'Michroma-Regular.ttf', 21, DIGITS + '/', 1),
    # Vector: the music panel's song title and artist (any printable ASCII: a song's text is folded to it, hud.js
    # mediaText), the ring gauges' numbers and labels, the track time
    ('v_title', 'BarlowSemiCondensed-SemiBold.ttf', 38, ''.join(chr(i) for i in range(32, 127))),
    ('v_artist', 'Barlow-Medium.ttf', 26, ''.join(chr(i) for i in range(32, 127))),
    ('v_val', 'Michroma-Regular.ttf', 22, DIGITS + '.-+', 1),
    ('v_label', 'BarlowSemiCondensed-SemiBold.ttf', 19, UPPER + LOWER + DIGITS + ' °%/.-'),
    ('v_time', 'Michroma-Regular.ttf', 16, DIGITS + ':-', 1),
    # Minimal: one huge speed, the gear, small print
    ('n_speed', 'BarlowSemiCondensed-Medium.ttf', 260, DIGITS + '-'),
    ('n_gear', 'BarlowSemiCondensed-SemiBold.ttf', 110, DIGITS + 'PRNDSM-'),
    ('n_unit', 'Barlow-Medium.ttf', 34, LOWER + UPPER + '/'),
    # Cruise and Minimal labels (r_label: the Roadster theme's, kept when Roadster was removed in 0.17.8)
    ('r_label', 'BarlowSemiCondensed-SemiBold.ttf', 24, UPPER + LOWER + DIGITS + '/°%.: -'),
    # Drag: the 0-60 clock
    ('timer', 'BarlowCondensed-Bold.ttf', 220, DIGITS + '.-'),
    # Rally: the huge gear and the readouts in the arc
    ('y_gear', 'BarlowCondensed-Bold.ttf', 300, DIGITS + 'PRNDSM-'),
    ('y_val', 'BarlowCondensed-Bold.ttf', 76, DIGITS + '.:-+°', 0, None, None, '°'),
    # Retro 80s: seven-segment digits (DSEG7 Classic, SIL OFL; the unlit 8s behind are the same font in "track")
    ('d7_big', 'DSEG7Classic-Bold.ttf', 170, DIGITS + '-'),
    ('d7_val', 'DSEG7Classic-Bold.ttf', 60, DIGITS + '-.:'),
    ('d7_sm', 'DSEG7Classic-Bold.ttf', 42, DIGITS + '-.:'),
    ('d7_gear', 'DSEG7Classic-Bold.ttf', 190, DIGITS + 'PRN-', 0, None, {'R': 'r', 'N': 'n'}),   # r and n: seven segments can't draw R or N
    # Cruise: calm, light numbers
    ('c_speed', 'BarlowSemiCondensed-Medium.ttf', 150, DIGITS + '-'),
    ('c_val', 'BarlowSemiCondensed-Medium.ttf', 62, DIGITS + '.:-+°'),
    # Ribbon: Outfit (SIL OFL), thin and calm: the huge speed, the side readouts, small spaced labels
    ('b_speed', 'Outfit[wght].ttf', 250, DIGITS + '-', 0, 'ExtraLight'),
    ('b_val', 'Outfit[wght].ttf', 44, DIGITS + '.:-+°% ' + LOWER + UPPER, 0, 'Light'),
    ('b_label', 'Outfit[wght].ttf', 20, UPPER + DIGITS + "' .-", 0, 'SemiBold'),
    ('b_unit', 'Outfit[wght].ttf', 26, UPPER + LOWER + '/', 0, 'Medium'),
    ('b_gear', 'Outfit[wght].ttf', 32, DIGITS + 'PRNDSM-', 0, 'SemiBold'),
    ('b_scale', 'Outfit[wght].ttf', 20, DIGITS, 0, 'Medium'),
]
FONTS = {'idrive_hud_widgets': HUD_FONTS, 'ix3_themes': CLUSTER_FONTS}
PAD = 2
ATLAS_W = 1024


def bake(out, name, file, size, chars, stroke=0, weight=None, subs=None, tuck='', xscale=1.0):
    """stroke: px of extra weight round every glyph (Michroma has one weight). weight: a named instance of a
    variable font (Orbitron: Regular .. Black), for the M theme's squared BMW-style gear, speed and numbers.
    subs: {char: glyph drawn for it} (Orbitron's zero is slashed; the M8's is plain, so its O stands in).
    tuck: characters added to a font after layouts were built on its cell height (° on value / y_val, Nov 7 2026):
    they don't count towards the cell, and one that rises above it is drawn lower so its top meets the cell's.
    xscale: every glyph squeezed (< 1) or widened sideways after drawing (the Concept theme's narrow numbers)."""
    font = ImageFont.truetype(os.path.join(SRC, file), size)
    if weight: font.set_variation_by_name(weight)
    subs = subs or {}
    glyph = lambda c: subs.get(c, c)
    ink = [c for c in chars if c != ' ']
    boxes = {c: font.getbbox(glyph(c), anchor='ls', stroke_width=stroke) for c in ink}
    top = min(b[1] for c, b in boxes.items() if c not in tuck)
    bottom = max(b[3] for c, b in boxes.items() if c not in tuck)
    drop = {c: max(0, top - boxes[c][1]) for c in tuck if c in boxes}
    height = bottom - top + 2 * PAD
    tab = (max(font.getlength(glyph(d)) for d in DIGITS if d in chars) + 2 * stroke) * xscale if any(d in chars for d in DIGITS) else 0

    cells = []
    for c in chars:
        adv = (font.getlength(glyph(c)) + (2 * stroke if c != ' ' else 0)) * xscale
        if c == ' ':
            cells.append((c, None, 0, round(adv if adv else size * 0.25)))
            continue
        l, _, r, _ = boxes[c]
        w = r - l + 2 * PAD
        img = Image.new('L', (w, height), 0)
        ImageDraw.Draw(img).text((PAD - l, PAD - top + drop.get(c, 0)), glyph(c), font=font, fill=255, anchor='ls', stroke_width=stroke, stroke_fill=255)
        if xscale != 1.0:
            img = img.resize((max(1, round(img.width * xscale)), height), Image.LANCZOS)
        shift = (tab - adv) / 2 if c in DIGITS else 0
        cells.append((c, img, round((l - PAD) * xscale + shift), round(tab if c in DIGITS else adv)))

    # simple row packing
    x = y = 0
    placed = {}
    for c, img, ox, adv in cells:
        if img is None:
            continue
        if x + img.width > ATLAS_W:
            x, y = 0, y + height
        placed[c] = (x, y)
        x += img.width
    atlas_h = y + height
    atlas = Image.new('L', (ATLAS_W, atlas_h), 0)
    glyphs = {}
    for c, img, ox, adv in cells:
        if img is None:
            glyphs[c] = {'x': 0, 'y': 0, 'w': 0, 'h': 0, 'ox': 0, 'advance': adv}
            continue
        gx, gy = placed[c]
        atlas.paste(img, (gx, gy))
        glyphs[c] = {'x': gx, 'y': gy, 'w': img.width, 'h': img.height, 'ox': ox, 'advance': adv}
    meta = {'source': file, 'size': size, 'cellHeight': height, 'baseline': PAD - top, 'glyphs': glyphs,
            'width': ATLAS_W, 'height': atlas_h, 'alpha': base64.b64encode(atlas.tobytes()).decode('ascii')}
    with open(os.path.join(out, name + '.json'), 'w') as f:
        json.dump(meta, f, separators=(',', ':'), ensure_ascii=False)
    print('%-6s %3dpx  cell height %3d  atlas %dx%d  %d glyphs' % (name, size, height, ATLAS_W, atlas_h, len(glyphs)))


if __name__ == '__main__':
    import sys
    for app in sys.argv[1:] or sorted(FONTS):
        out = os.path.join(APPS, app, 'hud', 'fonts')
        os.makedirs(out, exist_ok=True)
        print(app)
        for spec in FONTS[app]:
            bake(out, *spec)
