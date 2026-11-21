<p align="center"><img src="apps/kurdbimmer_themes/icon.png" width="120" alt="KurdBimmer icon"></p>

<h1 align="center">KurdBimmer Themes</h1>

<p align="center">
Seventeen full-screen instrument cluster themes for BMW iDrive 7 (MGU), with a Kurdish (Sorani) interface.<br>
Made by <a href="https://github.com/FDX100">FDX100</a>.
</p>

> **Every theme and feature here is tested on a BMW G20 with iDrive 7 (ID7)**, by the author, on his own car. Other models with an iDrive 7 head unit should work the same way, but they are not tested. Install at your own risk, as with any non-BMW app on a head unit.

## This fork (BMW iX3)

A fork of [FDX100/KB](https://github.com/FDX100/KB) for a BMW iX3 (iDrive 7). Themes with a big one-off shader (Alpina, Concept, Live Cockpit) restarted the iX3's head unit, so they are being cut down here one by one; Apex runs.

- **Concept** now draws each gauge as three small shader layers (the line with the swoosh, the glass panel, the little fuel / coolant gauge) instead of one big one: at most 53 uniform vectors in a shader, not 118. It looks the same on the bench (largest pixel difference 19 of 255); only the car shows whether the iX3 takes it.
- **Concept: match the ambient light colour** (Settings tab, off by default): the gauges' blues take the colour of the car's ambient light, read now and then from the body controller (read-only requests). The amber swoosh stays amber.

## What you get

- **17 cluster themes**, each drawn for the full 1920x720 cluster (see below).
- **Waze on the cluster:** with "Show Waze map inside the theme" on, themes that have a map window open it in the middle. Without Waze the middle stays as the theme drew it.
- **Drive-mode switching:** pick a different theme for Comfort, Sport and Eco Pro.
- **Readouts, badge, G-meter, alerts, shift lights and units** to set from the app's page on the center screen.
- **A Kurdish (Sorani) interface:** About tab, Language. Right-to-left, with joined Arabic letters and Arabic-Indic digits. The cluster itself stays in English.
- **Kurdish-flag look** for the app's pages (green, gold, red), with a picture of every theme.

## Themes

<table>
<tr><td align="center" width="50%"><img src="docs/themes/apex.png" width="440" alt="Apex"><br><b>Apex</b><br>Twin dials, a huge gear and a shift strip between them.</td><td align="center" width="50%"><img src="docs/themes/alpina.png" width="440" alt="Alpina"><br><b>Alpina</b><br>Chevron scales with light blue hatched bands, blue glass panels, the ALPINA wordmark.</td></tr>
<tr><td align="center" width="50%"><img src="docs/themes/concept.png" width="440" alt="Concept"><br><b>Concept</b><br>Curved glossy gauges with an amber swoosh; Waze oval in the middle.</td><td align="center" width="50%"><img src="docs/themes/live.png" width="440" alt="Live Cockpit"><br><b>Live Cockpit</b><br>Blue speed chevron, red rev chevron, fuel and oil bars.</td></tr>
<tr><td align="center" width="50%"><img src="docs/themes/eco.png" width="440" alt="Eco"><br><b>Eco</b><br>Speed and power rings with a green efficiency window over a glowing floor.</td><td align="center" width="50%"><img src="docs/themes/classic.png" width="440" alt="Classic"><br><b>Classic</b><br>Analog dials with red-orange ticks, small fuel and temperature dials, a lit middle window.</td></tr>
<tr><td align="center" width="50%"><img src="docs/themes/classic_map.png" width="440" alt="Classic Map"><br><b>Classic Map</b><br>Classic with smaller dials and a big window for the Waze map.</td><td align="center" width="50%"><img src="docs/themes/night.png" width="440" alt="Night Drive"><br><b>Night Drive</b><br>Very dark and quiet: slim bronze dials and a large clock.</td></tr>
<tr><td align="center" width="50%"><img src="docs/themes/mdigital.png" width="440" alt="M Digital"><br><b>M Digital</b><br>Tall curved rev bands, big speed and gear, the M stripe.</td><td align="center" width="50%"><img src="docs/themes/bluedials.png" width="440" alt="Blue Dials"><br><b>Blue Dials</b><br>Vivid blue round dials with tapered red needles and a road floor.</td></tr>
<tr><td align="center" width="50%"><img src="docs/themes/epower.png" width="440" alt="ePower"><br><b>ePower</b><br>Plug-in hybrid dials: speed, POWER % with a CHARGE sector, fuel and battery.</td><td align="center" width="50%"><img src="docs/themes/rain.png" width="440" alt="Digital Rain"><br><b>Digital Rain</b><br>Matrix-style falling glyphs behind seven-segment speed.</td></tr>
<tr><td align="center" width="50%"><img src="docs/themes/neon.png" width="440" alt="Neon City"><br><b>Neon City</b><br>Cyberpunk skyline, neon frames, huge yellow speed.</td><td align="center" width="50%"><img src="docs/themes/glass.png" width="440" alt="Glass"><br><b>Glass</b><br>Two big glass-ring dials, the middle left clear for Waze.</td></tr>
<tr><td align="center" width="50%"><img src="docs/themes/e46.png" width="440" alt="E46 M3"><br><b>E46 M3</b><br>White-faced analog cluster with chrome bezels and an orange LCD.</td><td align="center" width="50%"><img src="docs/themes/hybrid.png" width="440" alt="Hybrid"><br><b>Hybrid</b><br>One big speed with the battery charge line.</td></tr>
<tr><td align="center" width="50%"><img src="docs/themes/luxe.png" width="440" alt="Luxe"><br><b>Luxe</b><br>Classic and luxurious e-drive: gold-bezel dials, a POWER dial with a CHARGE sector, an analog clock, and a charging view with kW, battery and time to full.</td></tr>
</table>

Pictures are bench screenshots of the cluster area, not photos from a car.

## Install

You need a BMW iDrive 7 head unit with the [MGU Store](https://github.com/robertnisipeanu/mgu-store) and the **cluster-render** app (from [robertnisipeanu/idrive-apps](https://github.com/robertnisipeanu/idrive-apps)). Every theme draws through cluster-render, so install it first.

### From GitHub (online)

1. In the MGU Store open **Settings → Add source** and type **`FDX100/KB`** (or the link `https://github.com/FDX100/KB`). When it asks what to follow, pick the **main** branch.
2. Install **cluster-render** first if it is not on the car yet (from [robertnisipeanu/idrive-apps](https://github.com/robertnisipeanu/idrive-apps)).
3. Install **KurdBimmer Themes**. The Store builds it on the car from this repository (`mgu-repo.json`), and updates it when the version in `app.json` goes up.
4. Open **KurdBimmer Themes** from the apps menu on the center screen and pick a theme on the Themes tab.

### From a USB stick (offline)

On a computer with Node 18 or newer, using the Store's installer:

```sh
git clone https://github.com/robertnisipeanu/mgu-store
git clone https://github.com/FDX100/KB
cd mgu-store
node deploy/mgu-install.js usb-repo <stick> ../KB
# optional: put cluster-render on the same stick
node deploy/mgu-install.js usb-repo <stick> github:robertnisipeanu/idrive-apps
```

`<stick>` is the stick's mount point (`E:\` on Windows, `/run/media/<you>/USB` on Linux). In the car open **MGU Store, USB** and install cluster-render, then KurdBimmer Themes. Copying files onto the stick by hand does not work; the stick must be written by `usb-repo`.

## Using it

- **Look:** choose the theme, and optionally one per drive mode (Comfort, Sport, Eco Pro).
- **Hybrid and electric cars:** with "Change with the drive mode" on, the Themes tab also has **Hybrid** (engine running) and **Electric** (engine off) cells: pick a theme for each, or leave "Same" to follow the drive mode. The state comes from the engine speed, has to hold for 6 seconds, and the theme changes at most every 20 seconds, so a hybrid starting and stopping its engine in traffic does not keep redrawing the cluster. On a car without a hybrid system, leave both on Same.
- **Map:** turn on "Show Waze map inside the theme" and use Waze on Cluster (robertnisipeanu). Themes with a map window open it; the others ignore it.
- **Settings:** units, clock, fuel tank size, redline and shift point, shift lights, night colours, warnings.
- **Charging view** (Luxe): when the car is parked and the battery charge is rising, the middle shows CHARGING with the estimated kW, the battery bar and the time to full. It is worked out from the battery charge (the charger unit isn't read), so it appears a few minutes after you plug in, and the kW needs the right **Battery size** on the Settings tab.
- **Badges and logos:** every theme shows your model badge, as text or as your own logo PNG (see Badges and logos below).
- **Restart cluster** (Settings tab): drops the theme, resets the cluster's control unit the way BimmerCode does (UDS ECUReset to the KOMBI, address 0x60) and draws the theme again. Only while the car stands still; the cluster is dark for about 20 seconds.
- **About:** credits and the **Language** switch (English / Kurdish Sorani).

## Badges and logos

The **Badge** tab picks your model (1 Series to XM, i, Z4, ALPINA ...). Every theme has a place for the badge, in a spot that is free in that theme.

- **Text:** with nothing else set, the badge is the model's name in the theme's own font ("BMW" lettering optional).
- **Logo:** the app ships **no BMW, M, i or ALPINA artwork** (those are trademarks, and this repository is public), so the logos are your own PNG files. Put them in the app's data folder, `logos/`, and the badge shows the logo instead of the text, in every theme. The Badge tab shows which file it found.

File names, the first one that exists wins:

| File | Used for |
| --- | --- |
| `m340i.png`, `x3-m40i.png`, `i4-edrive40.png`, `b3.png` ... | that model (lower case, dashes) |
| `alpina.png` | ALPINA models |
| `i.png` | i4, i5, i7, iX and their M versions |
| `m.png` | M models and M Performance (M135i, M340i, X3 M40i, XM ...) |
| `bmw.png` | every other model |

Transparent PNG, any size up to 4096 px, 8 or 16 bit, not interlaced; it is scaled to fit the theme's spot. Put the files on the car over SSH:

```sh
./scripts/logos.sh root@<car-ip> bmw.png m.png i.png alpina.png
```

The app looks at the folder every few seconds, so no restart is needed. **Badge style** picks *Logo beside the text* (the default), *Logo only* or *Text only*; where a theme's spot is too narrow for both, the logo shows alone. `tools/logo_png.sh Mlogo.eps logos/m.png` turns an EPS (or PDF, SVG) you have into the PNG. On the bench, put the files in `bench/.data/kurdbimmer_themes/logos/`. The `logos/` folders are git-ignored, so the pictures are never committed. A theme made with `tools/gen_*.py` gets its badge from `tools/badge_spot.py` (one line in each generator): add a spot there for a new theme.

## Try it without a car

```sh
node bench/server.js kurdbimmer_themes     # then open http://localhost:8078
```

The bench draws the cluster and the center-screen page with simulated car data. Pick a theme on the Themes tab. Saving a layout or `shared/` file rebuilds and reloads it. See `bench/README.md`.

## Make your own theme

1. Write `tools/gen_<name>.py` (copy `tools/gen_apex.py`) that writes `apps/kurdbimmer_themes/hud/layouts/<name>.json`. The widget types are listed at the top of `shared/hud.js`.
2. Add a palette to `shared/hud_themes.js` (copy the `apex` entry).
3. Add `["<name>", "<Title>"]` to the four theme lists in `apps/kurdbimmer_themes/app.json` (`hudLayout`, `inComfort`, `inSport`, `inEco`), and a caption to `tags` in `apps/kurdbimmer_themes/main.js`.
4. Check it in the bench. The cluster draws at most 8 layers per connection; give widgets `"conn": 2` or `3` when a layout needs more.
5. Make its picture: `python3 tools/previews_kb.py kurdbimmer_themes 8078`.

More in `docs/DEVELOPING.md`.

## Kurdish (Sorani)

- `shared/ckb.js` shapes Arabic-script letters into their joined forms, puts a line in right-to-left order (Latin words and numbers keep their direction) and turns digits into Arabic-Indic ones.
- The letter forms come from Noto Sans Arabic (SIL OFL): `python3 tools/ckb/bake_arabic.py` bakes them into `kit/runtime/fonts/arabic*.json` and `shared/ckb_table.js`.
- Translations live in `tools/ckb/catalog.json` (English string to Sorani, `{n}` for a number). `python3 tools/ckb/make_catalog.py` writes `shared/ckb_catalog.js` and lists strings with no entry; those stay English.
- **The translation has not been reviewed by a native speaker.** Corrections to `catalog.json` are welcome.

## Build

```sh
python3 kit/tools/build.py kurdbimmer_themes     # writes dist/kurdbimmer_themes@<version>.mgu and .tgz
```

The build needs the BMW `oap-sdk`, which the Store makes on the car. In this repository `oap-sdk/` is a stub for the bench, so those files are for testing only; do not copy them to a car.

## Credits and licence

- Made by **FDX100**, https://github.com/FDX100.
- Built on [bimmer-lab/apps](https://github.com/bimmer-lab/apps) (Cluster Themes, MIT) and cauliflowermossgrape's [MGU App Kit](https://github.com/cauliflowermossgrape/idrive7-apps) (MIT). Every original bimmer-lab theme has been removed; only the themes made here remain.
- Cluster drawing by [cluster-render](https://github.com/robertnisipeanu/idrive-apps) and the [MGU Store](https://github.com/robertnisipeanu/mgu-store) by robertnisipeanu.
- Fonts: Barlow, Orbitron, Outfit and Noto Sans Arabic, all SIL OFL. See `apps/kurdbimmer_themes/NOTICE`.
- Some themes were drawn after photos of real clusters. They are original drawings, not BMW or Alpina artwork. BMW, M and Alpina are trademarks of their owners; this project is not affiliated with them.
- MIT licence, see `LICENSE`.
