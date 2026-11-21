#!/usr/bin/env bash
# Put your badge logo PNGs on the car (they are read by the Badge tab and every theme's badge spot), over SSH.
#
#   ./scripts/logos.sh root@<car-ip-or-hostname> logos/*.png
#   APP=ix3_themes ./scripts/logos.sh root@<car> bmw.png m.png i.png alpina.png m340i.png
#
# The app ships no BMW, M, i or ALPINA artwork (trademarks, and this repository is public): the pictures are yours. Transparent
# PNG, any size up to 4096 px, 8 or 16 bit, not interlaced. File names the app looks for, first that exists wins:
#   <model>.png     the model in lower case with dashes: m340i.png, x3-m40i.png, i4-edrive40.png, b3.png
#   alpina.png      ALPINA models           i.png    i4, i5, i7, iX      m.png    M models and M Performance      bmw.png   the rest
# With no file the badge is the model's name as text. The app looks again every few seconds: no restart needed.
# Delete a file on the car (<app>/data/logos/) to go back. UNVERIFIED until the first install, like deploy.sh: the app's folder
# is found on the car (OAP installs each app under /var/opt/public/oap/oap_<uid>/) and SSH access as root is assumed.
set -euo pipefail

APP_ID="${APP:-ix3_themes}"
OAP_ROOT="/var/opt/public/oap"

[ $# -ge 2 ] || { echo "Usage: $(basename "$0") <car-ssh-host> <logo.png> [more.png ...]" >&2; exit 1; }
CAR_HOST="$1"; shift

for f in "$@"; do
    [ -f "$f" ] || { echo "No such file: $f" >&2; exit 1; }
    case "$(basename "$f" | tr 'A-Z' 'a-z')" in *.png) ;; *) echo "Not a .png: $f" >&2; exit 1 ;; esac
    head -c 8 "$f" | od -An -tx1 | tr -d ' \n' | grep -q '^89504e470d0a1a0a$' || { echo "Not a PNG file: $f" >&2; exit 1; }
done

APP_DIR="$(ssh "$CAR_HOST" "grep -l '\"name\": \"${APP_ID}\"' ${OAP_ROOT}/oap_*/source/package.json 2>/dev/null | head -1 | sed 's#/source/package.json##'")"
[ -n "$APP_DIR" ] || { echo "Could not find ${APP_ID} under ${OAP_ROOT} on ${CAR_HOST}. Is the app installed?" >&2; exit 1; }
DEST="${APP_DIR}/data/logos"
echo "App folder on the car: ${APP_DIR}"

# the data folder belongs to the app's own user: the files are theirs too
OWNER="$(ssh "$CAR_HOST" "stat -c '%u:%g' '${APP_DIR}/data'")"
ssh "$CAR_HOST" "mkdir -p '${DEST}' && chown '${OWNER}' '${DEST}'"
for f in "$@"; do
    scp "$f" "${CAR_HOST}:${DEST}/$(basename "$f" | tr 'A-Z' 'a-z')"
done
ssh "$CAR_HOST" "chown '${OWNER}' '${DEST}'/*.png"
echo "Put $# logo file(s) in ${DEST}. Pick a model on the Badge tab; the logo shows within a few seconds."
