#!/bin/sh
# Baut die App aus quelle/ neu und legt die fertigen Dateien ins Hauptverzeichnis (wird von GitHub Pages veröffentlicht).
set -e
cd "$(dirname "$0")"
python3 build/build.py .
cp site/* ..
rm -rf site
echo "Fertig: App im Hauptverzeichnis aktualisiert."
